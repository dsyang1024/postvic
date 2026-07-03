import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
import warnings
warnings.filterwarnings('ignore')


def get_scenarios(scelist0):
    """_summary_
    this function will automatically get the list of scenarios in the current 'SCENARIOS' directory
    Returns:
        scelist (list): this is the list of scenarios in the current directory in string format
    """
    scelist = []
    for i in range(len(scelist0)):
        scelist.append('OUTPUTS_ROUTED_' + scelist0[i])
    
    return scelist


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

    print('\n\n>>> Validation simulated discharge using observed discharge dataset')
    # this function will validate the simulation by comparfing the flow values from the routed output files with the observed flow values
    # read the routed output files as dataframe format, first line is the header
    # the observation data should be downloaded from USGS website directly
    obslines = pd.read_csv(os.path.join('../','OBSERVED',routefilename),sep='\t', skiprows=26,header=None, names=['Agency', 'Site', 'Date', 'Observed', 'Discharge_cd'])
    # drop Agency, site, Discharge_cd columns
    obslines = obslines.drop(columns=['Agency', 'Site', 'Discharge_cd'])
    obslines['Date'] = pd.to_datetime(obslines['Date'])
    # convert the 'Observed' from cfs to cms multiply by 0.02831683199881
    obslines['Observed'] = obslines['Observed'] * 0.02831683199881

    # filter the obslines with the styear and endyear
    obslines = obslines[(obslines['Date'].dt.year >= styear) & (obslines['Date'].dt.year <= endyear)]

    for scenario in scelist:
        if default_scenario in scenario:
            # read the observed flow values from the routed output files
            flines = read_rte(scenario, routefilename, styear, endyear, ts, type=1)
            '''if ts < 24:
                # current Date column include hours so remove it
                flines['Date'] = flines['Date'].dt.date
                # make daily average if ts is less than 24 hours
                flines = flines.groupby(flines['Date']).mean()
                # reset index
                flines = flines.reset_index()
                # convert the Date column to datetime formatnnnnnnnnn
                flines['Date'] = pd.to_datetime(flines['Date'])'''

                
            # merge the two dataframes on the Date column to the flines dataframe
            flines = pd.merge(flines, obslines, on='Date', how='left')
            # drop the NA rows
            flines = flines.dropna()
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
            
            plt.xlabel('Observed Discharge ('+r"$m^3$"+'/sec)')
            plt.ylabel('Simulated Discharge ('+r"$m^3$"+'/sec)')
            plt.xlim(0, max(max(flines['Observed']), max(flines['Discharge']))*1.02)
            plt.ylim(0, max(max(flines['Observed']), max(flines['Discharge']))*1.02)
            plt.gca().get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
            plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
            plt.grid()
            plt.title(f'{scenario.replace("OUTPUTS_ROUTED_", "")} Discharge Validation')
            plt.legend(['Discharge', '1:1 Line'])
            plt.tight_layout()
            plt.savefig(f'./discharge_validation/{routefilename[:-4]}/sim_vali_{scenario.replace("OUTPUTS_ROUTED_", "")}.png', dpi=600)
            plt.close()

            # plot the timeseries of the observed and simulated flow values
            plt.figure(figsize=(8,4))
            plt.plot(flines['Date'], flines['Observed'], label='Observed', color='black', linestyle='--', linewidth=1)
            plt.plot(flines['Date'], flines['Discharge'], label=scenario.replace('OUTPUTS_ROUTED_', ''), color='r', alpha=0.5, linewidth=1)
            plt.xlabel('Date')
            plt.xticks(rotation=30)
            plt.ylabel('Discharge ('+r"$m^3$"+'/sec)')
            plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
            plt.grid()
            plt.title(f'{scenario.replace("OUTPUTS_ROUTED_", "")} Discharge Validation')
            plt.legend(['Observed', scenario.replace('OUTPUTS_ROUTED_', '')])
            plt.tight_layout()
            plt.savefig(f'./discharge_validation/{routefilename[:-4]}/sim_vali_timeseries_{scenario.replace("OUTPUTS_ROUTED_", "")}.png', dpi=600)
            plt.close()
            
            print(f'   ... simulation validation graph for {scenario.replace("OUTPUTS_ROUTED_", "")} saved')


            '''# conduct statistical analysis for the observed and simulated flow values
            # print the correlation coefficient between the observed and simulated flow values
            # any hydrology model validation standards can be found here: https://swat.tamu.edu/media/90109/moriasimodeleval.pdf
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
            kge = 1 - np.sqrt((corr - 1) ** 2 + (rmse / flines['Observed'].mean() - 1) ** 2 + (flines['Discharge'].mean() / flines['Observed'].mean() - 1) ** 2)'''
            corr, r_squared, nse, pbias, rmse, mae, mape, kge = vali_func(flines)
            # print or stats in the table format
            print(f'          {"Daily scale Stat":>25} | {"Value":>10}')
            print(f'          {"-"*25} | {"-"*10}')
            print(f'          {"Correlation Coefficient":>25} | {round(corr, 3):>10}')
            print(f'          {"R-squared":>25} | {round(r_squared, 3):>10}')
            print(f'          {"NSE":>25} | {round(nse, 3):>10}')
            print(f'          {"P-Bias":>25} | {round(pbias, 3):>10}')
            print(f'          {"RMSE":>25} | {round(rmse, 3):>10}')
            print(f'          {"MAE":>25} | {round(mae, 3):>10}')
            print(f'          {"MAPE":>25} | {round(mape, 3):>10}')
            print(f'          {"KGE":>25} | {round(kge, 3):>10}')
            print(f'          {"-"*25}   {"-"*10}')
            print()


            # Conduct statistical analysis for the observed and simulated flow values in monthly scale
            # convert flines to year-monthly average and make a new dataframe
            flines['Year-Month'] = flines['Date'].dt.to_period('M')
            monthly_flines = flines.groupby('Year-Month').mean()
            # TODO: should be SUM instead of mean for the discharge values

            corr, r_squared, nse, pbias, rmse, mae, mape, kge = vali_func(monthly_flines)
            # print or stats in the table format
            print(f'          {"Monthly scale Stat":>25} | {"Value":>10}')
            print(f'          {"-"*25} | {"-"*10}')
            print(f'          {"Correlation Coefficient":>25} | {round(corr, 3):>10}')
            print(f'          {"R-squared":>25} | {round(r_squared, 3):>10}')
            print(f'          {"NSE":>25} | {round(nse, 3):>10}')
            print(f'          {"P-Bias":>25} | {round(pbias, 3):>10}')
            print(f'          {"RMSE":>25} | {round(rmse, 3):>10}')
            print(f'          {"MAE":>25} | {round(mae, 3):>10}')
            print(f'          {"MAPE":>25} | {round(mape, 3):>10}')
            print(f'          {"KGE":>25} | {round(kge, 3):>10}')
            print(f'          {"-"*25}   {"-"*10}')
            print()


