# Multi-Agent Systems for Smart Machining
## ECIU's Course offered by INSA Tolouse

This repository contains several data analyses developed during the course mentioned in the title.

## Shared Python settings

`repo_settings.py` supplies consistent Matplotlib defaults: a 10-inch-wide
figure with a golden-ratio canvas, 200 DPI exports, and a white export background.
Importing the module alone has no plotting or filesystem side effects.

From the repository root:

```python
from pathlib import Path
from repo_settings import configure_plots, output_dir, save_figure

configure_plots()  # Preserve interactive display; call before importing pyplot.
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1])
path = save_figure(fig, output_dir(Path.cwd()) / "example.png")
plt.show()  # Or plt.close(fig) in an export-only script.
```

For scripts that only export figures, use `configure_plots(headless=True)`
before importing `matplotlib.pyplot`. Interactive notebooks should keep the
default `headless=False`. Calling the configuration function repeatedly is safe.

Scripts in subdirectories locate `repo_settings.py` by searching from their
own directory up through its parents. When `__file__` is unavailable, the same
bootstrap searches from the working directory; run interactive cells from
within the repository. See the setup cell in either root notebook for an example.

Pass the script or assignment directory to `output_dir(base_dir)` to keep
exports in its `outputs/` folder. `save_figure(fig, path)` creates missing parent
directories and returns the destination as a `Path`; it does not close the
figure or print a message. Display-only plots are not exported automatically.

Override the default canvas when needed, for example
`plt.subplots(2, 1, figsize=(10, 7))` for stacked plots. `FIGURE_SIZE`,
`FIGURE_WIDTH`, `GOLDEN_RATIO`, and `OUTPUT_DPI` are also available for import.
Use `fig.savefig(...)` directly for custom export settings; `save_figure` always
uses the shared DPI and full canvas, including when tight cropping was enabled
elsewhere. Avoid tight cropping when the exported golden ratio must be preserved.
