from datetime import datetime
from functools import lru_cache
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import Divider, Size
import random
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams.update({'font.size': 12}) # or any other desired size in points
# plt.rcParams['lines.linewidth'] = 1.0 
import warnings
warnings.filterwarnings('ignore')

"""

"""


def _scenario_name(scenario):
    return scenario.replace('OUTPUTS_ROUTED_', '').replace('_sub', '')


def _routed_name(scenario):
    return scenario.replace('OUTPUTS_ROUTED_', '')


def _print_stat_block(scale_name, r_squared, nse, pbias, r2_thresholds, nse_thresholds, pbias_thresholds):
    def grade_high(value, thresholds):
        if value > thresholds[0]:
            return 'Very Good'
        if value > thresholds[1]:
            return 'Good'
        if value > thresholds[2]:
            return 'Satisfactory'
        return 'Unsatisfactory'

    def grade_low(value, thresholds):
        if value < thresholds[0]:
            return 'Very Good'
        if value < thresholds[1]:
            return 'Good'
        if value < thresholds[2]:
            return 'Satisfactory'
        return 'Unsatisfactory'

    print(f'          {scale_name:>25} | {"Value":>10} | Measure')
    print(f'          {"-"*25} | {"-"*10} | {"-"*10}')
    print(f'          {"R-squared":>25} | {round(r_squared, 2):>10} | {grade_high(r_squared, r2_thresholds)}')
    print(f'          {"NSE":>25} | {round(nse, 2):>10} | {grade_high(nse, nse_thresholds)}')
    print(f'          {"P-Bias (%)":>25} | {round(pbias, 2):>10} | {grade_low(abs(pbias), pbias_thresholds)}')
    print(f'          {"-"*25}   {"-"*10}   {"-"*10}')


def _save_figure(output_path, dpi=600):
    plt.savefig(output_path, dpi=dpi)
    plt.close()
    return True


def _scenario_display_name(scenario):
    return scenario.replace('OUTPUTS_ROUTED_', '').replace('_sub', '')


def _scenario_output_name(scenario):
    return scenario.replace('OUTPUTS_ROUTED_', '')


def _flow_type_name(flowtype):
    if isinstance(flowtype, list):
        if not flowtype or flowtype == [0]:
            return 'Discharge'
        flowtype = flowtype[0]
    return {
        1: 'High-Flow',
        2: 'Moist-Condition',
        3: 'Mid-Flow',
        4: 'Dry-Condition',
        5: 'Low-Flow',
    }.get(flowtype, 'Discharge')


def _flow_plot_title(flowtype, time_frame, growing_season, criteria):
    title = _flow_type_name(flowtype)
    if time_frame == 'Y':
        title = f'Annual {criteria.capitalize()} {title}'
    elif time_frame == 'Y-M':
        title = f'Monthly {criteria.capitalize()} {title}'
    if growing_season:
        title = f'{title} (Growing Season)'
    return title


def _flow_range_from_flowtype(flowtype, flow_criteria):
    if flowtype == [0]:
        return [999999, 0]
    if len(flowtype) == 2:
        return [flow_criteria[flowtype[0]-1], flow_criteria[flowtype[1]]]
    return [flow_criteria[flowtype[0]-1], flow_criteria[flowtype[0]]]


def _discharge_axis_label(name):
    return f'{name} Discharge ('+r"$m^3$"+'/sec)'


def _configure_discharge_axes(x_label, y_label):
    plt.xlabel(x_label)
    plt.gca().get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.ylabel(y_label)
    plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))


def _build_validation_plot_path(routefilename, scenario, suffix):
    return f'./discharge_validation/{routefilename[:-4]}/{suffix}_{_scenario_output_name(scenario)}.png'


def _build_compare_plot_path(routefilename, scenario, growing_season, time_frame, flowtype, criteria):
    return f'./discharge_compare/{routefilename[:-4]}/discharge_compare_g-{growing_season}_{time_frame}_f{flowtype}_{criteria}_{_scenario_output_name(scenario)}.png'


def get_scenarios(scelist0):
    """_summary_
    this function will automatically get the list of scenarios in the current 'SCENARIOS' directory
    Returns:
        scelist (list): this is the list of scenarios in the current directory in string format
    """
    return ['OUTPUTS_ROUTED_' + scenario_name for scenario_name in scelist0]


def folder_setup(routefilename, refresher):
    from shutil import rmtree
    """_summary_
    this function is used to set up the folders for the lake analysis

    Args:
        routefilename (str): the filename of the routed output file. file extension should be '.txt'
        refresher (bool): if True, it will refresh the folder by removing the existing folder and creating a new one. if False, it will keep the existing folder.
        
    Returns:
        None
    """
    routefilename = routefilename[:-4]
    print('\n\n>>> Setting up folders for the analysis for the route: '+routefilename)
    # make the folders for the lake analysis
    access = 0o777
    
    if not os.path.exists('./discharge_validation/'):
        print('   ... Creating folders for Discharge validation')
        os.mkdir('./discharge_validation/', access)
    if not os.path.exists('./FDC/'):
        print('   ... Creating folders for FDC analysis')
        os.mkdir('./FDC/', access)
    if not os.path.exists('./hydrographs/'):
        print('   ... Creating folders for hydrographs analysis')
        os.mkdir('./hydrographs/', access)
    if not os.path.exists('./discharge_compare/'):
        print('   ... Creating folders for discharge_compare analysis')
        os.mkdir('./discharge_compare/', access)
    
    
    if not os.path.exists('./discharge_validation/'+routefilename):
        print('   ... Creating folders for Discharge validation')
        os.mkdir('./discharge_validation/'+routefilename, access)
    elif refresher == True:
        rmtree('./discharge_validation/'+routefilename)
        os.mkdir('./discharge_validation/'+routefilename, access)
        print('   ... Discharge validation Directory refreshed')
    else:
        print('   ... Discharge validation Directory already exists')

    if not os.path.exists('./FDC/'+routefilename):
        print('   ... Creating folders for FDC analysis')
        os.mkdir('./FDC/'+routefilename, access)
    elif refresher == True:
        rmtree('./FDC/'+routefilename)
        os.mkdir('./FDC/'+routefilename, access)
        print('   ... FDC Directory refreshed')
    else:
        print('   ... FDC Directory already exists')

    if not os.path.exists('./hydrographs/'+routefilename):
        print('   ... Creating folders for hydrographs analysis')
        os.mkdir('./hydrographs/'+routefilename, access)
    elif refresher == True:
        rmtree('./hydrographs/'+routefilename)
        os.mkdir('./hydrographs/'+routefilename, access)
        print('   ... hydrographs Directory refreshed')
    else:
        print('   ... hydrographs Directory already exists')

    if not os.path.exists('./discharge_compare/'+routefilename):
        print('   ... Creating folders for discharge_compare analysis')
        os.mkdir('./discharge_compare/'+routefilename, access)
    elif refresher == True:
        rmtree('./discharge_compare/'+routefilename)
        os.mkdir('./discharge_compare/'+routefilename, access)
        print('   ... Discharge_compare Directory refreshed')
    else:
        print('   ... Discharge_compare Directory already exists')




