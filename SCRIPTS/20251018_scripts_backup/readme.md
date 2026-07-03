# Multi-Scenario Analysis for the VIC Model

This script (`post_analysis.py`) is designed to perform multi-scenario post-analysis of the Variable Infiltration Capacity (VIC) model outputs. It can analyze routed discharge, lake-specific data, and validate simulation results against observations.

All simulation results and routed outputs are expected to be in the `SCENARIOS` folder, organized into `OUTPUTS_<scenario_name>` and `OUTPUTS_ROUTED_<scenario_name>` directories.

---

## Directory Structure

The script assumes a specific directory structure for the VIC model project. The root folder should be organized as follows:

```
... Model Root folder/
    ├── FORCINGS/
    ├── GLOBALFILES/
    │   └── global_default.txt
    ├── INPUTS/
    │   └── withdrawals.txt
    ├── OUTPUTS/
    ├── OUTPUTS_ROUTED/
    ├── ROUTING_FILES/
    ├── SCENARIOS/
    │   ├── OUTPUTS_1/
    │   ├── OUTPUTS_2/
    │   ├── OUTPUTS_ROUTED_1/
    │   ├── OUTPUTS_ROUTED_2/
    │   ├── ...
    │   ├── FDC/
    │   ├── hydrographs/
    │   ├── lake_antpcp_scplot/
    │   ├── lake_boxplot/
    │   ├── lake_hydrology_timeseries/
    │   ├── lake_timeseries/
    │   ├── map/
    │   └── post_analysis.py
    ├── run_vic_commands.csh
    ├── Submit_VIC_Runs.csh
    ├── make_scenarios.py
    └── scenarios.csv
```

**Note:** The analysis output folders (`FDC`, `hydrographs`, etc.) will be created automatically inside the `SCENARIOS` directory if they do not exist.

---

## Usage

Execute the script from within the `SCENARIOS` directory.

```bash
python post_analysis.py [options]=[arguments]
```

### Analysis Condition Arguments

| Option | Argument | Description | Default |
| :--- | :--- | :--- | :--- |
| `-h`, `help` | | Shows the help and introduction block. | |
| `-r`, `route` | | Enables the routed discharge analysis. | `False` |
| `-l`, `lake` | | Enables the lake-specific grid analysis. | `False` |
| `1` or `0` | | `1` refreshes (clears) result folders; `0` does not. | `0` |
| `-l=` | `90001`</br>`90001,90002` | Specifies lake grid numbers for analysis. Use commas to separate multiple grids. | Uses `given_lakefilenames` from `post_analysis.py` |
| | `all` | Analyzes all lake grids defined in the soil file. | |
| `-ts=` | `number` | Sets the simulation timestep in hours (e.g., `3`, `24`). | `24` (or read from `OUT_STEP` in the default global file) |
| `-t=` | `YYYY-YYYY` | Sets the time of interest for the analysis. | Reads `STARTYEAR` + `SKIPYEAR` to `ENDYEAR` from the default global file. |
| `-target=` | `variable` | Sets the target variable for mapping in the lake analysis. Options include `OUT_RUNOFF`, `OUT_BASEFLOW`. | `veg_frac` |
| `-f=` | `num` or `range` | Sets the flow type for Flow Duration Curve (FDC) analysis. `1`: high, `2`: moist, `3`: mid, `4`: dry, `5`: low. A range like `1-3` can be used. | `0` (entire flow) |

### Trigger Type Arguments

| Option | Description | Default |
| :--- | :--- | :--- |
| `-g` | Enables growing season analysis for routed discharge. (*Currently under development*). | `False` |
| `-c` | Checks simulation results by reading `.err` and `.out` files from the `RUN_MESSAGES` directory. | `False` |
| `-v` | Validates routed discharge against observed data from the `OBSERVED` folder. This automatically enables the `-r` flag. | `False` |
| `-m` | Generates a map of the `-target` variable for lake grids across all scenarios. This automatically enables the `-l` flag. | `False` |

---

## Examples

**1. Validate Routed Discharge**
Validate the default routed discharge file against observed data for the years 2006-2015.
```bash
python post_analysis.py -v -t=2006-2015
```

**2. Run Both Route and Lake Analysis**
Perform both route and lake analysis using default settings. The analysis period will be determined from the default global file that is given.
```bash
python post_analysis.py -r -l
```

**3. Analyze a Specific Route File**
Analyze the specified routed discharge file, refreshing the results folders first.
```bash
python post_analysis.py 1 -r Wabash_03336000_discharge.txt
```

**4. Analyze a Specific Lake Grid**
Analyze the lake data for grid number `96044` without refreshing result folders.
```bash
python post_analysis.py 0 -l -l=96044
```

**5. Map Mean Annual Runoff**
Run routed discharge analysis and also generate a map of the mean annual `OUT_RUNOFF` for lake grids for the period 2006-2015.
```bash
python post_analysis.py -r -m -t=2006-2015 -target=OUT_RUNOFF
```

---
*This documentation was generated based on `post_analysis_variable.py`, created by DK @ 2025.*