def vali_func(flines):
    """_summary_
    this function will conduct statistical analysis for the observed and simulated flow values
    any hydrology model validation standards can be found here: https://swat.tamu.edu/media/90109/moriasimodeleval.pdf

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




def get_FDC(scelist, routefilename, styear, endyear, ts, flowtype):
    """_summary_
    this function returns the FDC from the routed output files
    this function will plot the all of the FDC graph for each scenario and save it in the FDC folder with the folder name of given routefilename
    this function requires subfunction return_FDC to get the FDC from the routed output files and setup_fig to set up the figure for the FDC

    Args:
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
    setup_FDC_fig()
    print(scelist)

    for scenario in scelist:
        # get the FDC from the routed output files
        list_FDC, flow_criteria = return_FDC(scenario, routefilename, styear, endyear, ts)
        flow_criteria.insert(0, 999999) # add the max value to the first element
        flow_criteria.append(0) # add the min value to the last element

        if flowtype != [0]:
            if len(flowtype) == 2:
                flow_range = [flow_criteria[flowtype[0]-1], flow_criteria[flowtype[1]]]
            else:
                flow_range = [flow_criteria[flowtype[0]-1], flow_criteria[flowtype[0]]]
        else:
            flow_range = [999999, 0]
        # filter the list_FDC based on the flow_range
        temp_FDC = [[],[]]
        for i in range(len(list_FDC[0])):
            if list_FDC[1][i] <= flow_range[0] and list_FDC[1][i] >= flow_range[1]:
                temp_FDC[0].append(list_FDC[0][i])
                temp_FDC[1].append(list_FDC[1][i])
        # list_FDC, flow_criteria = return_FDC(scenario, routefilename, styear, endyear, ts)

        # plot list_FDC to the plot
        plt.plot(temp_FDC[0], temp_FDC[1], label=scenario.replace('OUTPUTS_ROUTED_', ''))

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
    plt.savefig(f'./FDC/{routefilename[:-4]}/FDC_graph_{flowtypename}.png', dpi=600)
    print('   ... FDC graph saved')
    plt.close()

    return None


