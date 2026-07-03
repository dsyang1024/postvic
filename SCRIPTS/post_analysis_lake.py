import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams.update({'font.size': 12}) # or any other desired size in points
from matplotlib.markers import MarkerStyle
import geopandas as gpd
import math
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
        scelist.append('OUTPUTS_' + scelist0[i])
    scelist = [sce for sce in scelist if 'No' not in sce]
    print (scelist)
    return scelist


def folder_setup(CONFIG, lakefilename, refresher):
    from shutil import rmtree
    """_summary_
    this function is used to set up the folders for the lake analysis

    Args:
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.
        refresher (bool): if True, it will refresh the folder by removing the existing folder and creating a new one. if False, it will keep the existing folder.
        
    Returns:
        None
    """
    
    print('\n\n>>> Setting up folders for the analysis for the Grid: '+lakefilename)
    # make the folders for the lake analysis
    access = 0o777
    lakefilename = f'{CONFIG.LAKE["prefix"]}_{lakefilename}'
    if not os.path.exists('./lake_boxplot'):
        print('    ... Creating folders for lake boxplot')
        os.mkdir('./lake_boxplot', access)
    if not os.path.exists('./lake_antpcp_scplot'):
        print('    ... Creating folders for lake antpcp scplot')
        os.mkdir('./lake_antpcp_scplot', access)
    if not os.path.exists('./lake_timeseries'):
        print('    ... Creating folders for lake timeseries')
        os.mkdir('./lake_timeseries', access)
    if not os.path.exists('./lake_hydrology_timeseries'):
        print('    ... Creating folders for lake hydrology timeseries')
        os.mkdir('./lake_hydrology_timeseries', access)
    
    
    if not os.path.exists('./lake_boxplot/'+lakefilename):
        print('    ... Creating folders for lake boxplot')
        os.mkdir('./lake_boxplot/'+lakefilename, access)
    elif refresher == True:
        rmtree('./lake_boxplot/'+lakefilename)
        os.mkdir('./lake_boxplot/'+lakefilename, access)
        print('    ... Boxplot Directory refreshed')
    else:
        print('    ... Boxplot Directory already exists')

    if not os.path.exists('./lake_antpcp_scplot/'+lakefilename):
        print('    ... Creating folders for lake antpcp scplot')
        os.mkdir('./lake_antpcp_scplot/'+lakefilename, access)
    elif refresher == True:
        rmtree('./lake_antpcp_scplot/'+lakefilename)
        os.mkdir('./lake_antpcp_scplot/'+lakefilename, access)
        print('    ... Antpcp scplot Directory refreshed')
    else:
        print('    ... Antpcp scplot Directory already exists')

    if not os.path.exists('./lake_timeseries/'+lakefilename):
        print('    ... Creating folders for lake timeseries')
        os.mkdir('./lake_timeseries/'+lakefilename, access)
    elif refresher == True:
        rmtree('./lake_timeseries/'+lakefilename)
        os.mkdir('./lake_timeseries/'+lakefilename, access)
        print('    ... Timeseries Directory refreshed')
    else:
        print('    ... Timeseries Directory already exists')

    if not os.path.exists('./lake_hydrology_timeseries/'+lakefilename):
        print('    ... Creating folders for lake hydrology timeseries')
        os.mkdir('./lake_hydrology_timeseries/'+lakefilename, access)
    elif refresher == True:
        rmtree('./lake_hydrology_timeseries/'+lakefilename)
        os.mkdir('./lake_hydrology_timeseries/'+lakefilename, access)
        print('    ... Lake hydrology timeseries Directory refreshed')
    else:
        print('    ... Lake hydrology timeseries Directory already exists')

    if not os.path.exists('./map'):
        print('    ... Creating folders for map')
        os.mkdir('./map', access)
    elif refresher == True:
        rmtree('./map')
        os.mkdir('./map', access)
        print('    ... map Directory refreshed')
    else:
        print('    ... map Directory already exists')

    '''if not os.path.exists('./lakedepth_results/'+lakefilename):
        print('    ... Creating folders for lake depth results')
        os.mkdir('./lakedepth_results/'+lakefilename, access)
    elif refresher == True:
        rmtree('./lakedepth_results/'+lakefilename)
        os.mkdir('./lakedepth_results/'+lakefilename, access)
        print('    ... Depth results Directory refreshed')
    else:
        print('    ... Depth results Directory already exists')'''
    