def sim_vali(scelist, routefilename, styear, endyear, default_scenario, ts):
    """_summary_
    1. this function will validate the simulation by comparing the flow values from the routed output files with the observed flow values
    2. this function requires subfunction read_rte to read the routed output files
    3. and it will save the validation graph in the 'discharge_validation' folder with the folder name of given routefilename
    4. this function will plot the scatter plot between the observed and simulated flow values
    5. and the timeseries of the observed and simulated flow values
    Args:
        scelist (_list_): list of scenarios in the current directory
        routefilename (_str_): the filename of the routed output file. file extension should be '.txt', default name is given in the 'post_analysis.py' script
        styear (_int_): starting year of the data, given from upper class
        endyear (_int_): ending year of the data, given from upper class
        default_scenario (str): the default scenario to plot the flow comparison for comparison. Defaults from post_analysis.py script.
        ts (int): the time step of the output data (hours)
    """

    print(f'\n\n>>> Validation simulated discharge using observed discharge dataset: {routefilename}')
    # this function will validate the simulation by comparfing the flow values from the routed output files with the observed flow values
    # read the routed output files as dataframe format, first line is the header
    # the observation data should be downloaded from USGS website directly
    obslines = pd.read_csv(os.path.join('../','OBSERVED',routefilename),sep='\t', comment='#', header=None, names=['Agency', 'Site', 'Date', 'Observed', 'Discharge_cd'])[2:]
    # print(obslines.head())
    # change 'Observed' column to float
    obslines['Observed'] = obslines['Observed'].astype(float)
    # drop Agency, site, Discharge_cd columns
    obslines = obslines.drop(columns=['Agency', 'Site', 'Discharge_cd'])
    obslines['Date'] = pd.to_datetime(obslines['Date'])
    # convert the 'Observed' from cfs to cms multiply by 0.02831683199881
    obslines['Observed'] = obslines['Observed'] * 0.02831683199881

    # filter the obslines with the styear and endyear
    obslines = obslines[(obslines['Date'].dt.year >= styear) & (obslines['Date'].dt.year <= endyear)]

    for scenario in scelist:
        if default_scenario in scenario:
            scenario_label = _scenario_display_name(scenario)
            # read the observed flow values from the routed output files
            flines = _read_rte(scenario, routefilename, styear, endyear, ts, type=1)

            # merge the two dataframes on the Date column to the flines dataframe
            flines = pd.merge(flines, obslines, on='Date', how='left')
            # drop the NA rows
            flines = flines.dropna()
            # if there is values with '-nan' or 'inf', drop those rows
            flines = flines.replace([np.inf, -np.inf], np.nan).dropna(subset=['Discharge', 'Observed'])
            # plot the scatter plot between the observed and simulated flow values
            plt.figure(figsize=(5,5))
            # plt.scatter(flines['Observed'], flines['Discharge'], label=scenario.replace('OUTPUTS_ROUTED_', ''), color='grey', edgecolors='black', s=15, zorder=2)
            plt.scatter(flines['Observed'], flines['Discharge'], color='grey', edgecolors='black', s=15, zorder=2, label='Discharge')
            
            # plot the y=x line
            plt.axline((0, 0), slope=1, color='limegreen', linestyle='dashdot', linewidth=0.75, zorder=2, label='1:1 Line')

            # add linear regression line (infinite) of the scatter plot
            m, b = np.polyfit(flines['Observed'], flines['Discharge'], 1)
            # draw an infinite line using the slope and intercept of the linear regression line
            plt.axline((0, b), slope=m, color='r', linestyle='--', linewidth=0.75, zorder=2, label='Linear Regression')
            _configure_discharge_axes('Observed Discharge ('+r"$m^3$"+'/sec)', 'Simulated Discharge ('+r"$m^3$"+'/sec)')
            # print (scenario, max(flines['Observed']), max(flines['Discharge']))
            plt.xlim(0, max(max(flines['Observed']), max(flines['Discharge']))*1.02)
            plt.ylim(0, max(max(flines['Observed']), max(flines['Discharge']))*1.02)
            plt.grid()
            plt.title(f'{scenario_label} Discharge Validation')
            plt.legend(['Discharge', '1:1 Line'])
            plt.tight_layout()
            if _save_figure(_build_validation_plot_path(routefilename, scenario, 'sim_vali')):
                print(f'   ... simulation validation graph for {scenario_label} saved')

            # plot the timeseries of the observed and simulated flow values
            plt.figure(figsize=(10,5))
            plt.plot(flines['Date'], flines['Observed'], label='Observed', color='black', linestyle='--', linewidth=0.5)
            plt.plot(flines['Date'], flines['Discharge'], label=scenario_label, color='r', alpha=0.5, linewidth=0.5)
            plt.xlabel('Date')
            plt.xticks(rotation=30)
            plt.ylabel('Discharge ('+r"$m^3$"+'/sec)')
            plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
            plt.grid()
            plt.title(f'{scenario_label} Discharge Validation')
            plt.legend(['Observed', scenario_label])
            plt.tight_layout()
            _save_figure(_build_validation_plot_path(routefilename, scenario, 'sim_vali_timeseries'))


            corr, r_squared, nse, pbias, rmse, mae, mape, kge = _vali_func(flines)
            _print_stat_block('Daily scale Stat', r_squared, nse, pbias, (0.85, 0.70, 0.50), (0.80, 0.70, 0.50), (5.0, 10.0, 25.0))
            print()


            # Conduct statistical analysis for the observed and simulated flow values in monthly scale
            # convert flines to year-monthly average and make a new dataframe
            flines['Year-Month'] = flines['Date'].dt.to_period('M')
            # deepcopy flines to monthly_flines
            monthly_flines = flines.copy()
            # drop the date column
            monthly_flines = monthly_flines.drop(columns=['Date'])
            monthly_flines = monthly_flines.groupby('Year-Month').sum()
            # TODO: should be SUM instead of mean for the discharge values

            corr, r_squared, nse, pbias, rmse, mae, mape, kge = _vali_func(monthly_flines)
            _print_stat_block('Monthly scale Stat', r_squared, nse, pbias, (0.85, 0.80, 0.70), (0.85, 0.70, 0.55), (3.0, 10.0, 15.0))
            print(f'{"Moriasi et al., 2015":>65}\n')