def return_FDC(scenario,routefilename, styear, endyear, ts):
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
    flines = read_rte(scenario, routefilename, styear, endyear, ts)

    # organize FDC data
    FDC = []
    exist = []
    for i in range(1,len(flines)):
        if flines[i][1] not in FDC:
            FDC.append(flines[i][1])
            exist.append(1)
        else:
            exist[FDC.index(flines[i][1])] = exist[FDC.index(flines[i][1])]+1

    # sort the FDC list in descending order
    temp = []
    for i in range(len(FDC)):
        temp.append((FDC[i],exist[i]/len(flines)*100))

    # sort the temp list by the first element in descending order
    FDCtuple = sorted(temp, key = lambda x : (-x[0]))

    # conver tuple to list
    FDClist = []
    for i in range(len(FDCtuple)):
        FDClist.append(list(FDCtuple[i]))

    # FDC exceedance probability
    for i in range(1,len(FDClist)):
        FDClist[i][1] = round(FDClist[i][1]+FDClist[i-1][1],3)

    FDC = []
    exist = []
    for i in range(len(FDClist)):
        FDC.append(FDClist[i][0])
        exist.append(FDClist[i][1])

    #	Check the 10%, 40%, 60%, and 90% flow value
    flow_criteria = []
    for i in [10, 40, 60, 90]:
        a = []
        for r in range(len(exist)):
            a.append(abs(i-exist[r]))
        flow_criteria.append(round(FDC[a.index(min(a))],3))
    print ('   ...', scenario, flow_criteria)

    # print(scenario, flow_criteria)
    return [exist, FDC], flow_criteria


def setup_FDC_fig():
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
    flines = read_rte(f'OUTPUTS_ROUTED_{default_scenario}', routefilename, styear, endyear, ts, type=1)

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
        for scenario in scelist:
            # read the flow timeseries for each scenario
            flines = read_rte(scenario, routefilename, styear, endyear, ts, type=1)
            # extract the Discharge values from 5 days ago to 5 days later of the peakdate
            peakflowvals = flines[(flines['Date'] >= peakdate - pd.Timedelta(days=7)) & (flines['Date'] <= peakdate + pd.Timedelta(days=7))]
            if scenario == f'OUTPUTS_ROUTED_{default_scenario}':
                plt.plot(peakflowvals['Date'], peakflowvals['Discharge'], label=scenario[15:], color='black', linestyle='--')
            else:
                plt.plot(peakflowvals['Date'], peakflowvals['Discharge'])
        
        plt.title(str(peakdate)[:10])
        plt.xlabel('Date')
        plt.xticks(rotation=30)
        # put comma in the y-axis
        plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        plt.ylabel('Discharge ('+r"$m^3$"+'/day)')
        plt.legend([sce[15:] for sce in scelist])
        plt.tight_layout()
        plt.savefig(f'./hydrographs/{routefilename[:-4]}/hydrograph_{str(peakdate)[:10]}.png', dpi=600)
        print(f'   ... hydrograph for {str(peakdate)[:10]} saved')
        plt.close()

    xcorr(scelist, routefilename, peakdates, styear, endyear, default_scenario, ts)

    return None