def lake_boxplot(outvar, unit, scelist, lakefilename, styear, endyear, yrange=[0,3]):
    """_summary_
    this function will make a boxplot for the lake depth from each scenario
    it will do the following:
    1. read the lake depth file from each scenario
    2. make a boxplot for each scenario
    3. save the boxplot as a png file
    4. save the boxplot in a folder named 'lake_boxplot'
    5. save the boxplot with the name of the scenario
    6. save the boxplot with the name of the scenario+'_lake_depth_boxplot.png'
    7. save the boxplot in a folder named 'lake_boxplot' with the name of the each scenario

    Args:
        scelist (_type_): list of scenarios in the current directory
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.
        yrange (list, optional): y-axis range for the boxplot. Defaults to [1.5,3.5].

    Returns:
        None
        
    """

    print(f'\n\n>>> Making boxplot for the lake {outvar.replace("OUT_","").lower()} from each scenario')
    # make the subplots for the integrated lake depth boxplot
    rowmax = math.ceil(len(scelist)/2)
    fig, axs = plt.subplots(rowmax, 2, figsize=(8, rowmax*2.5), sharex=True, sharey=True)

    rows = 0
    columns = 0

    for scenario in scelist:
        # read the lake depth file
        lakefile = os.path.join('./', scenario, lakefilename)
        # check if the file exists
        if os.path.exists(lakefile):
            # read the lake depth file
            flines = read_lake(scenario, lakefilename, styear, endyear)

            # get the OUT_LAKE_DEPTH values in boxplot according to MONTH
            flines.boxplot(column=outvar, by='MONTH')

            # set the x-axis label as 'Month'
            plt.xlabel('Month')
            # set the y-axis label
            ylabel = outvar.replace('OUT_','').replace('_', ' ').title() + ' (' + unit + ')'
            plt.ylabel(ylabel)
            # if yaxis value is over 1000, use scientific notation
            if flines[outvar].max() > 1000:
                plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

            # title of the boxplot is the SCE name
            # remove the title of the boxplot and leave the suptitle
            plt.title('')
            plt.suptitle(scenario.replace('OUTPUTS_', 'Scenario: '))
            plt.tight_layout()

            # save the figure as SCE name
            plt.savefig(os.path.join('./lake_boxplot/'+lakefilename+'/', scenario+f'_{outvar.replace("OUT_","").lower()}_boxplot.png'), dpi=600)
            print(f'    ... {scenario} saved')

            # assign the graph to the fig plot with the right axs number
            flines.boxplot(column=outvar, by='MONTH', label=scenario.replace('OUTPUTS_', ''), ax=axs[rows, columns])
            axs[rows, columns].set_title('')
            axs[rows, columns].set_ylabel('')
            axs[rows, columns].set_xlabel('')
            # axs[rows, columns].set_ylim(yrange)
            # axs[rows, columns].set_yticks(np.arange(yrange[0], yrange[1], 0.5))
            axs[rows, columns].legend()

            # increment the xaxs and yaxs
            columns += 1
            if columns == 2:
                columns = 0
                rows += 1
                            
            # reset the figure
            plt.close()
        else:
            print(f'    ... {scenario} lake file does not exist')
            pass

    fig.texts = []
    fig.supylabel(outvar.replace('OUT_','').replace('_', ' ').title()+' ('+unit+')')
    fig.supxlabel('Month')
    fig.tight_layout()
    fig.savefig(os.path.join('./lake_boxplot/'+lakefilename+'/', f'Entire_{outvar.replace("OUT_","").lower()}_boxplot.png'), dpi=600)
    print('    ... Entire Boxplot saved')
    # close the figure
    plt.close(fig)
    plt.close()

    return None




