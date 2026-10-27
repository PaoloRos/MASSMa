# Outlines for AI

## AI commands

* the writing `[*italic*]` is strictly an ai command
* if something is inconsistence or not clear let me know in the `plan` phase!

## General formattig

* output must be a generated pdf, written in Latex
* Use title case
* text well formatted, mathematical symbols and formulas in Latex
* check wheter each plot as the same format, is consistent in formatting (eg power in kW), otherwise modify the code for figure generation and generate the new one (tell to me of this modification!)
* add a short description to each plot and table
* add reference of the each .py code to the file inside my repository on github. If are required, add other references to the repository
* put the [picture](../../unitn_logo.png) of the university at the first page, somewhere that is good
* Title: Assigmnment 1
* Subtitle: Multi Agent Systems for Smart Machining, ECIU Micro-Module
* "offered by INSA Tolouse"

## General approach

* focus on the result instead on the method and the analyses steps! ie: Don't spend too much words in explaining steps
* Be concise as possible: what metters are the tables, numbers and graphs. Shortest number of pages as possible

## [*Source material and background*]

* [Tasks](../README.md)
* [inspirational document](../turning_params.pdf)
* [Mathematical models 1](../../../1_intro_machining/Slides%201%20-%20%20Introduction%20%20-%20Smart%20Machining%20-%202025.pdf)
* [Mathematical models 2: specific to drilling](../../../1_intro_machining/formulas-and-deinitions-for-drilling-metric-enu.pdf)

## AI-usage

Put a session, clearly visible (maiby of a different color), explaining the ai usage: ai used to generate only code, material and the report too.

But the approach, analysis decisions were of the author.

Ai as co-author -> put the model.

This section must be really short!


## Turning Process

[*What's follows really briefly*]

* show parameters
* explain two machining modes
* measured cutting power calculated as $P_c = P_m - P_nc$, where P_m is the machining recorded power, while P_nc the one of air cutting

### Task 1&2: cutting power prediction

* In prediction of timings the full engagement of the tool was considered. The engagement was neglected, because of the purpose of the assigment isn't so much relavant

* **Conclusions regarding the two different machining modes** (constant Vc or constant N):

  - **Constant Vc**: allows to preserve a constant Pc, while N increases as the diameter decreases
  - **constant N**: vc and Pc decrease as the diameter decrease

* **Comparison**:

  - even the noisy trace of cutting power, the offline filtering isn't necessary: averaging Pc value for each pass is enough to find a proper estimator: in fact the calculated averages are similar to the predictex values, with a deviation o less then 5% for vc constant and less then 10% for n constant.
  - Pass windows were selected as continuous intervals with $P_c > 500\,\mathrm{W}$ lasting at least $2\,\mathrm{s}$; for constant N, a short centered median filter (about $0.10\,\mathrm{s}$) was used only for detection. Mean and standard deviation were calculated from the raw samples within each window, without additional entry/exit trimming. So allowing to bound the effect of transition and transition peaks
  - [show tables and plots]: [comparison at vc](../outputs/power_comparison_constant_vc.csv), [comparison at n](../outputs/power_comparison_constant_n.csv), [plot at vc]

### Task 3: estimation of Kc

#### Constant vc

* For constatn vc a filtering stage is required. Qualitative and iterative criterion was followed:
  ```
  Number of samples selection:
    extract the shortest cutting window
    samples in that window: Nextr = textr/Ts
    number of samples for MA window as a fraction of Nextr
  ```
  - [*skipping the filtering steps*] MA window of 55 samples

* **Retained Windows for Kc at Constant Vc**:

  - Detect entries and exits at $1000\,\mathrm{W}$ on the same short median-filtered signal (detection only); discard intervals shorter than $2\,\mathrm{s}$ and pair passes with the prediction CSV in order.
  - Nominal windows end at $t_{\mathrm{start},i}+\mathrm{duration}_{i,\mathrm{CSV}}$. For Kc, stop at the earlier of this nominal end and the detected exit to avoid post-cut idle-subtraction transients.
  - Trim half the centered moving-average support from both boundaries so all samples contributing to Kc lie inside the cut. No Kc-based outlier removal is applied.
  - In the plot: orange dashed outlines indicate nominal CSV windows; blue shading indicates samples retained for Kc.

* [*show plot*] [kc at vc](../outputs/kc_windows_constant_vc.png)

* Kc calculation:
  - for each sample:
  $$
    K_c[i] = \frac{60\,P_c[i]}{v_c\,f\,a_p}.
  $$
  - calculate average and sd for each pass
  - [*show table*](../outputs/kc_constant_vc.csv)


#### Constant n

* even the high variance of power for each pass, the measurements donßt present outlier peaks for each pass, therefore no filter was applied

* **Retained Windows for Kc at Constant N**:
  - Read pass duration, diameter and cutting speed from `prediction_parameters_constant_n.csv`. Nominal windows start at measured entries and last the predicted duration ($10\,\mathrm{s}$), preserving non-cutting gaps.
  - Detect entries/exits using a $0.10\,\mathrm{s}$ median (detection only), a $500\,\mathrm{W}$ threshold and a $2\,\mathrm{s}$ minimum duration, as in `power_comparison_TP.py`; a $1000\,\mathrm{W}$ threshold would miss late passes as power decreases. Cap each nominal window at the detected exit to exclude return moves.
  - Calculate Kc from raw, idle-subtracted power within these windows, without moving-average filtering, transition margins, clipping or outlier removal. Averaging reduces random noise but does not remove systematic bias.

* [*show plot*] [kc at vc](../outputs/kc_windows_constant_n.png)

* Calculation of Kc (same of the previous one):
  - [*show table*](../outputs/kc_constant_n.csv)

*   - conclude with the estimation of mean values for both cases

## Drilling process

* describe the tasks 3&4 on the bases of what written in the [power prediction in DP file](../local_scratch/power_prediction_DP.ipynb).

* Emphatize the conclusions on prediction:

  - [*show*] [plot](../outputs/prediction_power_vs_time_drilling.png) and [*if necessary*] [parameters](../outputs/pre_drilling_drilling_parameters.csv)
  - transition of power until the tool si fully engaged
  - change of cutting power when the pilot bottom is reached
