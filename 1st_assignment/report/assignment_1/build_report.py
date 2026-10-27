"""Regenerate the assignment results, checked tables and final LaTeX PDF."""

from pathlib import Path
import os
import shutil
import subprocess
import sys


def main():
    project = Path(__file__).resolve().parent
    assignment = project.parents[1]
    build = project / "build"
    build.mkdir(exist_ok=True)
    environment = os.environ.copy()
    environment.setdefault("MPLCONFIGDIR", str(build / "matplotlib"))
    latexmk = shutil.which("latexmk")
    if latexmk is None:
        raise SystemExit("latexmk is required to export the PDF. Install or activate TeX Live/MacTeX.")
    for filename in [
        "power_prediction_TP.py",
        "power_comparison_TP.py",
        "kc_estimation_TP.py",
        "power_prediction_DP.py",
    ]:
        subprocess.run([sys.executable, str(assignment / filename)], cwd=assignment,
                       env=environment, check=True)
    subprocess.run([sys.executable, str(project / "prepare_report.py")],
                   cwd=project, env=environment, check=True)
    subprocess.run([
        latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error",
        "-jobname=assignment_1", f"-outdir={build}", "main.tex",
    ], cwd=project, env=environment, check=True)
    destination = project / "assignment_1.pdf"
    shutil.copy2(build / "assignment_1.pdf", destination)
    print(f"Report saved: {destination}")


if __name__ == "__main__":
    main()