def xcorr(scelist, routefilename, peakdates, styear, endyear, dafault_scenario, ts):

    from scipy import signal

    print('\n\n>>> Discharge cross-correlation analysis')
    
    # read the default scenario flow timeseries
    default_flines = read_rte(f'OUTPUTS_ROUTED_{dafault_scenario}', routefilename, styear, endyear, ts, type=1)
    
    for scenario in scelist:
        if scenario != f'OUTPUTS_ROUTED_{dafault_scenario}':
            # keep the lag list for average lag for each events
            lag_list = []
            
            for peakdate in peakdates:
                # get the data for the peakdate for the default scenario and the given scenario
                default_peakflowvals = default_flines[(default_flines['Date'] >= peakdate - pd.Timedelta(days=7)) & (default_flines['Date'] <= peakdate + pd.Timedelta(days=7))]
                flines = read_rte(scenario, routefilename, styear, endyear, ts, type=1)
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
    RBI_values = pd.DataFrame(columns=['Scenario', 'Year', 'RBI'])
    for scenario in scelist:
        # read the routed output file
        for i in range(styear, endyear + 1):
            flines = read_rte(scenario, routefilename, i, i, ts, type=1)
            streamflow = flines['Discharge'].values
            numerator = sum(abs(streamflow[i] - streamflow[i - 1]) for i in range(1, len(streamflow)))
            denominator = sum(streamflow)
            RBI_value = round(numerator / denominator, 3) if denominator != 0 else 0
            RBI_values = RBI_values._append({'Scenario': scenario.replace('OUTPUTS_ROUTED_', ''), 'Year': i, 'RBI': RBI_value}, ignore_index=True)
            # print(f'   ... {scenario} - {i} :\t{RBI_value}')
    # save the RBI values to a csv file
    RBI_values.to_csv(f'./discharge_compare/{routefilename[:-4]}/RBI_values.csv', index=False)
    # make the bar graph of the average RBI values for each scenario
    plt.figure(figsize=(5, 5))
    avg_RBI_values = RBI_values.groupby('Scenario')['RBI'].mean().reset_index()
    plt.bar(avg_RBI_values['Scenario'], avg_RBI_values['RBI'], color='skyblue', edgecolor='black')
    # limit y axis from 0.5*min to 1.2*max
    plt.ylim(min(avg_RBI_values['RBI'])*0.75, max(avg_RBI_values['RBI'])*1.05)
    plt.xlabel('Scenario')
    plt.ylabel('Average RBI')
    plt.title('Average RBI by Scenario')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'./discharge_compare/{routefilename[:-4]}/Average_RBI_values.png', dpi=600)
    plt.close()
    print(f'   ... RBI values saved to ./discharge_compare/{routefilename[:-4]}/RBI_values.csv and avg value graph.')
    return None
        



#! Growing season option is added only for this function
def flow_compare(scelist, routefilename, styear, endyear, default_scenario, ts, flowtype=0, flow_range=None, growing_season=False, time_frame=None, criteria='avg', threshold=1200):
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
    list_FDC, flow_criteria = return_FDC(f'OUTPUTS_ROUTED_{default_scenario}', routefilename, styear, endyear, ts)
    flow_criteria.insert(0, 999999) # add the max value to the first element
    flow_criteria.append(0) # add the min value to the last element

    # read the Discharge from the default scenario in dataframe forrmat
    default_flines = read_rte(f'OUTPUTS_ROUTED_{default_scenario}', routefilename, styear, endyear, ts, type=1)

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

    # make a scatter plot for between individual scenario's Discharge comparing with default scenario's Discharge
    for scenario in scelist:
        if scenario != f'OUTPUTS_ROUTED_{default_scenario}':
            # flow for entire discharge
            plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, flowtype, flow_range, growing_season, time_frame, criteria, threshold)
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

            print(f'   ... flow comparison graph for {scenario.replace("OUTPUTS_ROUTED_", "")} saved')

    return None