def _vali_func(flines):
    """_summary_
    this function will conduct statistical analysis for the observed and simulated flow values
    any hydrology model validation standards can be found here: https://swat.tamu.edu/media/90109/moriasimodeleval.pdf, https://web.ics.purdue.edu/~mgitau/pdf/Moriasi%20et%20al%202015.pdf

    Args:
        observed (list): list of observed flow values
        simulated (list): list of simulated flow values
    Returns:
        corr (float): correlation coefficient between the observed and simulated flow values
        r_squared (float): R-squared value between the observed and simulated flow values
        nse (float): NSE between the observed and simulated flow values
        pbias (float): P-Bias between the observed and simulated flow values
        rmse (float): RMSE between the observed and simulated flow values
        mae (float): MAE between the observed and simulated flow values
        mape (float): MAPE between the observed and simulated flow values
        kge (float): KGE between the observed and simulated flow values
    """
    # print the correlation coefficient between the observed and simulated flow values
    corr = flines['Observed'].corr(flines['Discharge'])
    # print the R-squared value between the observed and simulated flow values
    r_squared = corr ** 2
    # print the NSE between the observed and simulated flow values
    nse = 1 - (np.sum((flines['Observed'] - flines['Discharge']) ** 2) / np.sum((flines['Observed'] - flines['Observed'].mean()) ** 2))
    # print the P-Bias between the observed and simulated flow values
    pbias = 100 * (flines['Discharge'].sum() - flines['Observed'].sum()) / flines['Observed'].sum()
    # print the RMSE between the observed and simulated flow values
    rmse = np.sqrt(((flines['Observed'] - flines['Discharge']) ** 2).mean())
    # print the MAE between the observed and simulated flow values
    mae = (abs(flines['Observed'] - flines['Discharge'])).mean()
    # print the MAPE between the observed and simulated flow values
    mape = (abs(flines['Observed'] - flines['Discharge']) / flines['Observed']).mean()
    # print the KGE between the observed and simulated flow values
    kge = 1 - np.sqrt((corr - 1) ** 2 + (rmse / flines['Observed'].mean() - 1) ** 2 + (flines['Discharge'].mean() / flines['Observed'].mean() - 1) ** 2)

    return corr, r_squared, nse, pbias, rmse, mae, mape, kge


