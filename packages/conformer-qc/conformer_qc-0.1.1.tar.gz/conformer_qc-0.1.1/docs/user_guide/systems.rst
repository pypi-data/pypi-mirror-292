=======
Systems
=======

Systems are a collection of atoms. They can be molecules, clusters, or :ref:`periodic<Periodic Systems>` unit cells.

Importing Systems
=================

Systems can be loaded using the `systems` section of a strategy file. Systems are generally imported using .xyz, .pdb, and .frag files

.. code-block:: yaml

    systems:
        -
            name: system_name
            source: path/to/your/file
            note: More information about the system (optional)
            charges: 
                ... # Mapping of index/charge (optional)
            roles: 
                ... # Mapping of index/role (optional)
            unit_cell: [10, 10, 10] # unit cell dimensions in Å (optional) 
        - # Additional Systems
            ...

This block will add a system called ``system_name`` to the database. ``charges`` and ``roles`` are 1-based key-value pairs specifying the charge and role as :ref:`discussed below<Roles>`. If the charge and role are not specified for an atom, charge defaults to 0 and the role is assigned to ``PHYSICAL``.

.. note:: 
    PDB files will use the atom number in the PDB instead of the 1-based index for
    the `charges` and `roles` properties. 

See the :ref:`examples<defining_roles>` section for usage with the Fragme∩t CLI.


Atoms
=====

In addition to it's Cartesian coordinate (``r``) and the element name (``t``), atoms can specify a total charge, role, and cell.

Charges
-------

Charges are the *total* charge of the atom (*i.e.* nuclear charge + total electron charge). In Conformer, charges are localized to specific atoms. This is in contrast with common *ab initio* software packages which specify the *total* system charge; however, this is incompatible with fragmentation.

Roles
-----

Atoms in Conformer can take on different roles. The input 

``PHYSICAL`` (default)
    An atom with a nucleus, electrons, and basis functions
``CAPPING``
    A physical atom used to cap a severed covalent bond
``PINNED``
    A physical atom with a fixed/constrained location
``GHOST``
    Just basis functions centered at ``r``
``POINT_CHARGE``
    A point charge centered at ``r``
``DUMMY``
    A Cartesian point with no basis functions, nucleus, or charge

Custom roles can be defined :ref:`using a mapping<A broken link>`.

Cell
----

The unit vector (tuple of three integers) of the atom in a :ref:`quasi-periodic<quasi-periodic systems>`. For clusters and fully-periodic systems this is set to ``(0, 0, 0)``

Periodic Systems
================

Conformer supports periodic systems by specifying a unit cell. Systems can be fully-periodic which respect periodic boundary conditions or quasi-periodic which supports multiple atom images accross unit cells. 

Unit cells 

Full Periodic Systems
----------------------

Full periodic systems can be used with only some drivers (so far only CP2K). They can also be used as a starting point for generating quasi-periodic subsystems for use with non-periodic drivers.

Currently, conformer support orthorhombic unit cells.

Quasi-Periodic Systems
----------------------

Quasi-periodic systems have a defined unit cell which is used to calculate location of each atom. This allows fragment-based calculations of periodic systems with conventional non-periodic drivers.


Canonical Ordering
==================

Conformer defines a canonical ordering scheme for atoms based on their element, position, role, charge, and other metadata. Atoms are stored in canonical order in the database and this will likely differ from the ordering of the .xyz or .pdb input files. When a system is retrieved by name (*e.g.* ``fragment system info system_name`` or :func:`~conformer.stages.get_systems`) it will be reordered from canonical ordering to its original ordering.

Canonical ordering means that two equivalent atoms in two translationally equivalent systems should have the same index. It is not recommended relying on atom ordering. Instead, please use :meth:`conformer.systems.System.join_map` to find equivalent atoms.

.. todo:: 

    Give specifics for canonical ordering. A dry but important topic


Examples
========

.. _defining_roles:

Manually Defining Roles a Fragme∩t Project
-------------------------------------------

.. note:: 
    
    In practice, it would be simpler and less error-prone to use the :class:`~conformer.mods.counterpoise.CounterpoiseSubsystemMod`. Roles are defined explicitly by way of example.

Suppose you wanted to calculate the counterpoise corrected interaction energy of a
water dimer. This would require the water dimer and two water monomers *with* the other
monomer include as ghost atoms. Starting with the geometry

.. TODO: Update this example to use the subsystem syntax!
 
.. code-block:: text
    :caption: ``water2.xyz``

    6
    
    O -1.126149 -1.748387 -0.423240
    H -0.234788 -1.493897 -0.661862
    H -1.062789 -2.681331 -0.218819
    O -0.254210  1.611495 -1.293845
    H -1.001520  1.163510 -1.690129
    H -0.153399  2.411746 -1.809248

the three systems can be added using this strategy file

.. code-block:: yaml
    :caption: ``import_system.yaml``

    systems:
      -
        name: water_dimer
        source: ./water2.xyz
      -
        name: water_1
        note: The first water + ghost atoms!
        source: ./water2.xyz
        roles:
          1: GHOST
          2: GHOST
          3: GHOST
      -
        name: water_2
        note: The second water + ghost atoms!
        source: ./water2.xyz
        roles:
          1: GHOST
          2: GHOST
          3: GHOST 

and running ``fragment init import_system.yaml`` in a new project directory. It's now stored in ``fragment.db`` and can be retrieved using the ``fragment system info --with-atoms ...`` command.

.. code-block:: text
    :caption: ``$ fragment system info --with-atoms water_dimer water_1``

    System water_dimer:
    Created: 2024-07-09T10:50
    Fingerprint: 690658ae12ec81995040d7b578f95e62609fbce7
    Database ID: 2
    Chemical Formula: H4O2
    Number of Atoms: 6
    Charge: 0
    Multiplicity: 1
    Mass:  36.02112937 amu
    Atoms:
        T                X             Y             Z CHRG ROLE META
        O        -1.126149     -1.748387     -0.423240    0      {}
        H        -0.234788     -1.493897     -0.661862    0      {}
        H        -1.062789     -2.681331     -0.218819    0      {}
        O        -0.254210      1.611495     -1.293845    0      {}
        H        -1.001520      1.163510     -1.690129    0      {}
        H        -0.153399      2.411746     -1.809248    0      {}

    System water_1:
    Created: 2024-07-09T10:50
    Fingerprint: 9e9edf8e68c524894740ab7761ea73cd6d32b641
    Database ID: 1
    Chemical Formula: H2O
    Number of Atoms: 6
    Charge: 0
    Multiplicity: 1
    Mass:  18.01056468 amu
    Atoms:
        T                X             Y             Z CHRG ROLE META
        O        -1.126149     -1.748387     -0.423240    0 G    {}
        O        -0.254210      1.611495     -1.293845    0      {}
        H        -1.062789     -2.681331     -0.218819    0 G    {}
        H        -1.001520      1.163510     -1.690129    0      {}
        H        -0.234788     -1.493897     -0.661862    0 G    {}
        H        -0.153399      2.411746     -1.809248    0      {}