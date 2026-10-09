# rama.py
# Written by Jeremy Tame with extensive help from ChatGPT

from pymol import cmd
import matplotlib.pyplot as plt


def rama(selection="all"):
    """
    Make a clickable Ramachandran plot for a PyMOL selection.

    Usage:
        select my_object, selection-arguments (eg resi 100-200 and chain A)
        rama my_object
    """

    # Get phi/psi from PyMOL
    phipsi = cmd.get_phipsi(selection)

    if not phipsi:
        print("No phi/psi angles found for selection:", selection)
        return

    residues = []

    for (model, index), (phi, psi) in phipsi.items():

        # Get residue information for this atom
        atoms = []
        cmd.iterate(
            f"{model}`{index}",
            "atoms.append((chain, resi, resn))",
            space={"atoms": atoms}
        )

        if not atoms:
            continue

        chain, resi, resn = atoms[0]

        residues.append({
            "model": model,
            "index": index,
            "chain": chain,
            "resi": resi,
            "resn": resn,
            "phi": phi,
            "psi": psi
        })

    if not residues:
        print("No usable residues found.")
        return

    x = [r["phi"] for r in residues]
    y = [r["psi"] for r in residues]

    fig, ax = plt.subplots()
    plt.title(selection)

    colors = []
    for r in residues:
        if r["resn"] == "GLY":
            colors.append("red")
        elif r["resn"] == "PRO":
            colors.append("lightgreen")
        elif r["resn"] == "CYS":
            colors.append("yellow")
        elif r["resn"] == "TRP":
            colors.append("magenta")
        else:
            colors.append("C0")   # matplotlib's normal default blue

    points = ax.scatter(
        x,
        y,
        s=35,
        c=colors,
        edgecolors="black",
        linewidths=0.4,
        picker=True
    )
    # Legend.
    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0], [0], marker='o', linestyle='',
            markerfacecolor='red', markeredgecolor='black',
            label='Gly'),
        Line2D([0], [0], marker='o', linestyle='',
            markerfacecolor='lightgreen', markeredgecolor='black',
            label='Pro'),
        Line2D([0], [0], marker='o', linestyle='',
            markerfacecolor='yellow', markeredgecolor='black',
            label='Cys'),
        Line2D([0], [0], marker='o', linestyle='',
            markerfacecolor='magenta', markeredgecolor='black',
            label='Trp')
    ]

    legend = ax.legend(handles=legend_items, loc="best", fontsize=8)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-180, 180)

    ax.set_xticks(range(-180, 181, 60))
    ax.set_yticks(range(-180, 181, 60))

    ax.axhline(0, linewidth=0.5)
    ax.axvline(0, linewidth=0.5)

    ax.set_xlabel("Phi")
    ax.set_ylabel("Psi")
    ax.set_title("Ramachandran plot: " + selection)

    ax.grid(True, linewidth=0.3)

    annotation = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(10, 10),
        textcoords="offset points"
    )
    annotation.set_visible(False)

    def on_pick(event):

        if not len(event.ind):
            return

        i = event.ind[0]
        r = residues[i]

        label = (
            f"{r['resn']} {r['resi']} "
            f"chain {r['chain']}\n"
            f"phi={r['phi']:.1f}  psi={r['psi']:.1f}"
        )

        annotation.xy = (r["phi"], r["psi"])
        annotation.set_text(label)
        annotation.set_visible(True)
        fig.canvas.draw_idle()

        # Make a PyMOL selection
        selname = "rama_pick"

        pymol_sel = (
            f"model {r['model']} and "
            f"chain {r['chain']} and "
            f"resi {r['resi']}"
        )

        cmd.select(selname, pymol_sel)
        cmd.show("sticks", selname)
        cmd.zoom(selname, 8)

        print(
            f"{r['model']} "
            f"{r['chain']}:{r['resi']} "
            f"{r['resn']} "
            f"phi={r['phi']:.2f} "
            f"psi={r['psi']:.2f}"
        )
        legend.set_visible(False)
        fig.canvas.draw_idle()

    def on_click(event):
        # Ignore clicks outside the plotting axes
        if event.inaxes != ax:
            return

        # Did the click hit one of the scatter points?
        contains, info = points.contains(event)

        if not contains:
            cmd.delete("rama_pick")
            annotation.set_visible(False)
            legend.set_visible(True)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("pick_event", on_pick)
    fig.canvas.mpl_connect("button_press_event", on_click)

    plt.tight_layout()
    plt.show()

cmd.extend("rama", rama)