def water_balance_check(scelist, routefilename, styear, endyear, ts):
    

    print('\n>>> Water Balance Check from the individual output files')
    # from the default scenario, read the individual fluxes_ files.
    default_scenario = scelist[0].replace('ROUTED_','')
    fluxes_filelist = [flux for flux in os.listdir(default_scenario) if flux.startswith('fluxes_')]
    # sort the fluxes_filelist
    fluxes_filelist.sort()
    
    import post_analysis_lake as pal
    out_prec_sum = 0
    out_evap_sum = 0
    out_runoff_sum = 0
    out_baseflow_sum = 0
    filecount = 0 # for progress bar
    sample_flux = random.sample(fluxes_filelist, min(20, len(fluxes_filelist)))
    for flux in sample_flux:
        # read the individual flux file with pandas and get sum of OUT_RUNOFF and OUT_BASEFLOW
        df = pd.read_csv(os.path.join(default_scenario, flux), delim_whitespace=True, skiprows=5, header=0)
        # remove first one from the header list and make it as column header
        header_list = df.columns.tolist()
        # drop the last column
        df = df.iloc[:, :-1]
        df.columns = header_list[1:]
        # make the 'Date' column from 'YEAR', 'Month', 'DAY' columns
        df['Date'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
        # filter the dataframe with styear and endyear for water year using date column
        df = df[(df['Date'] >= pd.Timestamp(f'{styear}-10-01')) & (df['Date'] <= pd.Timestamp(f'{endyear}-09-30'))]

        out_prec = df['OUT_PREC'].sum()
        out_prec_sum += out_prec
        out_evap = df['OUT_EVAP'].sum()
        out_evap_sum += out_evap
        out_runoff = df['OUT_RUNOFF'].sum()
        out_runoff_sum += out_runoff
        out_baseflow = df['OUT_BASEFLOW'].sum()
        out_baseflow_sum += out_baseflow
        filecount += 1
        _printProgressBar(filecount, len(sample_flux), prefix = 'Reading:')

        output_path = f'./discharge_validation/{routefilename[:-4]}/soil_moisture_profile_{flux[:-4]}.png'
        if os.path.exists(output_path):
            continue

        # make figure with three rows and one column subplots
        fig, axs = plt.subplots(3, 1, figsize=(10, 5), sharex=True)
        axs[0].plot(df['Date'], df['OUT_SOIL_MOIST_0'], label='OUT_SOIL_MOIST_0', color='blue', lw=0.5)
        axs[0].set_ylabel('Soil Moisture 0 (mm)')
        axs[0].grid()
        axs[1].plot(df['Date'], df['OUT_SOIL_MOIST_1'], label='OUT_SOIL_MOIST_1', color='orange', lw=0.5)
        axs[1].set_ylabel('Soil Moisture 1 (mm)')
        axs[1].grid()
        axs[2].plot(df['Date'], df['OUT_SOIL_MOIST_2'], label='OUT_SOIL_MOIST_2', color='green', lw=0.5)
        axs[2].set_ylabel('Soil Moisture 2 (mm)')
        axs[2].set_xlabel('Date')
        axs[2].grid()
        plt.suptitle(f'Soil Moisture Profile - {flux}')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        _save_figure(output_path)

    # propose the total out_runoff_sum, out_baseflow_sum and their ratio
    total_outflow = out_runoff_sum + out_baseflow_sum
    print(f'\n   ... Total OUT_PREC: {out_prec:.2f} mm')
    print(f'       Total OUT_EVAP: {out_evap:.2f} mm (out_evap/out_prec: {out_evap/out_prec*100:.2f}%)')
    print(f'       OUT_RUNOFF Total Sum: {out_runoff_sum:.2f} mm (out_runoff/out_prec: {out_runoff_sum/out_prec*100:.2f}%)')
    print(f'   ... OUT_BASEFLOW Total Sum: {out_baseflow_sum:.2f} mm (out_baseflow/out_prec: {out_baseflow_sum/out_prec*100:.2f}%)')
    print(f'       OUT_RUNOFF Ratio: {out_runoff_sum / total_outflow * 100:.2f}%, OUT_BASEFLOW Ratio: {out_baseflow_sum / total_outflow * 100:.2f}%')





def get_FDC(default_scenario, scelist, routefilename, styear, endyear, ts, flowtype):
    """_summary_
    this function returns the FDC from the routed output files
    this function will plot the all of the FDC graph for each scenario and save it in the FDC folder with the folder name of given routefilename
    this function requires subfunction return_FDC to get the FDC from the routed output files and setup_fig to set up the figure for the FDC

    Args:
        default_scenario (str): the default scenario to plot the FDC for comparison
        scelist (_list_): the list of scenarios in the current directory
        routefilename (_str_): the filename of the routed output file. file extension should be '.txt'
        default_scenario (str, optional): the default scenario to plot the FDC for comparison. Defaults to 'OUTPUTS_ROUTED_base'.
        styear (_int_): the starting year of the FDC
        endyear (_int_): the ending year of the FDC
        ts (int): the time step of the output data (hours)
        flowtype (list): the list of flow types to plot the FDC. if flowtype is [0], it will plot the FDC for all flow types. if flowtype is [1,2], it will plot the FDC for 10% and 40% exceedance probability
    Returns:
        None
    """

    print('\n\n>>> Getting FDC from the routed output files')
    # set up the figure for the FDC
    _setup_FDC_fig()
    # print(scelist)
    print('    Scenario, flow criteria')

    for scenario in scelist:
        # skip if the routefilename does not exist in the scenario folder
        # get the FDC from the routed output files
        scenario_label = _scenario_display_name(scenario)
        list_FDC, flow_criteria = _return_FDC(scenario, routefilename, styear, endyear, ts)
        flow_criteria.insert(0, 999999) # add the max value to the first element
        flow_criteria.append(0) # add the min value to the last element

        flow_range = _flow_range_from_flowtype(flowtype, flow_criteria)
        # filter the list_FDC based on the flow_range
        temp_FDC = [[],[]]
        for i in range(len(list_FDC[0])):
            if list_FDC[1][i] <= flow_range[0] and list_FDC[1][i] >= flow_range[1]:
                temp_FDC[0].append(list_FDC[0][i])
                temp_FDC[1].append(list_FDC[1][i])
        # list_FDC, flow_criteria = return_FDC(scenario, routefilename, styear, endyear, ts)

        # plot list_FDC to the plot
        # print (scenario.replace('OUTPUTS_ROUTED_', ''), flow_criteria)
        if scenario.replace('OUTPUTS_ROUTED_', '') == default_scenario:
            plt.plot(temp_FDC[0], temp_FDC[1], label=scenario_label, color='black', linestyle='--', linewidth=1)
        else:
            plt.plot(temp_FDC[0], temp_FDC[1], label=scenario_label, linewidth=1)

    FDC_ticks = [0,10,40,60,90,100]
    if flowtype == [0]:
        plt.xlim(0,100)
    elif len(flowtype) == 2:
        plt.xlim(FDC_ticks[flowtype[0]-1], FDC_ticks[flowtype[1]])
        # plt.ylim( flow_range[1]*0.95, flow_range[0]*1.05)
    else:
        plt.xlim(FDC_ticks[flowtype[0]-1], FDC_ticks[flowtype[0]])
        # plt.ylim(flow_range[1]*0.95, flow_range[0]*1.05)

    flowtypename = '-'.join([str(ft) for ft in flowtype]) if flowtype != [0] else 'All'
    
    plt.legend()
    if _save_figure(f'./FDC/{routefilename[:-4]}/FDC_graph_{flowtypename}.png'):
        print('   ... FDC graph saved')

    return None


def _return_FDC(scenario,routefilename, styear, endyear, ts):
    """_summary_
    this is subfunction of get_FDC
    this function returns the FDC from the routed output files

    Args:
        scenario (_str_): the name of the scenario (folder name)
        routefilename (_str_): the filename of the routed output file. file extension should be '.txt'
        styear (_int_): the starting year of the FDC, given from upper class
        endyear (_int_): the ending year of the FDC. given from upper class

    Returns:
        exist (list): the list of exceedance probability
        FDC (list): the list of flow values corresponding to the exceedance probability
        flow_criteria (list): the list of flow values for 10%, 40%, 60%, and 90% exceedance probability
    
    # Sort the discharge data in descending order
    sorted_discharge = df['discharge'].sort_values(ascending=False).reset_index(drop=True)
    # Calculate exceedance probabilities
    exceedance_probabilities = [(i + 1) / (len(sorted_discharge) + 1) * 100 for i in range(len(sorted_discharge))]
    plt.plot(exceedance_probabilities, sorted_discharge, label='Flow Duration Curve')
    
    """
    # get the list of routed output files
    # read the file
    flines = _read_rte(scenario, routefilename, styear, endyear, ts)

    flow_values = np.asarray([line[1] for line in flines], dtype=float)

    unique_flows, counts = np.unique(flow_values, return_counts=True)
    order = np.argsort(unique_flows)[::-1]

    FDC = unique_flows[order]
    exist = np.cumsum(counts[order]) / len(flow_values) * 100

    #	Check the 10%, 40%, 60%, and 90% flow value
    flow_criteria = []
    for target in [10, 40, 60, 90]:
        nearest_index = int(np.argmin(np.abs(exist - target)))
        flow_criteria.append(float(round(FDC[nearest_index], 3)))
    print (f'      {scenario}, {flow_criteria[0]}, {flow_criteria[1]}, {flow_criteria[2]}, {flow_criteria[3]}')

    # print(scenario, flow_criteria)
    return [exist, FDC], flow_criteria


def _setup_FDC_fig():
    # set up the figure for the FDC
    plt.figure(figsize=(8,4))

    # set the title
    plt.title('Flow Duration Curve')

    # set the x-axis
    plt.xlabel("Flow Exceedance(%)")
    plt.xlim(0,100)
    plt.xticks([0,10,40,60,90,100])

    # set the y-axis
    plt.yscale('log')
    # plt.ylim(0,10000)
    plt.ylabel('Discharge ('+r"$m^3$"+'/sec)')
    # plt.yticks([10,100,1000,10000])
    
    # set the grid
    plt.grid(zorder=0)




def hydrograph_plot(scelist, routefilename, styear, endyear, default_scenario, ts, peak_number=200):
    """_summary_
    this function will plot the hydrograph for each peakflow event from the routed output files for all scenarios in one plot per event
    this function requires subfunction read_rte to read the routed output files
    and it will save the hydrograph in the 'hydrographs' folder with the folder name of given routefilename
    this function is designed to conduct cross correlation analysis for the peakflow events

    Args:
        scelist (list): list of scenarios in the current directory
        routefilename (str): the filename of the routed output file. file extension should be '.txt'
        default_scenario (str, optional): the default scenario to plot the hydrograph for comparison. Defaults to 'OUTPUTS_ROUTED_base'.
        peak_number (int, optional): number of peak flow events to plot. Defaults to 200.

    Returns:
        None
    """

    # this function will choose the top peak flow from the timeseries of the flow and plot individual hydrograph
    print('\n\n>>> Conducting hydrograph analysis')

    # from the default scenario, read the flow timeseries
    flines = _read_rte(f'OUTPUTS_ROUTED_{default_scenario}', routefilename, styear, endyear, ts, type=1)
    cache_flines = {}
    for sce in scelist:
        cache_flines[sce] = _read_rte(sce, routefilename, styear, endyear, ts, type=1)

    peakflows = flines.nlargest(peak_number, 'Discharge')
    # sort the values by the date
    peakflows.sort_values('Date', inplace=True)
    # if the diff of the date is less than 7 days, remove the later one
    peakflows = peakflows[peakflows['Date'].diff() > pd.Timedelta(days=7)]
    print(f'   ... Peak flow event #: {len(peakflows)}')
    # extract the dates from the maxflows
    peakdates = peakflows['Date']

    # for each date in the peakdates, plot the hydrograph for each scenario
    for  peakdate in peakdates:
        peakflowvals = []
        fig = plt.figure(figsize=(6,5))
        # The first & third items are for padding and the second items are for the axes
        h = [Size.Fixed(1.0), Size.Scaled(1.), Size.Fixed(.5)]
        v = [Size.Fixed(1.0), Size.Scaled(1.), Size.Fixed(.2)]
        
        divider = Divider(fig, (0, 0, 1, 1), h, v, aspect=False)
        ax  = fig.add_axes(divider.get_position(), axes_locator=divider.new_locator(nx=1, ny=1))
        for scenario in scelist:
            # read the flow timeseries for each scenario
            flines = cache_flines[scenario]
            # extract the Discharge values from 5 days ago to 5 days later of the peakdate
            peakflowvals = flines[(flines['Date'] >= peakdate - pd.Timedelta(days=7)) & (flines['Date'] <= peakdate + pd.Timedelta(days=7))]
            if scenario == f'OUTPUTS_ROUTED_{default_scenario}':
                ax.plot(peakflowvals['Date'], peakflowvals['Discharge'], label=scenario[15:].replace('_sub',''), color='black', linestyle='--', linewidth=1.25)
            else:
                ax.plot(peakflowvals['Date'], peakflowvals['Discharge'], linewidth=1.25)
        
        plt.xlabel('Date')
        # make x-tick label as mm/dd/yyyy format
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        # make x-tick label interval of 3 days
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=3))
        # rotate the x-axis tick labels
        plt.xticks(rotation=20)
        # put comma in the y-axis
        plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        plt.ylabel('Discharge ('+r"$m^3$"+'/sec)')
        plt.legend([sce[15:].replace('_sub','') for sce in scelist])
        # make the grid line in light grey color
        plt.grid(color='lightgrey', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        if _save_figure(f'./hydrographs/{routefilename[:-4]}/hydrograph_{str(peakdate)[:10]}.png'):
            print(f'   ... hydrograph for {str(peakdate)[:10]} saved')

    xcorr(scelist, routefilename, peakdates, styear, endyear, default_scenario, ts)

    return None




def xcorr(scelist, routefilename, peakdates, styear, endyear, dafault_scenario, ts):

    from scipy import signal

    print('\n\n>>> Discharge cross-correlation analysis')
    
    # read the default scenario flow timeseries
    default_flines = _read_rte(f'OUTPUTS_ROUTED_{dafault_scenario}', routefilename, styear, endyear, ts, type=1)
    scenario_flines = {
        scenario: _read_rte(scenario, routefilename, styear, endyear, ts, type=1)
        for scenario in scelist
        if scenario != f'OUTPUTS_ROUTED_{dafault_scenario}'
    }
    
    for scenario in scelist:
        if scenario != f'OUTPUTS_ROUTED_{dafault_scenario}':
            # keep the lag list for average lag for each events
            lag_list = []
            flines = scenario_flines[scenario]
            
            for peakdate in peakdates:
                # get the data for the peakdate for the default scenario and the given scenario
                default_peakflowvals = default_flines[(default_flines['Date'] >= peakdate - pd.Timedelta(days=7)) & (default_flines['Date'] <= peakdate + pd.Timedelta(days=7))]
                peakflowvals = flines[(flines['Date'] >= peakdate - pd.Timedelta(days=7)) & (flines['Date'] <= peakdate + pd.Timedelta(days=7))]
                # compute the cross-correlation
                x = default_peakflowvals['Discharge'].values
                y = peakflowvals['Discharge'].values
                # compute the cross-correlation
                corr = signal.correlate(x, y, mode='full')
                lags = signal.correlation_lags(x.size, y.size, mode='full')
                # compute the lag
                lag = lags[np.argmax(np.abs(corr))]
                lag_list.append(lag)
            # compute the average lag for the given scenario
            lag = np.mean(lag_list)
            print(f'   ... cross-correlation between {dafault_scenario} and {scenario[15:]} lagged by {min(lag_list)} -- {max(lag_list)} simulation steps')


    return None




def RBI(scelist, routefilename, styear, endyear, ts):
    """_summary_

    Args:
        scelist (_list_): list of scenarios in the current directory
        routefilename (_str_): filename of the routed output file in the each routed scenario folder and should match with the file in the observed folder
        styear (_int_): start year of the simulation or analysis window
        endyear (_int_): end year of the simulation or analysis window

    Returns:
        _type_: _description_
    """
    print('\n\n>>> Calculating Rechard Baker Flashiness Index Calculation')
    # Rechard Baker Fashiness Index calculation
    # make empty dataframe to store the RBI values
    RBI_rows = []
    for scenario in scelist:
        # read the routed output file
        scenario_label = _scenario_output_name(scenario)
        scenario_label = scenario_label.split('_')[0] if '_' in scenario_label else scenario_label
        for i in range(styear, endyear + 1):
            # if the file does not exist, skip the scenario
            flines = _read_rte(scenario, routefilename, i, i, ts, type=1)
            streamflow = flines['Discharge'].values
            if len(streamflow) < 2:
                RBI_value = 0
            else:
                numerator = np.abs(np.diff(streamflow)).sum()
                denominator = streamflow.sum()
                RBI_value = round(numerator / denominator, 3) if denominator != 0 else 0
            RBI_rows.append({'Scenario': scenario_label, 'Year': i, 'RBI': RBI_value})
            # print(f'   ... {scenario} - {i} :\t{RBI_value}')
    RBI_values = pd.DataFrame(RBI_rows)
    # save the RBI values to a csv file
    scenames = [sce.replace('OUTPUTS_ROUTED_', '') for sce in scelist]
    RBI_values.to_csv(f'./discharge_compare/{routefilename[:-4]}/RBI_values_{"_".join(scenames)}.csv', index=False)
    # make the bar graph of the average RBI values for each scenario
    plt.figure(figsize=(5, 5))
    avg_RBI_values = RBI_values.groupby('Scenario')['RBI'].mean().reset_index()
    plt.bar(avg_RBI_values['Scenario'], avg_RBI_values['RBI'], color='skyblue', edgecolor='black')
    # limit y axis from 0.5*min to 1.2*max
    # plt.ylim(min(avg_RBI_values['RBI'])*0.5, max(avg_RBI_values['RBI'])*1.05)
    plt.ylim(0, max(avg_RBI_values['RBI'])*1.05)
    plt.xlabel('Scenario')
    plt.ylabel('Average RBI')
    plt.title('Average RBI by Scenario')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if _save_figure(f'./discharge_compare/{routefilename[:-4]}/Average_RBI_values_{"_".join(scenames)}.png'):
        print(f'   ... RBI values saved to ./discharge_compare/{routefilename[:-4]}/RBI_values{"_".join(scenames)}.csv and avg value graph.')
    return None
        



#! Growing season option is added only for this function
def flow_compare(scelist, routefilename, styear, endyear, default_scenario, ts, flowtype=0, flow_range=None, growing_season=False, time_frame=None, criteria='threshold', threshold=800, tick_interval=None):
    """_summary_
    this function will plot the flow comparison between the default scenario and the given scenario
    this function requires subfunction read_rte to read the routed output files
    and this function requires subfunction plot_compare_sc_fig to plot the flow comparison graph
    lastly, this function will save the flow comparison graph in the 'FDC' folder with the folder name of given routefilename

    Args:
        scelist (_list_): list of scenarios in the current directory
        routefilename (_str_): name of the routed output file, file extension should be '.txt'
        default_scenario (_str_): name fo the default scenario to plot the flow comparison for comparison. Defaults from post_analysis.py script.
        ts (_int_): time step of the output data (hours)
        flowtype (_int_, optional): the type of flow to plot. 0 for entire, 1 for high, 2 for moist, 3 for mid, 4 for dry, 5 for low. Defaults to 0.
                                    if multiple flowtype is needed, use - to connect the flowtype numbers. e.g., 1-2 for high and moist flow
        flow_range (_list_, optional): the range of flow to plot. Defaults to None.
        * flowtype and flow_range should not be used together
        growing_season (_bool_, optional): _description_. Defaults to False.
        time_frame (str, optional): the time frame to plot. 'Y-M' for year-month, 'Y' for year. Defaults to Daily.
        criteria (str, optional): the criteria value you want to check: 'avg', 'max', 'min', 'threshold'. Defaults to 'avg'.
        threshold (float, optional): the threshold value to filter the flow data. Defaults to 2000

    Returns:
        None
    """
    print('\n\n>>> Comparing flow from the routed output files, growing season option is set to '+str(growing_season))
    list_FDC, flow_criteria = _return_FDC(f'OUTPUTS_ROUTED_{default_scenario}', routefilename, styear, endyear, ts)
    flow_criteria.insert(0, 999999) # add the max value to the first element
    flow_criteria.append(0) # add the min value to the last element

    # read the Discharge from the default scenario in dataframe forrmat
    default_flines = _read_rte(f'OUTPUTS_ROUTED_{default_scenario}', routefilename, styear, endyear, ts, type=1)

    # check flow_type and flow_range parameters are not used together if they are, print a message and quit the function
    if flowtype != [0] and flow_range is not None:
        print('   ... flowtype and flow_range parameters should not be used together. Please choose one.')
        return None

    if flowtype != [0]:
        if len(flowtype) == 2:
            flow_range = [flow_criteria[flowtype[0]-1], flow_criteria[flowtype[1]]]
        else:
            flow_range = [flow_criteria[flowtype[0]-1], flow_criteria[flowtype[0]]]
    else:
        flow_range = [999999, 0]
    # print ('flow type', flowtype, 'flow range', flow_range)
    # make a scatter plot for between individual scenario's Discharge comparing with default scenario's Discharge
    for scenario in scelist:
        if scenario != f'OUTPUTS_ROUTED_{default_scenario}':

            # flow for entire discharge
            plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, flowtype, flow_range, growing_season, time_frame, criteria, threshold, tick_interval)
            #* plot for each flow duration (in daily discharge)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, flowtype=1, flow_range=[999999, flow_criteria[0]], growing_season=growing_season)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, flowtype=2, flow_range=[flow_criteria[0], flow_criteria[1]], growing_season=growing_season)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, flowtype=3, flow_range=[flow_criteria[1], flow_criteria[2]], growing_season=growing_season)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, flowtype=4, flow_range=[flow_criteria[2], flow_criteria[3]], growing_season=growing_season)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, flowtype=5, flow_range=[flow_criteria[3], 0], growing_season=growing_season)

            #* plot the flow comparison for year-month average/max/min
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, flowtype, flow_range, growing_season, time_frame, criteria, threshold)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, growing_season=growing_season, time_frame='Y', criteria='avg')
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, flowtype, flow_range, growing_season, time_frame, criteria, threshold)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, growing_season=growing_season, time_frame='Y', criteria='max')
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, flowtype, flow_range, growing_season, time_frame, criteria, threshold)
            # plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, growing_season=growing_season, time_frame='Y', criteria='min')


    return None


def plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, flowtype, flow_range, growing_season, time_frame, criteria, threshold, tick_interval):
    """_summary_
    this function will plot the flow comparison between the default scenario and the given scenario
    this function requires subfunction read_rte to read the routed output files
    and it will save the flow comparison graph in the 'FDC' folder with the folder name of given routefilename

    Args:
        scenario (str): name of the scenario (folder name)
        routefilename (str): filename of the routed output file
        default_flines (Dataframe): the dataframe of the default scenario's flow timeseries, contains observed flow
        flowtype (_list_, optional): the type of flow to plot. 0 for entire, 1 for high, 2 for moist, 3 for mid, 4 for dry, 5 for low. Defaults to [0].
                                     * if multiple flowtype is needed, use list to connect the flowtype numbers. e.g., [1,2] for high and moist flow
        flow_range (_list_, optional): the range of flow rate to plot. Defaults to None. i.e. [1000, 2000]
        growing_season (_bool_, optional): _description_. Defaults to False.
        time_frame (str, optional): the time frame to plot. 'Y-M' for year-month, 'Y' for year. Defaults to Daily.
        criteria (str, optional): the criteria value you want to check: 'avg', 'max', 'min', 'threshold'. Defaults to 'avg'.
        threshold (float, optional): the threshold value to filter the flow data. Defaults to 2000
    
    Returns:
        None
    """

    # ! if criteira is 'threshold', time_frame should be None
    if criteria == 'threshold':
        time_frame = None    

    # set up the figure for the flow comparison
    plt.figure(figsize=(5,5))

    scenario_label = _scenario_display_name(scenario)
    default_label = _scenario_display_name(default_scenario)

    # set the x-axis
    _configure_discharge_axes(_discharge_axis_label(default_label), _discharge_axis_label(scenario_label))
    plt.grid()

    # read the Discharge from the routed output file
    flines = _read_rte(scenario, routefilename, styear, endyear, ts, type=1)
    # concat the Discharge values from the default scenario and the given scenario using the date column
    default_flines['Scenario_Discharge'] = flines['Discharge']

    # make a scatter plot

    # if flow_range is not None, filter the flines by the flow_range
    if flow_range is not None:
        default_flines = default_flines[(default_flines['Discharge'] < flow_range[0]) & (default_flines['Discharge'] >= flow_range[1])]
        if threshold > flow_range[0] or threshold < flow_range[1]:
            print (flow_range, threshold)
            print('   *** ERROR: threshold value is out of the flow_range. Please check the values.')
            return None
    
    # filter the default_flines by the growing season (April 1st to October 31st)
    if growing_season == True:
        default_flines = default_flines[(default_flines['Date'].dt.month >= 4) & (default_flines['Date'].dt.month <= 10)]
    
    # if time_frame is not None, filter the default_flines by the time_frame
    if time_frame is not None:
        # if the time frame is 'Y', make annual average using groupby function
        if time_frame == 'Y':
            if criteria == 'avg':
                default_flines = default_flines.groupby(default_flines['Date'].dt.year).mean()
            elif criteria == 'max':
                default_flines = default_flines.groupby(default_flines['Date'].dt.year).max()
            elif criteria == 'min':
                default_flines = default_flines.groupby(default_flines['Date'].dt.year).min()
            else:
                print('   ... criteria parameter should be avg, max, or min')
                      
        # if the time frame is 'Y-M', make year-month average
        elif time_frame == 'Y-M':
            if criteria == 'avg':
                default_flines = default_flines.groupby([default_flines['Date'].dt.year, default_flines['Date'].dt.month]).mean()
            elif criteria == 'max':
                default_flines = default_flines.groupby([default_flines['Date'].dt.year, default_flines['Date'].dt.month]).max()
            elif criteria == 'min':
                default_flines = default_flines.groupby([default_flines['Date'].dt.year, default_flines['Date'].dt.month]).min()
            else:
                print('   ... criteria parameter should be avg, max, or min')
    
    elif time_frame is None and criteria == 'threshold':
        default_flines = _peak_over_threshold(default_flines, threshold)
        
        
    # save filtered default_flines in csv file for checking with scenario name (optional)
    default_flines.to_csv(f'./discharge_compare/{routefilename[:-4]}/filtered_flows_{scenario.replace("OUTPUTS_ROUTED_", "")}_g-{growing_season}_{time_frame}_f{flowtype}_{criteria}.csv', index=False)

    if default_flines.empty:
        print(f'    ERROR: No data for {scenario.replace("OUTPUTS_ROUTED_", "")} to plot for this scenario and criteria.')
        return None
    else:
        # x axis is the Discharge from the default scenario and y axis is the Discharge from the given scenario
        plt.scatter(default_flines['Discharge'], default_flines['Scenario_Discharge'], label=scenario_label, color='grey', edgecolors='black', s=15, zorder=2)
    

        # plot the y=x line
        plt.axline((0, 0), slope=1, color='red', linestyle='--', linewidth=.5, zorder=3)

        plt.xlim(0, max(max(default_flines['Discharge']), max(default_flines['Scenario_Discharge']))*1.02)
        plt.ylim(0, max(max(default_flines['Discharge']), max(default_flines['Scenario_Discharge']))*1.02)
        # set xtick ytick interval to given number
        if tick_interval is not None:
            plt.xticks(np.arange(0, max(max(default_flines['Discharge']), max(default_flines['Scenario_Discharge']))*1.02, tick_interval))
            plt.yticks(np.arange(0, max(max(default_flines['Discharge']), max(default_flines['Scenario_Discharge']))*1.02, tick_interval))

        plt.legend(['Discharge', '1:1 Line'])
        
        # for graph title
        plt.title(_flow_plot_title(flowtype, time_frame, growing_season, criteria))

        plt.tight_layout()
        if _save_figure(_build_compare_plot_path(routefilename, scenario, growing_season, time_frame, flowtype, criteria)):
            print(f'   ... flow comparison graph for {scenario_label} saved')



