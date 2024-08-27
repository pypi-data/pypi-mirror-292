#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import pickle
from unittest import TestCase

import numpy as np
import peewee
from numpy.testing import assert_allclose

from conformer.common import GHOST_ATOM
from conformer.db.models import (
    DBAtom,
    DBAtomToSystem,
    DBSystem,
    DBSystemLabel,
    DBUnitCell,
)
from conformer.systems import (
    Atom,
    NamedSystem,
    System,
    UniqueSystemSet,
    bound_COM_join,
    hash_Atom_v2,
    hash_System_v2,
    merge,
    subsystem_merge,
)
from tests.conformer import ConformerTestCase


class AtomTestCases(TestCase):
    def test_constructors(self):
        A1 = Atom("H", [0, 0, 0])
        self.assertEqual(A1.t, "H")
        assert_allclose(A1.r, np.array([0.0, 0.0, 0.0]))
        self.assertEqual(A1.charge, 0)
        self.assertDictEqual(A1.meta, {})

        A2 = Atom("H", [0, 0, 0], charge=2, meta={"a": 1})
        self.assertEqual(A2.t, "H")
        assert_allclose(A2.r, np.array([0.0, 0.0, 0.0]))
        self.assertEqual(A2.charge, 2)
        self.assertDictEqual(A2.meta, {"a": 1})

    def test_properties(self) -> None:
        C = Atom("C", np.array([0.0] * 3))
        self.assertEqual(C.electrons, 6)
        self.assertEqual(C.core_electrons, 2)
        self.assertEqual(C.valence_electrons, 4)
        self.assertEqual(C.max_valence, 8)
        self.assertAlmostEqual(C.mass, 12.0, 1)
        self.assertAlmostEqual(C.covalent_radius, 0.76, 2)
        self.assertAlmostEqual(C.vdw_radius, 1.7, 2)

        C13 = Atom("C13", np.array([0.0] * 3))
        self.assertAlmostEqual(C13.mass, 13.00, 2)

    def test_equality(self):
        self.assertEqual(Atom("H", [0, 0, 0]), Atom("H", [0, 0, 0]))
        self.assertNotEqual(Atom("H", [0, 0, 0], charge=1), Atom("H", [0, 0, 0]))
        self.assertNotEqual(Atom("H", [0, 0, 0], charge=1), Atom("H", [0, 0, 1]))

    def test_fingerprinting(self):
        HASH1 = "d08f2ab71a42c4bf25c93978931685c25b46b754"
        A = Atom("H", np.array([0.0, 0.0, 0.0]))
        self.assertEqual(hash_Atom_v2(A).hexdigest(), HASH1)

        # Check offset
        A = Atom("H", np.array([1.0, 1.0, 1.0]))
        self.assertEqual(
            hash_Atom_v2(A).hexdigest(), "92fae579e8776881137addb0e84ff56f611b342e"
        )
        # Offsetting should fix the hash difference
        self.assertEqual(
            hash_Atom_v2(A, np.array([-1.0, -1.0, -1.0])).hexdigest(), HASH1
        )

        # Check SMALL displacents
        A = Atom("H", np.array([0.0, 0.0, 0.0]) + 1e-7)
        self.assertEqual(
            hash_Atom_v2(A).hexdigest(), "65edc9ddca555d5671725d376fde7d25c48cc32e"
        )

        A = Atom("H", np.array([0.0, 0.0, 0.0]) + 1e-6)
        self.assertEqual(
            hash_Atom_v2(A).hexdigest(), "1aeb25336a72a7800657260c66138f24f990f725"
        )

        # Test Charges
        A = Atom("H", np.array([0.0, 0.0, 0.0]), charge=-2)
        self.assertEqual(
            hash_Atom_v2(A).hexdigest(), "46e0fd40dfdebbe7252dda98ff6933f63f3b65d0"
        )

        # Test Charges
        A = Atom("H", np.array([0.0, 0.0, 0.0]), meta=dict(a=2))
        self.assertEqual(
            hash_Atom_v2(A).hexdigest(), "57b598c77f2db26be49e6d47d8edccb22ecfe3bb"
        )

        # letters = "ABCDEFGHIJKLMPQRSTUVWXYZ"
        # from random import randint
        # np.random.random(3)
        # atoms = {}
        # for i in range(1000000):
        #     A = Atom(
        #         letters[randint(0, len(letters) - 1)],
        #         np.random.random(3) * 10,
        #         charge=randint(-3, 3)
        #     )

        #     try:
        #         A2 = atoms[A.hash()]
        #         print("GOT A HIT!!!")
        #         print(A, A2)
        #     except KeyError:
        #         atoms[A.hash()] = A

        #     # if randint(1, 100000) == 1:
        #     #     print(A, "-->", A.hash())

        # print(len(atoms))