def plot_compare_sc_fig(scenario, routefilename, default_flines, styear, endyear, default_scenario, ts, flowtype, flow_range, growing_season, time_frame, criteria, threshold):
    """_summary_
    this function will plot the flow comparison between the default scenario and the given scenario
    this function requires subfunction read_rte to read the routed output files
    and it will save the flow comparison graph in the 'FDC' folder with the folder name of given routefilename

    Args:
        scenario (str): name of the scenario (folder name)
        routefilename (str): filename of the routed output file
        default_flines (Dataframe): the dataframe of the default scenario's flow timeseries
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

    # set the x-axis
    plt.xlabel(default_scenario.replace('OUTPUTS_ROUTED_', '')+' '+'Discharge ('+r"$m^3$"+'/sec)')
    plt.gca().get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    # set the y-axis
    plt.ylabel(scenario.replace('OUTPUTS_ROUTED_', '')+' '+'Discharge ('+r"$m^3$"+'/sec)')
    plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    # set the grid
    plt.grid()

    # read the Discharge from the routed output file
    flines = read_rte(scenario, routefilename, styear, endyear, ts, type=1)
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
        default_flines = peak_over_threshold(default_flines, threshold)


    # x axis is the Discharge from the default scenario and y axis is the Discharge from the given scenario
    plt.scatter(default_flines['Discharge'], default_flines['Scenario_Discharge'], label=scenario.replace('OUTPUTS_ROUTED_', ''), color='grey', edgecolors='black', s=15, zorder=2)
   

    # plot the y=x line
    plt.axline((0, 0), slope=1, color='red', linestyle='--', linewidth=.5, zorder=3)
    
    plt.xlim(0, max(max(default_flines['Discharge']), max(default_flines['Scenario_Discharge']))*1.02)
    plt.ylim(0, max(max(default_flines['Discharge']), max(default_flines['Scenario_Discharge']))*1.02)
    plt.legend(['Discharge', '1:1 Line'])
    
    # for graph title
    graphtitle = 'Discharge'
    if flowtype == 0:
        pass
    elif flowtype == 1:
        graphtitle = 'High-Flow '+graphtitle
    elif flowtype == 2:
        graphtitle = 'Moist-Condition '+graphtitle
    elif flowtype == 3:
        graphtitle = 'Mid-Flow '+graphtitle
    elif flowtype == 4:
        graphtitle = 'Dry-Condition '+graphtitle
    else:
        graphtitle = 'Low-Flow '+graphtitle

    if time_frame is not None:
        graphtitle = graphtitle
        if time_frame == 'Y':
            graphtitle = criteria.capitalize()+' '+graphtitle
            graphtitle = 'Annual '+graphtitle
        elif time_frame == 'Y-M':
            graphtitle = criteria.capitalize()+' '+graphtitle
            graphtitle = 'Monthly '+graphtitle
    if growing_season == True:
        graphtitle = graphtitle+' (Growing Season)'
    plt.title(graphtitle)

    plt.tight_layout()
    plt.savefig(f'./discharge_compare/{routefilename[:-4]}/discharge_compare_g-{growing_season}_{time_frame}_f{flowtype}_{criteria}_{scenario.replace("OUTPUTS_ROUTED_", "")}.png', dpi=600)
    plt.close()


def peak_over_threshold(default_flines, threshold):
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
    peak_flines = pd.DataFrame(columns=default_flines.columns.tolist()) # new dataframe to store the peakflow dates and values

    p_flag = False # initial flag value

    for index, row in default_flines.iterrows():
        
        c_flag = True if row['Discharge'] >= threshold else False
        
        if p_flag == False and c_flag == True:
            # if the previous flag is False and the current flag is True, then this is the start of a peak
            c_peak = row

        elif p_flag == True and c_flag == True:
            # if the previous flag is True and the current flag is True, then this is a continuous peak
            # put c peak  as p_peak and c_peak will be updated
            p_peak = c_peak
            c_peak = row
            if p_peak['Discharge'] > c_peak['Discharge']:
                # if the previous peak is bigger than the current peak, then make the previous peak as the current peak
                c_peak = p_peak
                
        elif p_flag == True and c_flag == False:
            # if the previous flag is True and the current flag is False, then this is the end of a peak
            # save the current peak value and date to the peak_flines dataframe
            peak_flines = pd.concat([peak_flines, c_peak.to_frame().T], ignore_index=True)
        elif p_flag == False and c_flag == False:
            pass # do nothing
        else:
            print('logic error')
        
        p_flag = c_flag


    # print(peak_flines) 
    return peak_flines    




def read_rte(scenario, routefilename, styear, endyear, ts, type=0):
    """_summary_
    this function reads the routed output file and returns the flow timeseries in splited list format
    format:
    [date, flow value]
    
    Args:
        scenario (_str_): Name of the scenario (folder name)
        routefilename (_str_): Name of the routed output file (file extension should be '.txt')
        styear (_int_): the starting year of the FDC, given from upper class
        endyear (_int_): the ending year of the FDC. given from upper class
        type (int, optional): 0 for splited list format, 1 for dataframe format. Defaults to 0.

    Returns:
        flines (list): the list of flow timeseries in the format of [date, flow value]
        - date (str): (YYYY-MM-DD)
        - flow value (float)
        flines (DataFrame): the dataframe of flow timeseries with date column
    """
    
    # if output is daily timestep
    if ts == 24:

        if type == 0:
            # read the routed output file and return the flow timeseries in splited list format
            with open(os.path.join('./', scenario, routefilename), 'r') as f:
                flines = f.readlines()
                for j in range(len(flines)):
                    flines[j] = flines[j].split()
                    flines[j][1] = float(flines[j][1])
                # filter the flow timeseries by the styear and endyear
                flines = [flines[i] for i in range(len(flines)) if int(flines[i][0][6:]) >= styear and int(flines[i][0][6:]) <= endyear]

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
            # read the routed output file and return the flow timeseries in splited list format
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



# end of the script