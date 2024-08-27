#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
"""Migration migration_20240819_015214.py

Please explain why this migration is necessary
"""

from collections import defaultdict

import numpy as np
import peewee

from conformer.db.models import DBSystem, DBUnitCell
from conformer.systems import (
    hash_System_v1,
    hash_System_v2,
    hash_UnitCell_v1,
    hash_UnitCell_v2,
)


def migrate(project_path: str, database_path: peewee.Database) -> None:
    print("UPDATING SYSTEM HASHES")
    id_to_old = {
        i: f for i, f in DBSystem.select(DBSystem.id, DBSystem.fingerprint).tuples()
    }
    id_to_new = {} 
    new_fps = set()
    duplicates = defaultdict(list) 

    num_sys = 0
    mismatch = 0

    for ids in peewee.chunked(id_to_old.keys(), 500):
        systems = DBSystem.get_systems(ids)
        for i in ids:
            num_sys += 1
            sys = systems[i]
            if hash_System_v1(sys).hexdigest() != id_to_old[i]:
                # print(f"  WARNING: Database fingerprint != V1 hash: {sys._saved} ({sys.chemical_formula()})")
                mismatch += 1
            new_fp = hash_System_v2(sys).hexdigest()
            if new_fp in new_fps:
                duplicates.append(new_fp)
            else:
                new_fps.add(new_fp)
            id_to_new[i] = hash_System_v2(sys).hexdigest()
    if mismatch:
        print(f"{mismatch}/{num_sys} were missmatched")
        print("The hashes were recalculated so this shouldn't be an issue")
    if len(id_to_new) != len(set(id_to_new.values())):
        print("THERE WERE DUPLICATES!")
        print("Please file an issue on GitLab and we'll help you resolve this")
    print(duplicates)

    for i, f in id_to_new.items():
        DBSystem.update(fingerprint=f).where(DBSystem.id == i).execute()

    print("UPDATING UNIT CELL HASHES")
    # Handle Unit Cells
    id_to_old = {
        c.id: c for c in DBUnitCell.select()
    }
    id_to_new = {} 
    new_fps = set()
    duplicates = defaultdict(list) 

    num_cells = 0
    mismatch = 0
        
    for db_id, db_cell in id_to_old.items():
        num_cells += 1
        cell = np.array([db_cell.a, db_cell.b, db_cell.c], dtype=np.float64)

        if hash_UnitCell_v1(cell) != db_cell.fingerprint:
            # print(f"CELL: Database fingerprint != V1 hash: {db_id}")
            mismatch += 1

        new_fp = hash_UnitCell_v2(cell).hexdigest()
        if new_fp in new_fps:
            duplicates.append(new_fp)
        else:
            new_fps.add(new_fp)
        id_to_new[db_id] = new_fp

    if mismatch:
        print(f"{mismatch}/{num_cells} were missmatched")
        print("The hashes were recalculated so this shouldn't be an issue")
    print(len(set(id_to_new.values())), len(id_to_new))
    if len(id_to_new) != len(set(id_to_new.values())):
        print("THERE WERE DUPLICATES!")
        print("Please file an issue on GitLab and we'll help you resolve this")
    print(duplicates)

    for i, f in id_to_new.items():
        DBUnitCell.update(fingerprint=f).where(DBUnitCell.id == i).execute()
    # exit()  # Cancel the migration
