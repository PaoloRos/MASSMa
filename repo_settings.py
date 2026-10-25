"""Shared plotting and export settings for MASSMa scripts and notebooks.

Importing this module does not configure Matplotlib or create directories.
"""

from pathlib import Path

GOLDEN_RATIO = (1 + 5 ** 0.5) / 2
FIGURE_WIDTH = 10  # inches
FIGURE_SIZE = (FIGURE_WIDTH, FIGURE_WIDTH / GOLDEN_RATIO)
OUTPUT_DPI = 200


def configure_plots(*, headless=False):
    """Apply shared defaults; call before importing pyplot for headless use.

    Leave the current backend unchanged unless headless=True is requested.
    Explicit figure sizes and save arguments can override these defaults.
    """
    import matplotlib

    if headless:
        matplotlib.use("Agg")
    matplotlib.rcParams.update({
        "figure.figsize": FIGURE_SIZE,
        "savefig.dpi": OUTPUT_DPI,
        "savefig.facecolor": "white",
        "savefig.bbox": None,
    })


def output_dir(base_dir):
    """Create and return the outputs directory under the supplied base path."""
    directory = Path(base_dir) / "outputs"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_figure(fig, path):
    """Save the full figure canvas at the shared DPI and return its Path.

    Preserve canvas proportions even if the caller enabled tight cropping.
    Closing the figure and reporting its location remain the caller's job.
    """
    import matplotlib

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with matplotlib.rc_context({"savefig.bbox": None}):
        fig.savefig(path, dpi=OUTPUT_DPI, facecolor="white", bbox_inches=None)
    return path
