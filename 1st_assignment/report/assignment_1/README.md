# Assignment 1 Report

main.tex is the editable source; assignment_1.pdf is the compiled report.
The report may extend to seven pages. Conclusions form a separate numbered
section on their own page; body text, references and the AI-use statement use
the normal text size, without compression to enforce a six-page limit.
The images/ folder contains copies of the university logo and the five included
figures, making this LaTeX project self-contained for compilation. Preparation
refreshes these copies from the repository logo and 1st_assignment/outputs/.

Numbered citations link to the bibliography; result references link to the
corresponding figures and tables. The chapter title links to its GitHub PDF.
The course slides are bundled in sources/ and linked as a local PDF, since they
are outside this GitHub repository.

From the repository root, rebuild with:

    .venv/bin/python 1st_assignment/report/assignment_1/build_report.py

The build needs the repository Python environment (NumPy, pandas and Matplotlib)
and TeX Live/MacTeX with latexmk and pdflatex. It regenerates the four analysis
scripts' outputs, runs prepare_report.py to check the data and generate LaTeX
tables, then compiles and exports the PDF. The report date is refreshed in the
Europe/Rome timezone. Intermediate compiler files stay in the ignored build/
directory.

generated/evidence.json records timing calculations, per-pass durations and the
reported summary values. prepare_report.py checks pass pairing, stored statistics,
turning formulas and the transfer of the final constant-N pass to drilling.
Generated power tables display kW; the source CSVs retain watts.

Only the displayed units of the two standalone turning prediction plots were
changed from W to kW. Numerical predictions and the analysis methods are preserved.
