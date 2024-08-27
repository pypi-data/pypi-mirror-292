#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest

import networkx as nx
import numpy as np

import conformer.spatial as spatial
from conformer.example_systems import read_example
from conformer.systems import Atom, System


class SpatialTestCases(unittest.TestCase):
    def setUp(self):
        self.sys = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("H", 1, 0, 0),
                ("H", 2, 0, 0),
            ]
        )

    def test_distance_matrix(self):
        S = self.sys

        self.assertEqual(spatial.distance(S[0], S[1]), 1.0)

        dm = spatial.AtomDistanceMatrix(S, spatial.distance)
        self.assertEqual(dm[S[0], S[1]], 1.0)
        self.assertEqual(dm[S[0], S[2]], 2.0)
        self.assertEqual(dm[S[1], S[2]], 1.0)

        self.assertEqual(dm[S[2], S[0]], 2.0)  # Check the idxs can be exchanged

        self.assertEqual(dm[0, 1], 1.0)  # Test int lookups
        self.assertEqual(dm[1, 0], 1.0)  # Test input invariance

    def test_neighbor_graph(self):
        S = self.sys
        ng = spatial.primative_neighbor_graph(self.sys, 1.2)
        ref_ng = nx.Graph()
        ref_ng.add_edges_from(
            [
                (S[0], S[1], dict(r=1.0)),
                (S[1], S[2], dict(r=1.0)),
            ]
        )

        self.assertEqual(len(ng), len(ref_ng))

        for u, v, d in ng.edges(data=True):
            d_ref = ref_ng.edges[u, v]
            self.assertDictEqual(d, d_ref)

    def test_DGraph(self):
        # Make a potato chip shape
        S = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("H", 0, 1, 0),
                ("H", 0.5, 0.5, 1),
                ("H", -0.5, 0.5, 1),
            ]
        )

        NEIGHBORS = {
            S[0]: {S[1], S[2], S[3]},
            S[1]: {S[0], S[2], S[3]},
            S[2]: {S[0], S[1], S[3]},
            S[3]: {S[0], S[1], S[2]},
        }

        dg = spatial.Delaunay_graph(S)
        for n in dg.nodes:
            self.assertSetEqual(set(dg.neighbors(n)), NEIGHBORS[n])

    def test_geometry_fns(self):
        S = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("H", 0, 1, 0),
                ("H", 0.5, 0.5, 1),
                ("H", -0.5, 0.5, 1),
            ]
        )  # A cross of atoms, two separated by 1 A
        self.assertAlmostEqual(spatial.distance(S[0], S[3]), 1.2247, places=3)
        self.assertAlmostEqual(
            spatial.angle(S[0], S[1], S[2], use_degrees=True), 65.9052, places=3
        )
        self.assertAlmostEqual(
            spatial.torsion_angle(S[0], S[1], S[2], S[3], use_degrees=True),
            78.46304,
            places=3,
        )

        S.unit_cell = np.array([2.0, 2.0, 1.0])
        # self.assertAlmostEqual(spatial.MIC_distance(S[0], S[3]), 0.7071, places=3)

        dm = spatial.AtomDistanceMatrix(S, spatial.MIC_distance)
        np.testing.assert_allclose(
            dm.data, [1.0, 0.70710678, 0.70710678, 0.70710678, 0.70710678, 1.0]
        )

        # Test vectorization!
        dm_vec = spatial.AtomDistanceMatrix(
            S, spatial.MIC_distance, vectorized_metric=spatial.vecotrized_MIC_distance
        )
        np.testing.assert_allclose(
            dm_vec.data, [1.0, 0.70710678, 0.70710678, 0.70710678, 0.70710678, 1.0]
        )

        # Edge cases
        S1 = System.from_tuples(
            [
                ("H", 1.2, 0.0, 0.0),
                ("H", -20.4, 0.0, 0.0),
            ],
            unit_cell=[2, 2, 2],
        )
        self.assertAlmostEqual(spatial.MIC_distance(S1[0], S1[1]), 0.4)
        self.assertAlmostEqual(spatial.MIC_distance(S1[1], S1[0]), 0.4)

    def test_bonding_radii(self):
        """
        Should be approximatly https://en.wikipedia.org/wiki/Ionic_radius#cite_note-Shannon-6

        This is an inexact fix. It likely needs it to be better
        """
        self.assertAlmostEqual(
            spatial.bonding_radius(Atom("Na", [0, 0, 0], charge=1)), 1.079, 2
        )
        self.assertAlmostEqual(  # No change
            spatial.bonding_radius(Atom("Mg", [0, 0, 0], charge=1)), 1.41, 2
        )
        self.assertAlmostEqual(  # Will change
            spatial.bonding_radius(Atom("Na", [0, 0, 0], charge=2)), 1.079, 2
        )
        self.assertAlmostEqual(
            spatial.bonding_radius(Atom("F", [0, 0, 0], charge=0)), 0.57, 2
        )
        self.assertAlmostEqual(
            spatial.bonding_radius(Atom("F", [0, 0, 0], charge=-1)), 0.876, 2
        )

    def test_bonding_graph(self):
        w6 = read_example("water-6-cluster.xyz")
        BG = spatial.bonding_graph(w6)
        # for N in BG.nodes:
        #     print(N)
        #     print(list(BG.neighbors(N)))
        self.assertEqual(nx.number_connected_components(BG), 6)
        for comp in nx.connected_components(BG):
            s = System(comp)
            self.assertEqual(s.chemical_formula(), "H2O")

    def test_filtering(self):
        sys = System.from_tuples([("H", i, 0, 0) for i in range(5)])
        cc = list(spatial.covalent_components(sys))
        self.assertEqual(len(cc), 5)
        dm = spatial.system_distance_matrix(cc, spatial.system_COM_distance)

        target = System.from_tuples([("H", 0, 0, 0)])
        results = [System.from_tuples([("H", 1, 0, 0)])]
        self.assertListEqual(spatial.filter_r(dm, target, 1.5), results)
        self.assertListEqual(spatial.filter_n_closest(dm, target, 1), results)
