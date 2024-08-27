#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from json import JSONDecodeError, loads
from typing import Dict, Optional, TextIO

import numpy as np

from conformer.systems import Atom, NamedSystem

from .common import SupersystemModel


def XYZRead(file: TextIO, charges: Optional[Dict[int, int]] = None) -> NamedSystem:
    num_atoms = 0
    comment = ""
    atoms = []
    if charges is None:
        charges = {}

    for i, line in enumerate(file):
        if i == 0:  # Number of atoms
            num_atoms = int(line)
            continue
        if i == 1:  # Comment line
            comment = line.strip()
            continue

        if not line.strip():
            break # Break lines are allowed at end of file
        l_parts = line.split()
        t = l_parts[0]
        r = np.array((float(l_parts[1]), float(l_parts[2]), float(l_parts[3])))

        try:
            # Charges are 1-based indexed
            # We lose 2 lines from count/comment
            charge = charges[i - 1]
        except KeyError:
            charge = 0
        atoms.append(Atom(t, r, charge=charge))

    if num_atoms != len(atoms):
        raise Exception(
            f"XYZ input contains {len(atoms)} atoms but promised {num_atoms}."
        )

    # Load data supplied in the comment line
    sys = NamedSystem(atoms=atoms)  # Names will be added by caller
    try:
        comment_json = loads(comment)
    except JSONDecodeError:
        comment_json = None
    
    if comment_json:
        ssm = SupersystemModel(source="COMMENT", **comment_json)
        # Handle charges
        if not charges and ssm.charges:
            for i, c in ssm.charges.items():
                sys._atoms[i]._atom.charge = np.int16(c)
        if ssm.name:
            sys.name = ssm.name
        if ssm.note:
            sys.meta.update(note=ssm.note)
        if ssm.unit_cell:
            sys.unit_cell = np.array(ssm.unit_cell)
    else:
        sys.meta.update(comment=comment)

    return sys
