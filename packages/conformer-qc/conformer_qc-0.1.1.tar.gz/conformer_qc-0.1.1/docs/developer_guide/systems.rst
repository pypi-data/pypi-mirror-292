=======
Systems
=======

A :py:class:`~conformer.systems.System` is a collection of :py:class:`~conformer.systems.AbstractAtom`. Please read the :doc:`user guide</user_guide/systems>` to get a general overview of how systems are used. A system can be constructed as

.. code-block:: python

    from conformer.systems import System, Atom
    H2 = System([
        Atom("H", [0.0, 0.0, 0.0]),
        Atom("H", [0.74, 0.0, 0.0]),
    ])

    print(H2)
    #> System(formula="H2", name="sys-15bdc20c")

Alternatively structures can be imported from .xyz, .pdb, and .frag files using the :py:func:`~conformer.geometry_readers.read_geometry` function or with a Project using :py:meth:`~conformer.project.Project.read_geometry`. Systems can also be imported into projects using :ref:`strategy files<defining_roles>`. 

.. code-block:: python

    from conformer.geometry_readers import read_geometry
    
    # Suppost we have a water6 geometry in the files "water6.xyz"
    water6 = read_geometry("water6", "water6.xyz")

Individual atoms can be accesses by subscripting the system and through iteration.

.. code-block:: python

    print(H2[0])
    #> BoundAtom(t=H, r=[0.74 0.   0.  ])

    print(list(H2[1,2])) # Returns a generator expression. Use `list` to make printable
    #> [BoundAtom(t=H, r=[0. 0. 0.]), BoundAtom(t=H, r=[0.74 0.   0.  ])]

    print(H2[0:1]) # Return a list
    #> [BoundAtom(t=H, r=[0. 0. 0.]), BoundAtom(t=H, r=[0.74 0.   0.  ])]

    for a in H2:
        print(a)
    #> BoundAtom(t=H, r=[0. 0. 0.])
    #> BoundAtom(t=H, r=[0.74 0.   0.  ])

    # TODO: Type inconsistency. Maybe fix?

Atoms vs. BoundAtoms
====================

Subsystem Creation
==================

Subsystem are created using the :py:meth:`System.subsystem<conformer.systems.System.subsystem>` method. For example, to get the first water molecule from our 6-water cluster use

.. code-block:: python

    water_1 = water6.subsystem([0, 1, 2])
    print(water_1)
    #> System(formula="H2O", name="sys-881b41b6")

Subsystem Mods
--------------

Sometimes simply taking the atoms out of the supersystem and making a new one isn't sufficient. For example capped covalent bonds might need to be capped, missing atoms might get added back as point charges or ghost atoms, or the system might need to be re-wrapped to comply with the minimal image convention. Mods exist as a way to make these processes easier.

For example, suppose you wanted to select only one of the hydrogens from the ``H2`` system and replace the other with a ghost atom you could run

.. code-block:: python

    from conformer.mods.counterpoise import CounterpoiseSubsystemMod
    
    csm = CounterpoiseSubsystemMod() # Construct the new mod. Returns a callable
    H1_ghost = H2.subsystem([0], mods=[csm])
    
    for a in H1_ghost:
        print(a)
    #> BoundAtom(t=H, r=[0.74 0.   0.  ], role='G')
    #> BoundAtom(t=H, r=[0. 0. 0.])

Mods need only be a callable or a function which accepts three arguments: ``supersystem``, the original supersystems; ``key``, the first argument of ``.subsystem`` used to trim ``supersystem``; [#ss_idxs]_ ``subsystem``, the current state of the subsystem. Multiple mods can be applied 

.. warning::

    Some modes might interact poorly with each other. For example, when a subsystem is created, severed bonds could be capped and then ghost atoms could be added for a counterpoise correction. Should ghost atoms be added for the atoms replaced by caps?

    Mod interactions is an active area of development. We hope new benchmarks of these methods will make clear what the best practices should be.

A simplified version of the counterpoise mode is given below. It requires additional code to be used as a Stage.

.. code-block:: python

    def counterpoise_mod(supersystem: System, key: SystemKey, system: System) -> System:
        ghost_idxs = set(range(len(supersystem))).difference(key)
        system.add_atoms(*supersystem[ghost_idxs], role=GHOST_ATOM)
        return system


Some examples of existing mods in Conformer are

* :doc:`Bond Capping</api_reference/mods/capping>`
* :doc:`Counterpoise Corrections</api_reference/mods/counterpoise>`
* :doc:`Minimal Image Convention</api_reference/mods/MIC>`

Fingerprinting
==============

Canonization
------------

System Joins
============

.. [#ss_idxs] these indices are relative to the supersystem, not the subsystem