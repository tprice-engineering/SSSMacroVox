"""Build a synthetic sphere and visualize an octree cross-section."""

import argparse
from dataclasses import asdict
import json
from math import pi
from pathlib import Path

from macrovoxel import voxelize


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("build"))
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--samples", type=int, default=96)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.patches import Circle, Patch, Rectangle

    radius = 0.28
    center = 0.5
    leaves = voxelize(
        lambda point: sum((v - center) ** 2 for v in point) <= radius ** 2,
        max_depth=args.max_depth, samples=args.samples, seed=args.seed,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    estimated = sum(leaf.edge ** 3 for leaf in leaves if leaf.filled)
    exact = 4 * pi * radius ** 3 / 3
    summary = {
        "grid_cells_at_finest_resolution": 8 ** args.max_depth,
        "octree_leaves": len(leaves),
        "filled_leaves": sum(leaf.filled for leaf in leaves),
        "estimated_sphere_volume": estimated,
        "analytical_sphere_volume": exact,
        "relative_volume_error": (estimated - exact) / exact,
        "sphere_radius": radius,
        "samples_per_cube": args.samples,
        "seed": args.seed,
    }
    payload = {"summary": summary, "leaves": [asdict(leaf) for leaf in leaves]}
    (args.out_dir / "octree.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(6, 6), layout="constrained")
    for leaf in leaves:
        x, y, z = leaf.origin
        if z <= center < z + leaf.edge:
            ax.add_patch(Rectangle((x, y), leaf.edge, leaf.edge,
                                   facecolor="#79bfd4" if leaf.filled else "#f3f5f8",
                                   edgecolor="#64748b", linewidth=0.4))
    circle = Circle((center, center), radius, fill=False, edgecolor="#a63521",
                    linestyle="--", linewidth=1.5, label="Analytical sphere boundary")
    ax.add_patch(circle)
    ax.legend(handles=[Patch(color="#79bfd4", label="Filled leaves"), circle], loc="upper right")
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="x", ylabel="y",
           title="Synthetic sphere at z = 0.5", aspect="equal")
    fig.savefig(args.out_dir / "sphere-slice.png", dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