def _peak_over_threshold(default_flines, threshold):
    """_summary_
    this function will find the peak over threshold value from the timeseries of the baseline scenario.
    after that, the peak value on the same date from the test scenario will be compared.

    Args:
        flines (DataFrame): the dataframe of flow timeseries with date column
        threshold (float): the threshold value to filter the flow data

    Returns:
        DataFrame: the filtered flow timeseries
    """
    
    # iterate through the default_flines and find the peak over threshold value
    # will use the flag variable to check if the current flow value is greater than the threshold value
    # if the flow value is greater than the threshold value, then the flag variable will be set to True
    # if the flow value is less than the threshold value, then the flag variable will be set to False
    # one peakflow date will be found during the single continuous over-threshold period
    # found peakflow date will be saved in the new dataframe
    above_threshold = default_flines['Discharge'] >= threshold
    event_id = (above_threshold.ne(above_threshold.shift(fill_value=False)) & above_threshold).cumsum()
    peak_flines = default_flines.loc[above_threshold].loc[
        default_flines.loc[above_threshold].groupby(event_id[above_threshold])['Discharge'].idxmax()
    ].reset_index(drop=True)

    print(f'   ... {len(peak_flines)} peak flow events found over the threshold value of {threshold} in the default scenario.')
    return peak_flines    