class SystemTestCases(TestCase):
    def test_constructor(self):
        sys = System(
            [
                Atom("H", [0.0, 0.0, 0.0]),
                Atom("C13", [1.0, 0.0, 0.0], charge=1),
                Atom("H", [0.0, 1.0, 0.0]),
            ]
        )
        sys.update_atoms([2], role=GHOST_ATOM)
        self.assertEqual(sys.size, 3)
        self.assertAlmostEqual(sys.mass, 14.011, 3)
        self.assertEqual(sys.charge, 1)
        self.assertEqual(sys.multiplicity, 1)
        assert_allclose(
            sys.r_matrix, np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        )
        assert_allclose(sys.masses, np.array([[1.00782503], [13.00335484], [0.0]]))
        assert_allclose(sys.COM, np.array([0.92806994, 0.0, 0.0]))
        assert_allclose(sys.charges, np.array([[0], [1], [0]]))

        # Make sure the cache is clearing
        sys.add_atoms(Atom("N", [0.0, 0.0, 1.0]))
        assert_allclose(
            sys.r_matrix,
            np.array(
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
            ),
        )

        sys.add_atoms(Atom("N", [0.0, 1.0, 1.0]))
        assert_allclose(
            sys.r_matrix,
            np.array(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0],
                    [0.0, 1.0, 1.0],
                ]
            ),
        )

    def test_periodic(self):
        sys = System(
            [
                Atom("H", [0.0, 0.0, 0.0]),
            ],
            unit_cell=np.array([1, 1, 1]),
        )

        assert_allclose(sys.r_matrix, np.array([0.0, 0.0, 0.0]).reshape(-1, 3))

        sys.add_atoms(Atom("H", (0, 0, 0)), cell=(1, 1, 1))
        assert_allclose(sys.r_matrix, np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]))

        sys2 = sys.subsystem([0, 0, 0])
        sys2.update_atoms([1], cell=(1, 1, 1))
        sys2.update_atoms([2], cell=(2, 2, 2))
        assert_allclose(
            sys2.r_matrix, np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])
        )

        # TODO: Test with Mask objects

    def test_nuclear_repulsion_energy(self):
        sys = System.from_string(
            """
            O    -0.97050800 2.45433300 1.17418600
            H    -1.56837000 1.71485600 1.26315600
            H    -1.35946000 3.18574300 1.62501500
        """
        )
        self.assertAlmostEqual(sys.nuclear_repulsion_energy, 9.26729174)

    def test_shift_recenter(self):
        sys1 = System([Atom("H", [0.0, 0.0, 0.0])])

        # Test no shift
        delta = np.array([0, 0, 0])
        self.assertIs(sys1, sys1.shift(delta))
        self.assertIs(sys1, sys1.recenter(sys1[0].r))

        delta = np.array([1, 1, 1])
        self.assertIsNot(sys1, sys1.shift(delta))
        assert_allclose(sys1.shift(delta)[0].r, delta)
        assert_allclose(sys1.recenter(delta)[0].r, delta)

    def test_copy(self):
        sys1 = System(
            [
                Atom("H", [0.0, 0.0, 0.0]),
                Atom("C13", [1.0, 0.0, 0.0], charge=1),
            ]
        )
        sys2 = sys1.copy()

        self.assertEqual(sys1, sys2)
        sys2.update_atoms([1], role=GHOST_ATOM)
        self.assertNotEqual(sys1, sys2)

        # Check equality of bound atoms
        self.assertNotEqual(sys1[1], sys2[1])
        self.assertEqual(sys1[1]._atom, sys2[1])
        self.assertEqual(sys1[1], sys2[1]._atom)

    def test_subsystem(self):
        sys1 = System(
            [
                Atom("H", np.array([0.0, 0.0, 0.0])),
                Atom("H", np.array([0.0, 1.0, 0.0])),
            ]
        )

        # Check that we are not duplicating objects!
        sys2 = sys1.subsystem([1])
        self.assertEqual(sys1[1], sys2[0])
        self.assertIsNot(sys1[1], sys2[0])
        self.assertIs(sys1[1]._atom, sys2[0]._atom)

        # Test mods
        def mod1(supersys: System, _key, sys: System):
            sys.add_atoms(Atom("H", np.array([1.0, 1.0, 1.0])))
            return sys

        sys3 = sys1.subsystem([1], mods=[mod1])
        self.assertEqual(sys3.size, 2)
        self.assertEqual(sys3[1], Atom("H", np.array([1.0, 1.0, 1.0])))

    def test_merge(self):
        sys1 = System(
            [
                Atom("H", np.array([0.0, 0.0, 0.0])),
                Atom("H", np.array([0.0, 1.0, 0.0])),
            ]
        )

        sys2 = System(
            [
                Atom("H", np.array([0.0, 1.0, 0.0])),
                Atom("H", np.array([0.0, 0.0, 1.0])),
            ]
        )

        # Merge should deduplicate the system
        self.assertEqual(
            sys1.merge(sys2),
            System(
                [
                    Atom("H", np.array([0.0, 0.0, 0.0])),
                    Atom("H", np.array([0.0, 1.0, 0.0])),
                    Atom("H", np.array([0.0, 0.0, 1.0])),
                ]
            ),
        )

    def test_equality(self):
        sys1 = System.from_tuples(
            [
                ("O", 0.0000000, 0.0184041, 0.0000000),
                ("H", 0.0000000, -0.5383517, -0.7830365),
                ("H", 0.0000000, -0.5383517, 0.7830365),
            ]
        )
        sys2 = System.from_string(
            """
        H  0.0000000 -0.5383517  0.7830365
        H  0.0000000 -0.5383517 -0.7830365
        O  0.0000000  0.0184041  0.0000000
        """
        )

        sys3 = System.from_tuples([("C", 0, 0, 0)])

        # Test equality
        self.assertEqual(sys1, sys2)

        # Test inequality
        self.assertNotEqual(sys1, sys3)

        # Test type
        self.assertFalse(sys3.__eq__(None))

    def test_fingerprinting(self):
        sys = System.from_tuples(
            [
                ("O", 0.0000000, 0.0184041, 0.0000000),
                ("H", 0.0000000, -0.5383517, -0.7830365),
                ("H", 0.0000000, -0.5383517, 0.7830365),
            ]
        )

        HASH1 = "def6c63f08eebb0466d66c4fb8ce661db0d6fa48"
        self.assertEqual(sys.fingerprint, HASH1)
        self.assertEqual(
            hash_System_v2(sys, use_fast=True).hexdigest(),
            hash_System_v2(sys, use_fast=False).hexdigest(),
        )

        # Displace all atom positions
        # NOTE: This is not OK in production code. Atoms are imutable
        for a in sys:
            a._atom.r += np.array([1, 1, 1])
        sys._reset_cache()
        self.assertEqual(sys.fingerprint, HASH1)
        self.assertEqual(
            hash_System_v2(sys, use_fast=True).hexdigest(),
            hash_System_v2(sys, use_fast=False).hexdigest(),
        )

        # Change roles
        sys.update_atoms([0], role=GHOST_ATOM)
        self.assertEqual(sys.fingerprint, "b8f98b83fd1e008deb5c218e0dd7d29c8c910252")
        self.assertEqual(
            hash_System_v2(sys, use_fast=True).hexdigest(),
            hash_System_v2(sys, use_fast=False).hexdigest(),
        )

        # TEST PERIODIC SYSTEMMS
        # Test unit cell
        sys.unit_cell = np.array([3, 3, 3], dtype=np.float64)
        sys._reset_cache()
        self.assertEqual(sys.fingerprint, "2693c637f3ca7e9d79d6224e1615d1a86a82ae63")
        self.assertEqual(
            hash_System_v2(sys, use_fast=True).hexdigest(),
            hash_System_v2(sys, use_fast=False).hexdigest(),
        )

        # Test moving at atom within world
        sys.update_atoms([0], cell=(0, 0, 1))
        sys._reset_cache()
        self.assertEqual(sys.fingerprint, "af90b79ca29451cc569bfa254e2d138689dcd80f")
        self.assertEqual(
            hash_System_v2(sys, use_fast=True).hexdigest(),
            hash_System_v2(sys, use_fast=False).hexdigest(),
        )

        sys.add_atoms(Atom("H", [0, 0, 0], charge=-1))
        self.assertEqual(
            hash_System_v2(sys, use_fast=True).hexdigest(),
            hash_System_v2(sys, use_fast=False).hexdigest(),
        )

    def test_fingerprint_instability(self):
        """
        This test case is the direct result of a big in Atom Driver where
        it run fine on the supercomputer, a macbook pro, but failed (for caching)
        on GitLab

        UPDATE: This has started happening on a M3 MBP
        """
        sys = System.from_tuples([("H", 0, 0, 0), ("H", 0.92, 0, 0)])
        shifted_sys = sys.shift(np.array([1.0, 1.0, 1.0]))

        self.assertEqual(
            hash_System_v2(shifted_sys, use_fast=True).digest(),
            hash_System_v2(sys, use_fast=True).digest(),
        )

        # Shifted so not equal (True)
        self.assertNotEqual(sys, shifted_sys)
        # Should be translationally equal (True)
        self.assertTrue(sys.eq_TI(shifted_sys))
        # Fingerprints are different (This part was failing)
        self.assertEqual(sys.fingerprint, shifted_sys.fingerprint)

    def test_NamedSystem(self):
        sys = NamedSystem.from_tuples(
            [
                ("O", 0.0000000, 0.0184041, 0.0000000),
                ("H", 0.0000000, -0.5383517, -0.7830365),
                ("H", 0.0000000, -0.5383517, 0.7830365),
            ],
            name="Test System",
        )
        subsys = sys.subsystem([0, 1])

        self.assertIsInstance(sys, NamedSystem)
        self.assertListEqual(sys.meta["order"], [2, 0, 1])
        # Check strict subclassing. We don't want to propogaed the named systems
        #   for subclassing
        self.assertIs(type(subsys), System)