def lake_depth_scplot(forcing_df, scelist, lakefilename, styear, endyear, antdays=30, yrange=[0,3]):
    """_summary_
    this function will make a scatter plot for the lake depth from each scenario
    it will do the following:
    1. read the forcing file for grid
    2. read the lake depth file from each scenario
    3. make a scatter plot for each scenario
    5. save the scatter plot in a folder named 'lake_antpcp_scplot' with the name of the each scenario

    Args:
        forcing_df (dataframe): dataframe of the forcing file (obtained from read_forcing function)
        scelist (_type_): list of scenarios in the current directory
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.
        antdays (int, optional): Days of precipitation cumulation. Defaults to 30.
        yrange (list, optional): y-axis range for the boxplot. Defaults to [1.5,3.5].

    Returns:
        None
    """

    print('\n\n>>> Making scatter plot for the lake depth from each scenario')

    # make the subplots for the integrated lake depth scatter plot
    rowmax = math.ceil(len(scelist)/2)
    # fig, axs = plt.subplots(rowmax,2, figsize=(8, 25))
    fig, axs = plt.subplots(rowmax, 2, figsize=(8, rowmax*2.5), sharex=True, sharey=True)

    rows = 0
    columns = 0
        
    for scenario in scelist:
        # read the lake depth file
        lakefile = os.path.join('./', scenario, lakefilename)
        # check if the file exists
        if os.path.exists(lakefile):

                flines = read_lake(scenario, lakefilename, styear, endyear)
                # merge the forcing data with the lake depth data
                flines = pd.merge(flines, forcing_df, on='DATE', how='left')

                # plot the OUT_LAKE_DEPTH vs PRECIP in scatter plot
                flines['ANT_PRECIP'] = flines['PRECIP'].rolling(window=antdays).sum()
                flines.plot(x='ANT_PRECIP', y=' OUT_LAKE_DEPTH', kind='scatter', color='black')

                # set the x-axis label as 'Precipitation (mm/day)'
                plt.xlabel(str(antdays)+'days Cumulative Precipitation (mm)')
                # set the y-axis label as 'Lake Depth (m)'
                plt.ylabel('Lake Depth (m)')
                plt.ylim(yrange)
                plt.yticks(np.arange(yrange[0], yrange[1], 0.5))

                # save the figure as SCE name
                plt.title(scenario.replace('OUTPUTS_', 'Scenario: '))
                plt.tight_layout()
                plt.savefig(os.path.join('./lake_antpcp_scplot/'+lakefilename+'/', scenario+'_lake_antpcp_scplot.png'), dpi=600)
                print(f'    ... {scenario} saved')

                # assign the graph to the fig plot with the right axs number
                flines.plot(x='ANT_PRECIP', y=' OUT_LAKE_DEPTH', kind='scatter', color='grey', edgecolors='black', s=15, label=scenario.replace('OUTPUTS_', ''), ax=axs[rows, columns])
                # axs[rows, columns].set_title(scenario.replace('OUTPUTS_', 'Scenario: '))
                axs[rows, columns].set_ylabel('')
                axs[rows, columns].set_xlabel('')
                axs[rows, columns].set_ylim(yrange)
                axs[rows, columns].set_yticks(np.arange(yrange[0], yrange[1], 0.5))

                # increment the xaxs and yaxs
                columns += 1
                if columns == 2:
                    columns = 0
                    rows += 1
                
                # reset the figure
                plt.close()

    fig.supylabel('Lake Depth (m)')
    fig.supxlabel(str(antdays)+'days Cumulative Precipitation (mm)')
    fig.tight_layout()

    fig.savefig(os.path.join('./lake_antpcp_scplot/', lakefilename, 'Entire_lake_antpcp_scplot.png'), dpi=600)
    print('    ... Entire Scatterplot saved')
    # close the figure
    plt.close(fig)


    return None