def _read_rte(scenario, routefilename, styear, endyear, ts, type=0):
    """_summary_
    this function reads the routed output file and returns the flow timeseries in splited list format
    format:
    [date, flow value]
    
    Args:
        scenario (_str_): Name of the scenario (folder name)
        routefilename (_str_): Name of the routed output file (file extension should be '.txt')
        styear (_int_): the starting year of the FDC, given from upper class
        endyear (_int_): the ending year of the FDC. given from upper class
        type (int, optional): 0 for splited numpy vectorized format, 1 for dataframe format. Defaults to 0.

    Returns:
        flines (list): the list of flow timeseries in the format of [date, flow value]
        - date (str): (YYYY-MM-DD)
        - flow value (float)
        flines (DataFrame): the dataframe of flow timeseries with date column, without header [date, flow value]
    """
    return _read_rte_cached(scenario, routefilename, styear, endyear, ts, type).copy()


@lru_cache(maxsize=256)
def _read_rte_cached(scenario, routefilename, styear, endyear, ts, type=0):
    # print (f'   ... reading routed output file for {scenario} from {styear} to {endyear}')
    # if output is daily timestep
    if ts == 24:

        if type == 0:
            # read the routed output file and return the flow timeseries in splited numpy vectorized format
            flines = np.loadtxt(os.path.join('./', scenario, routefilename),
                                delimiter='\t',
                                dtype=[("Date", "U10"), ("Discharge", "f8")],
                                converters={0: lambda s: np.datetime64(datetime.strptime(s, "%m-%d-%Y"))}
                                )
            # filter the flow timeseries by the styear and endyear using numpy vectorized operation
            flines = flines[(flines['Date'].astype('datetime64[D]').astype('datetime64[Y]').astype(int) + 1970 >= styear) & (flines['Date'].astype('datetime64[D]').astype('datetime64[Y]').astype(int) + 1970 <= endyear)]
            '''
            # read the routed output file and return the flow timeseries in splited list format
            with open(os.path.join('./', scenario, routefilename), 'r') as f:
                flines = f.readlines()
                for j in range(len(flines)):
                    flines[j] = flines[j].split()
                    flines[j][1] = float(flines[j][1])
                # filter the flow timeseries by the styear and endyear
                flines = [flines[i] for i in range(len(flines)) if int(flines[i][0][6:]) >= styear and int(flines[i][0][6:]) <= endyear]
            '''
        if type == 1:
            # read the routed output file and return the flow timeseries in dataframe format
            flines = pd.read_csv(os.path.join('./', scenario, routefilename), sep='\t', header=None, names=['Date', 'Discharge'])
            flines['Date'] = pd.to_datetime(flines['Date'])
            flines['Discharge'] = flines['Discharge'].astype(float)
            # filter the flow timeseries by the styear and endyear
            flines = flines[(flines['Date'].dt.year >= styear) & (flines['Date'].dt.year <= endyear)]

    # if output is subdaily timestep
    if ts < 24:

        if type == 0:
            with open(os.path.join('./', scenario, routefilename), 'r') as f:
                flines = f.readlines()
                for j in range(len(flines)):
                    flines[j] = flines[j].split()
                    flines[j][1] = float(flines[j][1])
                # filter the flow timeseries by the styear and endyear
                flines = [flines[i] for i in range(len(flines)) if int(flines[i][0][6:10]) >= styear and int(flines[i][0][6:10]) <= endyear]
        
        if type == 1:
            # read the routed output file and return the flow timeseries in dataframe format
            flines = pd.read_csv(os.path.join('./', scenario, routefilename), sep='\t', header=None, names=['Date', 'Discharge'])
            # from the 'Date' column, replace 'T' to ' '
            flines['Date'] = flines['Date'].str.replace('T', ' ')
            # convert 'Date' column to datetime foramt and the format of the raw data is 'MM-DD-YYYY HH'
            # convert the 'Date' column to datetime format
            flines['Date'] = pd.to_datetime(flines['Date'], format='%m-%d-%Y %H')
            flines['Discharge'] = flines['Discharge'].astype(float)
            # filter the flow timeseries by the styear and endyear
            flines = flines[(flines['Date'].dt.year >= styear) & (flines['Date'].dt.year <= endyear)]

    return flines    




def _printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 30, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()






# end of the script