class SystemDBTestCases(ConformerTestCase):
    def test_atoms(self):
        """Test Atoms in the DB"""
        A1 = Atom("H", [1, 1, 1])
        A2 = Atom("C", [0, 0, 0], charge=1, meta={"group_number": 1})

        DBAtom.add_atoms([A1, A2, A1])
        self.assertEqual(DBAtom.select().count(), 2)
        atoms = DBAtom.get_atoms([A1._saved, A2._saved])

        for a in [A1, A2]:
            self.assertEqual(a, atoms[a._saved])

        # Check that we are deduplicating
        A1_new = Atom("H", [1, 1, 1])
        DBAtom.add_atoms([A1_new])
        self.assertEqual(A1_new._saved, 1)

    def test_systems(self):
        """Test Systems in the DB"""
        S1 = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("C", 1, 1, 1),
                ("C", 2, 2, 2),
            ]
        )

        S2 = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("C", 3, 3, 3),
            ]
        )
        # Save a different role
        S2.update_atoms([0], GHOST_ATOM)

        DBSystem.add_systems([S1, S2, S1])

        # Check system 1
        self.assertEqual(S1._saved, 1)
        self.assertEqual(S1[0]._saved, 1)
        self.assertEqual(S1[1]._saved, 2)
        self.assertEqual(S1[2]._saved, 3)

        # Check system 2
        self.assertEqual(S2._saved, 2)
        self.assertEqual(S2[0]._saved, 1)
        self.assertEqual(S2[1]._saved, 4)

        self.assertEqual(DBSystem.select().count(), 2)
        self.assertEqual(DBAtom.select().count(), 4)
        self.assertEqual(DBAtomToSystem.select().count(), 5)

        sys_db = DBSystem.get_systems([S1._saved, S2._saved])

        for s in [S1, S2]:
            self.assertEqual(s, sys_db[s._saved])

    def test_merge(self):
        """Merge combines all atoms in the provided systems."""
        S1 = System.from_tuples([("H", 0, 0, 1)])
        S2 = System.from_tuples([("H", 0, 0, 2)])
        self.assertEqual(
            merge(S1, S2), System.from_tuples([("H", 0, 0, 1), ("H", 0, 0, 2)])
        )

    def test_subsystem_union(self):
        """Subsystem union combines systems only including atoms which appear in
        common Supersystem.

        To include all atoms, use :meth:`merge`
        """
        ss = System.from_tuples([("H", 0, 0, 1), ("H", 0, 0, 2), ("H", 0, 0, 3)])
        S1 = ss.subsystem([0])
        S2 = ss.subsystem([1])
        S2.add_atoms(Atom("H", [0, 0, -1]))  # This will not be included in the union
        self.assertEqual(
            subsystem_merge(S1, S2),
            System.from_tuples([("H", 0, 0, 1), ("H", 0, 0, 2)]),
        )

    def test_periodic_systems(self):
        """TODO: Implement this"""
        S1 = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("C", 1, 1, 1),
                ("C", 2, 2, 2),
            ]
        )
        S1.unit_cell = np.array([3, 3, 3], dtype=np.float64)
        S2 = S1.subsystem([0, 1])

        # Same system, but different unit cell
        S3 = S1.copy()
        S3.unit_cell = np.array([4, 4, 4], dtype=np.float64)

        # Same system, but not periodic
        S4 = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("C", 1, 1, 1),
                ("C", 2, 2, 2),
            ]
        )

        DBSystem.add_systems([S1, S2, S3, S4])
        self.assertEqual(DBUnitCell.select().count(), 2)

        # Verify we are not duplicating unit cells
        DBSystem.add_systems([S1.subsystem([2])])
        self.assertEqual(DBUnitCell.select().count(), 2)

        # Check getting systems
        systems = [S1, S2, S3, S4]
        ids = [S1._saved, S2._saved, S3._saved, S4._saved]
        db_systems = DBSystem.get_systems(ids)
        for i, s in zip(ids, systems):
            self.assertEqual(s, db_systems[i])

    def test_system_querying(self):
        S = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("H", 1, 0, 0),
                ("H", 2, 0, 0),
            ]
        )

        def assertQueryResults(_q1, _q2):
            q1 = list(_q1)
            q2 = list(_q2)

            self.assertEqual(len(q1), len(q2))
            for p1, p2 in zip(q1, q2):
                p1 = list(p1)
                p2 = list(p2)
                self.assertSetEqual(set(p1), set(p2))

        # Test k=1, no search_r
        assertQueryResults(S.atoms_near([0.1, 0, 0]), [{(0, S[0])}])

        assertQueryResults(
            S.atoms_near([0.1, 0, 0, 1.1, 0, 0]),
            [
                {(0, S[0])},
                {(1, S[1])},
            ],
        )

        # Test k=2 version
        assertQueryResults(
            S.atoms_near([0.1, 0, 0], k=2),
            [{(0, S[0]), (1, S[1])}],
        )

        assertQueryResults(
            S.atoms_near([0.1, 0, 0, 2.1, 0, 0], k=2),
            [
                {(0, S[0]), (1, S[1])},
                {(1, S[1]), (2, S[2])},
            ],
        )

        # Test search_r
        assertQueryResults(
            S.atoms_near([0.1, 0, 0], search_r=1.5),
            [
                {(0, S[0]), (1, S[1])},
            ],
        )

        assertQueryResults(
            S.atoms_near([0.1, 0, 0, 2.1, 0, 0], search_r=1.5),
            [
                {(0, S[0]), (1, S[1])},
                {(1, S[1]), (2, S[2])},
            ],
        )
        self.assertTrue(S.in_(Atom("H", [0, 0, 0])))
        self.assertFalse(S.in_(Atom("C", [0, 0, 0])))

        # Test periodic query
        S = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("H", 1, 0, 0),
                ("H", 2, 0, 0),
                ("H", 3, 0, 0),
            ],
            unit_cell=np.array([3.0, 3.0, 3.0]),
        )
        assertQueryResults(S.atoms_near([3.1, 0, 0]), [{(0, S[0])}])
        assertQueryResults(S.atoms_near([3.1, 0, 3], k=2), [{(0, S[0]), (3, S[3])}])
        assertQueryResults(
            S.atoms_near([0.1, 0, 0], search_r=0.2), [{(0, S[0]), (3, S[3])}]
        )
        self.assertTrue(S.in_(Atom("H", [0, 0, 0])))
        self.assertTrue(S.in_(Atom("H", [3, 3, 3])))

    def test_named_systems(self):
        """Test NamedSystems in the DB"""
        # Create an out-of-order system
        SYSTEM_NAME = "Test System"
        sys = NamedSystem.from_tuples(
            [
                ("C", 1, 1, 1),
                ("C", 2, 2, 2),
                ("H", 0, 0, 0),
            ],
            name=SYSTEM_NAME,
        )
        DBSystem.add_systems([sys])
        self.assertEqual(DBSystem.select().count(), 1)

        db_sys = DBSystem.get_systems([sys._saved])[sys._saved]
        named_sys = DBSystemLabel.get_systems_by_name([SYSTEM_NAME])[SYSTEM_NAME]
        self.assertEqual(sys, db_sys)
        self.assertEqual(sys, named_sys)

        # Check ordering
        # Named system should be in non-canonical order
        for a1, a2 in zip(sys, named_sys):
            self.assertEqual(a1, a2)

        for a1, a2 in zip(sys, db_sys):
            self.assertNotEqual(a1, a2)

        # Verify that we preserve offsets when we save to the DB
        named_systems = [
            NamedSystem.from_tuples([("H", 0, 0, 0)], name="s1"),
            NamedSystem.from_tuples([("H", 1, 2, 3)], name="s2"),
            NamedSystem.from_tuples([("H", -1, -1, -1)], name="s3"),
        ]

        # Quick test of hashing...
        self.assertEqual(len(set(named_systems)), 3)
        self.assertEqual(len(UniqueSystemSet(named_systems)), 1)
        DBSystem.add_systems(named_systems)
        self.assertEqual(DBSystem.select().count(), 2)  # Only one gets added

        # We can re-add without error
        DBSystem.add_systems([NamedSystem.from_tuples([("H", 0, 0, 0)], name="s1")])

        # Can't add a different system with the same name
        with self.assertRaises(peewee.IntegrityError):
            DBSystem.add_systems([NamedSystem.from_tuples([("C", 0, 0, 0)], name="s1")])

        for s in named_systems:
            self.assertEqual(named_systems[0]._saved, s._saved)

        DB_named_systems = DBSystemLabel.get_systems_by_name(["s1", "s2", "s3"])
        for s in named_systems:
            db_s = DB_named_systems[s.name]
            assert_allclose(s[0].r, db_s[0].r)

    def test_mask_introspection(self):
        S1 = System.from_tuples([("H", 0, 0, 0), ("H", 0, 0, 1)], unit_cell=[5, 5, 5])

        # Testing systems!
        S2 = S1.subsystem([0])
        self.assertEqual(S1.subsystem_mask(S2), frozenset([0]))

        # S3 = S1.subsystem([0])
        # S3.update_atoms([0], role=GHOST_ATOM)
        # assert S3[0] is GHOST_ATOM
        # self.assertEqual(
        #     S1.subsystem_mask(S3),
        #     Mask({CellIndex((0, 0, 0)): frozenset([AtomMask(0, GHOST_ATOM)])}),
        # )

        # S4 = S1.subsystem([0, 1])
        # S4.update_atoms([0], role=GHOST_ATOM)
        # S4.update_atoms([1], cell=np.array([0, 0, -1], dtype=int))
        # self.assertEqual(
        #     S1.subsystem_mask(S4),
        #     Mask({
        #         CellIndex((0, 0, 1)): frozenset([AtomMask(0, GHOST_ATOM)]),
        #         CellIndex((0, 0, 0)): frozenset([AtomMask(1)])
        #     }),
        # )

    def test_hashing(self):
        s1 = NamedSystem.from_tuples([("H", 0, 0, 0)], name="s1")
        s2 = NamedSystem.from_tuples([("H", 1, 2, 3)], name="s2")
        s3 = NamedSystem.from_tuples([("H", -1, -1, -1)], name="s3")

        self.assertNotEqual(s1, s2)
        self.assertTrue(s1.eq(s2, bound_COM_join))

        self.assertNotEqual(s1, s3)
        self.assertTrue(s1.eq(s3, bound_COM_join))

        self.assertNotEqual(s2, s3)
        self.assertTrue(s2.eq(s3, bound_COM_join))

        self.assertEqual(s1.fingerprint, s2.fingerprint)
        self.assertEqual(s1.fingerprint, s3.fingerprint)
        self.assertEqual(s2.fingerprint, s3.fingerprint)

        self.assertEqual(len({s1, s2, s3}), 3)
        self.assertEqual(len(UniqueSystemSet([s1, s2, s3])), 1)

    def test_pickle(self):
        atom = (Atom("H", [0.0, 0.0, 0.0]),)
        data = pickle.dumps(atom)
        atom_loaded = pickle.loads(data)
        self.assertEqual(atom, atom_loaded)

        sys = System([Atom("H", [0.0, 0.0, 0.0])])
        sys.COM
        sys.__hash__()
        sys.fingerprint

        data = pickle.dumps(sys)
        sys_loaded = pickle.loads(data)
        self.assertEqual(sys, sys_loaded)