def lake_timeseries_plot(CONFIG, forcing_df, scelist, lakefilename, styear, endyear, yrange=[0,3]):
    """_summary_
    this function will make a time series plot for the lake depth from each scenario
    it will do the following:
    1. read the forcing file for grid
    2. read the lake depth file from each scenario
    3. make a time series plot for each scenario
    4. save the time series plot in a folder named 'lake_timeseries' with the name of the each scenario

    Args:
        forcing_df (dataframe): dataframe of the forcing file (obtained from read_forcing function)
        scelist (_list_): list of scenarios in the current directory
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.
        styear (int, optional): _description_. start year of the analysis. Defaults to 1985.
        endyear (int, optional): _description_. end year of the analysis. Defaults to 2015.
        yrange (list, optional): y-axis range for the boxplot. Defaults to [1.5,3.5].        

    Returns:
        None
    """

    import matplotlib.dates as mdates

    print('\n\n>>> Making lake depth timeseries plot from each scenario')
    years = list(range(styear, endyear+1))
    print(f'    ... Years from {styear} to {endyear}')


    for year in years:
        # make the subplots for the integrated lake depth time series
        fig, axs = plt.subplots(len(scelist)+1, 1, figsize=(8, (len(scelist)+1)*1.5), sharex=True)
        # filter the forcing_df_year for year
        forcing_df_year = forcing_df.loc[forcing_df['DATE'].dt.year == year]
        
        axs[0].bar(forcing_df_year['DATE'], forcing_df_year['PRECIP'], color='royalblue', label='Precipitation (mm)')
        axs[0].set_ylabel('Precipitation\n(mm)', color='royalblue')
        axs[0].legend().set_visible(False)
        
        axnum = 1
        # for each scenario
        for scenario in scelist:

            # read the lake depth file
            lakefile = os.path.join('./', scenario, lakefilename)
            # check if the file exists
            if os.path.exists(lakefile):
                # print(f'    ... Reading {scenario} lake depth file')
                with open(lakefile, 'r') as f:
                    # read the lake depth file
                    flines = read_lake(scenario, lakefilename, styear, endyear)
                    
                    # filter the file for the given year
                    flines_year = flines.loc[flines['DATE'].dt.year == year]
                
                    flines_year.plot(x='DATE', y='OUT_LAKE_DEPTH', color='black', label=scenario.replace('OUTPUTS_', ''), ax=axs[axnum], zorder=2)
                    # Set x-axis ticks every three months and show year-month format
                    axs[axnum].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                    # rotate the x-axis labels for better readability
                    # plt.setp(ax[1].xaxis.get_majorticklabels(), rotation=30)
                    # axs[axnum].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                    axs[axnum].minorticks_off()
                    # ax[1].set_ylabel('Lake Depth (m)')
                    axs[axnum].set_ylim(yrange)
                    axs[axnum].set_ylabel('')
                    # ax[axnum].legend().set_visible(False)

                    axs[axnum].grid(True, zorder=0)

                    plt.ylabel('')
                    plt.ylim(yrange)
                    # save the figure as SCE name
                    # fig.suptitle(scenario.replace('OUTPUTS_', 'Scenario: '))
            axnum += 1
        for i in range(len(scelist)+1):
            # axs[i].legend().set_visible(False)
            axs[i].minorticks_off()
            axs[i].grid(True, zorder=0)
        axs[len(scelist)].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        fig.supylabel('Lake Depth (m)')
        fig.tight_layout()
        fig.savefig(os.path.join('./lake_timeseries/',lakefilename, str(year)+'_lake_timeseries.png'), dpi=600)

        # close the figure
        plt.close()
        print(f'    ... {year} saved')




    return None




