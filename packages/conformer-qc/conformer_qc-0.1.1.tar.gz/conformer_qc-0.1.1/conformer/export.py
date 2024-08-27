#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None
import json
from collections import defaultdict
from itertools import product

import numpy as np

from conformer.common import PHYSICAL_ATOM, role_to_str
from conformer.spatial import bonding_graph
from conformer.systems import NamedSystem, System


def to_xyz_str(sys: System):
    """
    Dumps atom to xyz file with correct metadata
    """
    # Load metadata that can't be represented in XYZ file
    charges = {}
    roles = {}
    coord_strs = []

    # Use 1-based indexing for public-facing code
    for i, a in enumerate(sys, 1):
        if a.charge != 0:
            charges[i] = int(a.charge)
        if a.role != PHYSICAL_ATOM:
            roles[i] = role_to_str(a.role)
        coord_strs.append(
            f"{a.t:<4s}  {a.r[0]:> 13.6f} {a.r[1]:> 13.6f} {a.r[2]:> 13.6f}"
        )

    # Load into JSON serlializable metadata
    meta = {}
    if sys.unit_cell is not None:
        meta["unit_cell"] = list(sys.unit_cell)
    if charges:
        meta["charges"] = charges
    if roles:
        meta["roles"] = roles
    if isinstance(sys, NamedSystem):
        meta["name"] = sys.name
        meta["meta"] = sys.meta

    # Create output
    xyz = [
        str(sys.size),
        json.dumps(meta) if meta else "",
    ]
    xyz.extend(coord_strs)

    return "\n".join(xyz)


# TODO: Choose nicer colors.
# Roughly follows https://en.wikipedia.org/wiki/CPK_coloring
OTHER_COLOR = "pink"
COLORS = defaultdict(lambda: OTHER_COLOR)
COLORS.update(
    {
        "H": "white",
        "C": "dimgray",
        "N": "blue",
        "O": "red",
        "F": "green",
        "Cl": "green",
        "Br": "brown",
        "I": "purple",
        "S": "yellow",
        "P": "orange",
        "B": "tan",
        "Li": "violet",
        "Na": "violet",
        "K": "violet",
        "Rb": "violet",
        "Cs": "violet",
        "Fr": "violet",
        "Be": "darkgreen",
        "Mg": "darkgreen",
        "Ca": "darkgreen",
        "Sr": "darkgreen",
        "Ba": "darkgreen",
        "Ra": "darkgreen",
        "Fe": "darkorange",
        "Ag": "silver",
        "Au": "gold",
        "Ti": "slategray",
        "Cu": "goldenrod",
        "Co": "steelblue",
        "He": "cyan",
        "Ne": "cyan",
        "Ar": "cyan",
        "Kr": "cyan",
        "Xe": "cyan",
    }
)


def visualize(
    sys: System,
    show_idxs=True,
    size_scale=7.5,
    ghost_alpha=0.4,
    draw_bonds=True,
    palette=COLORS,
):
    """
    Plots the system in a matplot lib window
    """
    if plt is None:
        raise ModuleNotFoundError("Please install Matplotlib to use `visualize`")

    if not isinstance(palette, defaultdict):
        raise ValueError("`palette` must be a `defaultdict`")

    # TODO: Make this easier to integrate with other plots
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    # Hide background
    ax.set_axis_off()

    # Create a bounding box to keep the 1:1:1 aspect ratio
    geom_mean = sys.r_matrix.mean(axis=0)
    bb_span = np.max(sys.r_matrix.max(axis=0) - sys.r_matrix.min(axis=0)) / 2
    bb_coords = np.zeros((8, 3))

    for i, (dx, dy, dz) in enumerate(
        product(
            [-bb_span, bb_span],
            [-bb_span, bb_span],
            [-bb_span, bb_span],
        )
    ):
        bb_coords[i, :] = geom_mean[0] + dx, geom_mean[1] + dy, geom_mean[2] + dz

    # Create the figure and the axis
    ax.scatter(*bb_coords.T, s=0)

    G = bonding_graph(sys)

    # Plot bonds
    if draw_bonds:
        for u, v in G.edges():
            if not u.is_physical or not v.is_physical:
                continue
            r = np.vstack([u.r, v.r])
            ax.plot(*r.T, c="black")

    # Plot atoms
    for i, a in enumerate(sys):
        r = np.reshape(a.r, (3, 1))
        # Make atoms proportional to vDW radii
        s = (a.vdw_radius * size_scale) ** 2 * np.pi
        alpha = 1.0 if a.is_physical else ghost_alpha
        c = palette[a.t]
        ax.scatter(*r, c=c, s=s, edgecolors="black", alpha=alpha, zorder=1)

    # Plot atom IDs
    if show_idxs:
        for i, a in enumerate(sys):
            ax.text(
                *a.r,
                i,
                None,
                zorder=10,
                horizontalalignment="center",
                verticalalignment="center",
            )
    plt.show()

    return fig