def lake_hydrology_timeseries_plot(forcing_df, scelist, lakefilename, styear, endyear, yrange=[0,3]):
    """_summary_
    this function will make a time series plot for the lake depth from each scenario
    it will do the following:
    1. read the forcing file for grid
    2. read the lake depth file from each scenario
    3. make a time series plot for each scenario
    4. save the time series plot in a folder named 'lake_hydrology_timeseries' with the name of the each scenario

    Args:
        scelist (_type_): list of scenarios in the current directory
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.
        styear (int, optional): _description_. start year of the analysis. Defaults to 1985.
        endyear (int, optional): _description_. end year of the analysis. Defaults to 2015.

    Returns:
        None
    """
    import matplotlib.dates as mdates

    print('\n\n>>> Making lake hydrology timeseries plot from each scenario')
    years = list(range(styear, endyear+1))
    # read the forcing data for the given years
    print(f'    ... Years from {styear} to {endyear}')

    for year in years:
        # list the components you need to plot
        plotlist = ['OUT_RUNOFF',
                    'OUT_BASEFLOW',
                    'OUT_LAKE_DEPTH',
                    'OUT_LAKE_VOLUME',
                    'OUT_LAKE_EVAP',
                    ]
        
        for scenario in scelist:
            # make the subplots for the integrated lake depth time series
            # subplots will show precipitation, lake depth, outflow, baseflow
            fig, axs = plt.subplots(len(plotlist)+1, 1, figsize=(8, len(plotlist)*1.5), sharex=True)

            # filter the forcing_df_year for year
            forcing_df_year = forcing_df.loc[forcing_df['DATE'].dt.year == year]
            
            axs[0].bar(forcing_df_year['DATE'], forcing_df_year['PRECIP'], color='royalblue', label='Precipitation (mm)', zorder=2)
            axs[0].set_ylabel('Precipitation\n(mm)', color='royalblue')
            
            # read the lake file and get the lake depth values
            flines = read_lake(scenario, lakefilename, styear, endyear)
            lakes_year = flines.loc[flines['DATE'].dt.year == year]
            # read the fluxes_ file and get outflow and baseflow values
            flines = read_flux(scenario, lakefilename, styear, endyear)
            fluxes_year = flines.loc[flines['DATE'].dt.year == year]
            # claculate the lake dynamics
            fluxes_year[' LAKE_DYNAMICS'] = fluxes_year['OUT_LAKE_RO_IN'] + fluxes_year['OUT_LAKE_BF_IN'] - fluxes_year['OUT_LAKE_BF_OUT'] + fluxes_year['OUT_LAKE_CHAN_IN']- fluxes_year['OUT_LAKE_CHAN_OUT'] - fluxes_year['OUT_LAKE_EVAP'] - fluxes_year['OUT_LAKE_RCHRG']
            # merge forcing_df_year, lakes_year, fluxes_year and fluxes_year using the 'DATE' column
            flines_year = pd.merge(forcing_df_year, lakes_year, on='DATE', how='left')
            flines_year = pd.merge(flines_year, fluxes_year, on='DATE', how='left')
            # print (flines_year.columns)

            for i in range(len(plotlist)):
                
                def lncolor (item):
                    if item == ' LAKE_DYNAMICS':
                        return 'red'
                    elif 'RUNOFF' in item or 'BASEFLOW' in item:
                        return 'darkblue'
                    elif '_IN' in item:
                        return 'teal'
                    elif '_OUT' in item or 'RCHRG' in item or 'EVAP' in item:
                        return 'saddlebrown'
                    else:
                        return 'black'

                # plot the values in the subplots
                flines_year.plot(x='DATE', y=plotlist[i], ax=axs[i+1], zorder=2, linewidth=1, color=lncolor(plotlist[i]), label=scenario.replace('OUTPUTS_', ''))
                axs[i+1].set_ylabel(plotlist[i].replace('OUT_','')+'\n(mm)', color=lncolor(plotlist[i]))
                if plotlist[i] == 'OUT_LAKE_DEPTH':
                    axs[i+1].set_ylim(yrange)
                    axs[i+1].set_ylabel('Lake Depth (m)', color='black')

            """flines_year.plot(x='DATE', y=' OUT_RUNOFF', color='darkblue', ax=axs[1], zorder=2, linewidth=1)
            axs[1].set_ylabel('Runoff (mm)', color='darkblue')
            flines_year.plot(x='DATE', y=' OUT_BASEFLOW', color='green', ax=axs[2], zorder=2, linewidth=1)
            axs[2].set_ylabel('Baseflow (mm)', color='green')
            flines_year.plot(x='DATE', y=' OUT_LAKE_DEPTH', color='black', ax=axs[3], zorder=2, linewidth=1)
            axs[3].set_ylabel('Lake Depth (m)', color='black')
            axs[3].set_ylim(yrange) #* only for the lake
            axs[4].set_ylabel('Lake Dynamics\n(mm)', color='red')
            flines_year.plot(x='DATE', y=' OUT_LAKE_RO_IN', color='darkblue', ax=axs[5], zorder=2, linewidth=1)
            axs[5].set_ylabel('Runoff\nto Lake (mm)', color='darkblue')
            flines_year.plot(x='DATE', y=' OUT_LAKE_BF_IN', color='teal', ax=axs[6], zorder=2, linewidth=1)
            axs[6].set_ylabel('Baseflow\nto Lake (mm)', color='teal')
            flines_year.plot(x='DATE', y=' OUT_LAKE_BF_OUT', color='teal', ax=axs[7], zorder=2, linewidth=1)
            axs[7].set_ylabel('Baseflow\nfrom Lake (mm)', color='teal')
            flines_year.plot(x='DATE', y=' OUT_LAKE_CHAN_IN', color='orange', ax=axs[8], zorder=2, linewidth=1)
            axs[8].set_ylabel('Channel Outflow\nto Lake (mm)', color='orange')
            flines_year.plot(x='DATE', y=' OUT_LAKE_CHAN_OUT', color='orange', ax=axs[9], zorder=2, linewidth=1)
            axs[9].set_ylabel('Channel Outflow\nfrom Lake (mm)', color='orange')
            flines_year.plot(x='DATE', y=' OUT_LAKE_EVAP', color='skyblue', ax=axs[10], zorder=2, linewidth=1)
            axs[10].set_ylabel('Evaporation\nfrom Lake (mm)', color='skyblue')
            flines_year.plot(x='DATE', y=' OUT_LAKE_RCHRG', color='grey', ax=axs[11], zorder=2, linewidth=1)
            axs[11].set_ylabel('Recharge\nfrom Lake (mm)', color='grey')"""

            # hide legends
            for i in range(len(plotlist)+1):
                axs[i].legend().set_visible(False)
                axs[i].minorticks_off()
                axs[i].grid(True, zorder=0)
            # set x-axis ticks every three months and show year-month format
            axs[len(plotlist)-1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))

            # save figure
            plt.tight_layout()
            fig.savefig(os.path.join('./lake_hydrology_timeseries/',lakefilename, scenario.replace('OUTPUTS_','')+'_'+str(year)+'_hydrology_timeseries.png'), dpi=600)
                
            plt.close()
        print(f'    ... {year} saved')
    
    return None




def map_lake(scelist, lakefilename, styear, endyear, default_scenario, target):
    import matplotlib.colors as mcolors
    """_summary_
    this function will map the data for the lake depth from each scenario
    it will do the following:
    1. read the flux file for the given lakefilename
    2. get the outflow values
    3. make a scatter plot for the outflow and baseflow
    4. save the scatter plot as a png file
    5. save the scatter plot in a folder named 'map'
    * this function will requires the subfunction [set_map]

    Args:
        scelist (_list_): list of scenarios in the current directory
        lakefilename (_str_): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.
        styear (_int_): start year of the analysis
        endyear (_int_): end year of the analysis
        default_scenario (_str_): default scenario's name. Defaults from post_analysis.py script.
        target (str): target variable to be mapped. Defaults to 'veg_frac'. other options are 'OUT_RUNOFF' and 'OUT_BASEFLOW'

        Returns:
        None
    """

    print(f'\n\n>>> Mapping the data for the each grid from each scenario of {target}')

    if target == 'veg_frac':
        scelist = [default_scenario]

    # read the flux file and get the outflow values
    for scenario in scelist:
        fig, ax, grid_marker, outlist = set_map(default_scenario, target)
        
        if target != 'veg_frac':
            for index, row in outlist.iterrows():
                # read the flux file
                lakefilename = 'LAKE_'+str(row['LAT'])+'_'+str(row['LON'])
                flines = read_flux(scenario, lakefilename, styear, endyear)
                # add average value of out_runoff and out_baseflow to the dataframe with column name of 'OUT_RUNOFF' and 'OUT_BASEFLOW' to the flines
                outlist.loc[index, 'OUT_RUNOFF'] = flines[' OUT_RUNOFF'].mean()
                outlist.loc[index, 'OUT_BASEFLOW'] = flines[' OUT_BASEFLOW'].mean()
        
        # check the min/max value of the outlist[target]
        print(f'    ... {scenario} {target} min: {round(outlist[target].min(),4)}, max: {round(outlist[target].max(),4)}')

        if target == 'veg_frac':
            # normalize the veg_frac values between 0 and 1
            normlize = mcolors.Normalize(vmin=0, vmax=1)
        else:
            # normalize the outflow values between 0 and 1.5
            vmin = 0
            vmax = 1.2
            normlize = mcolors.Normalize(vmin=vmin, vmax=vmax)
        # make a scatter plot for the outflow and baseflow
        sc = ax.scatter(outlist['LON'], outlist['LAT'], c=outlist[target], marker=grid_marker, edgecolors='k',label='Lake Grids', linewidth=0.2, zorder=2, norm=normlize)
        # add colorbar to the map with five ticks
        if target == 'veg_frac':
            cbar = fig.colorbar(sc, ticks=[0, 0.2, 0.4, 0.6, 0.8, 1])
        else:
            cbar = fig.colorbar(sc, ticks=[vmin, (vmin+vmax)/4, (vmin+vmax)/2, 3*(vmin+vmax)/4, vmax])

        # give the colorbar a title
        if target == 'veg_frac':
            cbar.set_label('Vegetation\nFraction'.title())
        else:
            cbar.set_label(target.replace('OUT_','')+' (mm/day)')

        plt.tight_layout()
        plt.savefig(f'./map/{scenario}_{target}.png', dpi=600)
        print (f'    ... {scenario} {target} map saved')


def set_map(default_scenario, target):
    """_summary_
    this function is subfunction for the map_lake function
    this function will set up the map for the lake depth analysis
    Args:
        default_scenario (str, optional): default scenario's name. Defaults from the post_analysis.py script.
        target (str): target variable to be mapped. Defaults to 'veg_frac'. other options are 'OUT_RUNOFF' and 'OUT_BASEFLOW'

    Returns:
        fig (figure): figure object for the map
        ax (axis): axis object for the map
        grid_marker (marker): marker object for the grid
        outlist (dataframe): dataframe of the lake depth file
    """
    # import the map library
    boundary = gpd.read_file('./map_data/boundary/cb_2023_us_state_20m.shp')
    boundary.head()
    boundary.crs
    boundary = boundary.to_crs(epsg=4326)
    fig = plt.figure(figsize=(8,6))

    
    # get the coordinates from the output files in the lake file
    outlist = os.listdir(f'./OUTPUTS_{default_scenario}')
    outlist = [file for file in outlist if 'LAKE' in file]
    outlist = [file.replace('LAKE_','').split('_') for file in outlist]
    # change the string to float
    outlist = [[float(i) for i in file] for file in outlist]
    # first column of the outlist is the latitude, make a dataframe
    lat = [i[0] for i in outlist]
    lon = [i[1] for i in outlist]
    latmax = max(lat)
    latmin = min(lat)
    lonmax = max(lon)
    lonmin = min(lon)
    outlist = pd.DataFrame(outlist, columns=['LAT', 'LON'])
    indexlist = pd.read_csv('../INPUTS/cell_info_all.txt', delimiter='\s+')
    veglist = pd.read_csv('../INPUTS/veg_area_all.txt', delimiter='\s+')
    outlist = pd.merge(outlist, indexlist, on=['LAT', 'LON'], how='inner')
    outlist = pd.merge(outlist, veglist, on=['gridcell'], how='inner')
    # get the min max value from the outlist
    latmax = outlist['LAT'].max()
    latmin = outlist['LAT'].min()
    lonmax = outlist['LON'].max()
    lonmin = outlist['LON'].min()


    ax = boundary.boundary.plot(color='dimgrey', linewidth=0.5, figsize=(8,6), zorder=0)
    # set the veiw to the boundary map with latmax, latmin, lonmax, lonmin
    # boundary = boundary.cx[lonmin:lonmax, latmin:latmax]
    ax.axis([lonmin-1, lonmax+1, latmin-1, latmax+1])
    # give xlable and ylabel to the map
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    # set the title of the map
    if target == 'veg_frac':
        plt.title('Vegetation Fraction of Simulated Grids')
    else:
        plt.title(target.replace('OUT_','')+' of Simulated Grids (mm/day)')

    # plot the point from outlist coordinates on the map
    grid_marker = MarkerStyle('s').scaled(0.82,1.2)

    return fig, ax, grid_marker, outlist




def read_forcing(CONFIG, lakefilename, styear, endyear, default_scenario, default_global):
    """_summary_
    this function will read the forcing file for the given lakefilename
    it will do the following:
    1. read the forcing file
    2. return the forcing dataframe

    Args:
        CONFIG (dict): configuration dictionary containing directory paths and other settings.
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.
        styear (int): starting year for the analysis. Defaults to model simulation.
        endyear (int): ending year for the analysis. Defaults to model simulation.
        default_scenario (str): default scenario's name. Defaults from the post_analysis.py script.

    Returns:
        forcing (dataframe): dataframe of the forcing file
    """
    print('\n\n>>> Reading forcing data for the analysis for the Grid: '+lakefilename)
    
    # get the forcing file by changing lakefile 'LAKE' to 'data' from directory '../FORCINGS'
    forcingfile = os.path.join('../', CONFIG.DIR['forcing'], f'{CONFIG.DIR["forcing_prefix"]}_{lakefilename}')
    print ('    ... Reading forcing file: '+forcingfile)
    
    # read the forcingfile, file has no header, delimiter is space
    with open(forcingfile, 'r') as f:
        forcing_df = pd.read_csv(f, delimiter=' ', header=None)
        # set the header name as ['PRECIP', 'MINTEMP', ''MAXTEMP, 'WINDSPEED']
        forcing_df.columns = ['PRECIP', 'MINTEMP', 'MAXTEMP', 'WINDSPEED']
    
    with open(f'../GLOBALFILES/{default_global}', 'r') as f:
        global_lines = f.readlines()
        # find the forcing data info
        '''
        FORCEYEAR	1915	# Year of first forcing record
        FORCEMONTH	01	# Month of first forcing record
        FORCEDAY	01	# Day of first forcing record
        '''
        for line in global_lines:
            if 'FORCEYEAR' in line:
                forceyear = int(line.split()[1])
            if 'FORCEMONTH' in line:
                forcemonth = int(line.split()[1])
            if 'FORCEDAY' in line:
                forceday = int(line.split()[1])
        print(f'    ... Forcing data starts from {forceyear}-{forcemonth:02d}-{forceday:02d}')
    
    # add the data of forcing data start date to the forcing dataframe
    forcing_df['DATE'] = pd.date_range(start=f'{forceyear}-{forcemonth:02d}-{forceday:02d}', periods=len(forcing_df), freq='D')
    # filter the forcing dataframe for the given years
    forcing_df = forcing_df.loc[(forcing_df['DATE'].dt.year >= styear) & (forcing_df['DATE'].dt.year <= endyear)]
    # reset the index of the dataframe
    forcing_df.reset_index(drop=True, inplace=True)
    # return the forcing dataframe
    print(f'    ... Forcing data read successfully from {styear} to {endyear}')
        
    return forcing_df


def read_lake(scenario, lakefilename, styear, endyear):
    """_summary_
    this function will read the lake depth file for the given scenario and lakefilename and return the dataframe of the lake output file

    Args:
        scenario (str): name of the scenario to be analyzed (folder name)
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.

    Returns:
        flines (dataframe): dataframe of the lake depth file
    """
    # read the lake depth file
    lakefile = os.path.join('./', scenario, lakefilename)
    # check if the file exists
    # read the lake depth file
    with open(lakefile, 'r') as f:
        # read the lakefile, this file is plain text file. the delimiter is tab, line 6 is the header
        flines = pd.read_csv(f, delimiter='\t', header=5)
        flines.dropna(inplace=True)

        # make column names have no white spaces
        flines.columns = flines.columns.str.strip()

        # make date column from # YEAR, MONTH, DAY columns
        flines['DATE'] = pd.to_datetime(flines['# YEAR'].astype(str) + '-' + flines['MONTH'].astype(str) + '-' + flines['DAY'].astype(str))
        # filter the flines for the given years
        flines = flines.loc[(flines['DATE'].dt.year >= styear) & (flines['DATE'].dt.year <= endyear)]

    
    return flines


def read_flux(scenario, lakefilename, styear, endyear):
    """_summary_
    this function will read the lake depth file for the given scenario and lakefilename and return the dataframe of the lake output file

    Args:
        scenario (str): name of the scenario to be analyzed (folder name)
        lakefilename (str): name of the lake file to be analyzed usually it starts with "LAKE_" and coordinates of the grid comes after the prefix.

    Returns:
        flines (dataframe): dataframe of the lake depth file
    """
    fluxesfilename = lakefilename.replace('LAKE', 'fluxes')
    # read the lake depth file
    fluxesfile = os.path.join('./', scenario, fluxesfilename)
    # check if the file exists
    # read the lake depth file
    with open(fluxesfile, 'r') as f:
        # read the lakefile, this file is plain text file. the delimiter is tab, line 6 is the header
        flines = pd.read_csv(f, delimiter='\t', header=5)
        flines.dropna(inplace=True)
        
        # make column names have no white spaces
        flines.columns = flines.columns.str.strip()

        # make date column from # YEAR, MONTH, DAY columns
        flines['DATE'] = pd.to_datetime(flines['# YEAR'].astype(str) + '-' + flines['MONTH'].astype(str) + '-' + flines['DAY'].astype(str))
        # filter the flines for the given years
        flines = flines.loc[(flines['DATE'].dt.year >= styear) & (flines['DATE'].dt.year <= endyear)]

    
    return flines


  


    


# end of the script