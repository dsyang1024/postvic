import sys, os, csv
from turtle import pd
import numpy as np
import glob
sys.path.append('./SCRIPTS')
# set matplotlib font as times new roman
'''

This is the post_analysis_diagnosis.py file.


'''

def run_diag(CONFIG):
    # stat_mode = stat_mode.replace('-stats=','').split('/')  # leave only the mode
    scenarios = get_scenarios(CONFIG)
    time_scale = CONFIG.STATS['scale']
    time_scale_dict = {'V':'Annual Average', 'A':'Annual', 'S':'Seasonal', 'M':'Monthly', 'W':'Weekly', 'D':'Daily', 'P':'Period'}
    print(f'    • Scenario: {scenarios}')
    print(f'    • Time scale: {time_scale_dict.get(time_scale, "Unknown")} ({time_scale})\n')

    # run the stats based on the diagnostic mode
    for scenario in scenarios:
        outvar, statistics = run_stats(CONFIG, scenario, time_scale)
        
    # make the graph for each variable and statistic
    # if the time_scale is 'S', seasonal, then the seasonal graph contains different scenarios in one graph,
    # if not, graph will be made for each scenario separately
    if time_scale == 'S':
        print ('----------------------------------------------------------------------')
        print (f'  Time scale: {time_scale_dict.get(time_scale, "Unknown")} ({time_scale})')
        # make one graph for each variable and statistic, and the graph contains different scenarios
        season = ['SPR', 'SUM', 'AUT', 'WIN']
        for var in outvar:
            for sea in season:
                print (f'\n>>> Var: {var}, from scenario/season: {scenario} copy below table to excel')
                print(f'SCE,SEASON,STAT,MIN,MAX')
                for stat in statistics:
                    usefiles = [file for file in os.listdir('./stats/') if f'_{var}' in file and f'_{stat}' in file and sea in file and file.endswith('.asc')]
                    if usefiles == []:
                        pass
                        # print (f'No file found for var: {var}, stat: {stat}, season: {sea}')
                    else:
                        map_stats(CONFIG, usefiles, time_scale, var, stat, sea)

    elif 'P' in time_scale:
        print ('----------------------------------------------------------------------')
        print (f'  Time scale: {time_scale_dict.get(time_scale, "SPECIFIC")} ({time_scale})')
        for var in outvar:
            print (f'\n>>> Var: {var}, for {time_scale} | copy below table to excel')
            for stat in statistics:
                # find the asc file with the var, stat, scenario name in the file name, and end with .asc in the stats folder
                usefiles = [f'{scenario}_{time_scale}_9999_{var}_{stat}.asc' for scenario in scenarios if os.path.isfile(f'./stats/{scenario}_{time_scale}_9999_{var}_{stat}.asc')]
                if usefiles == []:
                    pass
                    # print (f'No file found for var: {var}, stat: {stat}, period: {time_scale}')
                else:
                    print (usefiles)
                    print(f'SCE({stat}), PERIOD ,STAT,MIN,MAX')
                    map_stats(CONFIG, usefiles, time_scale, var, stat, time_scale)
    
    elif time_scale in ['V', 'A']:
        print ('----------------------------------------------------------------------')
        print (f'  Time scale: {time_scale_dict.get(time_scale, "Unknown")} ({time_scale})')
        for var in outvar:
            print (f'\n>>> Var: {var}, from scenario/season: {scenario} copy below table to excel')
            for stat in statistics:
                # find the asc file match to the format "f'{scenario}_9999_{var}_{stat}.asc" in the stats folder
                usefiles = [f'{scenario}_9999_{var}_{stat}.asc' for scenario in scenarios if os.path.isfile(f'./stats/{scenario}_9999_{var}_{stat}.asc')]
                yearoutpattern = f'./stats/[A-Z]_[0-9][0-9][0-9][0-9]_{var}_{stat}.asc'
                yearfiles = found_files = [os.path.basename(f) for f in glob.glob(yearoutpattern)]
                # print (yearfiles)
                # append yearfiles to usefiles
                usefiles.extend(yearfiles)
                # remove if there is duplicate in usefiles
                usefiles = list(set(usefiles))
                # usefiles = [file for file in os.listdir('./stats/') if f'_{var}' in file and f'_{stat}' in file and '_9999' in file and file.endswith('.asc')]
                if usefiles == []:
                    pass
                    # print (f'No file found for var: {var}, stat: {stat}, period: {time_scale}')
                else:
                    print(f'SCE({stat}), SCALE ,STAT,MIN,MAX')
                    map_stats(CONFIG, usefiles, time_scale, var, stat, 'ALL')
    
    elif time_scale == 'M':
        print ('----------------------------------------------------------------------')
        print (f'  Time scale: {time_scale_dict.get(time_scale, "Unknown")} ({time_scale})')
        month = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        # month = ['AUG', 'SEP', 'OCT', 'NOV']
        for var in outvar:
            print (f'\n>>> Var: {var}, from scenario/season: {scenario} copy below table to excel')
            print(f'SCE,MONTH,STAT,MIN,MAX')
            for mon in month:
                for stat in statistics:
                    usefiles = [file for file in os.listdir('./stats/') if f'_{var}' in file and f'_{stat}' in file and f'_{mon}' in file and file.endswith('.asc')]
                    if usefiles == []:
                        pass
                        # print (f'No file found for var: {var}, stat: {stat}, period: {mon}')
                    else:
                        map_stats(CONFIG, usefiles, time_scale, var, stat, mon)
    
    else:
        for scenario in scenarios:
            print ('----------------------------------------------------------------------')
            print (f'  Scenario: {scenario}')
            for var in outvar:
                print (f'\n>>> Var: {var}, from scenario/season: {scenario} copy below table to excel')
                print(f'SCE({stat}), Period ,STAT,MIN,MAX')
                for stat in statistics:
                    # find the asc file with the var, stat, scenario name in the file name, and end with .asc in the stats folder
                    usefiles = [file for file in os.listdir('./stats/') if f'_{var}' in file and f'_{stat}' in file and scenario in file and file.endswith('.asc')]
                    if usefiles == []:
                        print (f'No file found for var: {var}, stat: {stat}, period: {scenario}')
                    else:
                        map_stats(CONFIG, usefiles, time_scale, var, stat, scenario)


def get_scenarios(CONFIG):
    # get the scenarios for the statistics calculation
    # if there is key starts with 'scenario' in the CONFIG.STATS, get the values
    scenarios = []
    if '/' in CONFIG.STATS['scenarios']:
        scenarios = CONFIG.STATS['scenarios'].split('/')
    # if the value is 'all', get sce names from CONFIG.SCE['file']
    if 'all' in scenarios:
        # if the value is 'all', get sce names from CONFIG.SCE['file']
        scenario_file = CONFIG.SCE['scenario_file']
        input_path = CONFIG.DIR['input']
        with open(f'{input_path}/{scenario_file}', 'r') as f:
            # first column is the sce_name
            scenarios = [line.split()[0] for line in f.readlines()]
    return scenarios
      

def make_file_list(CONFIG,scenario):
    # make the output list
    # find the scenario folder
    scenario_path = f'./OUTPUTS_{scenario}'
    outputlist = os.listdir(scenario_path)
    # if the output file starts with 'fluxes_' or 'LAKE_', keep it in the list
    outputlist = [f for f in outputlist if f.startswith(CONFIG.STATS['prefix'])]
    # sort the output list
    outputlist.sort()
    # print (f'>>> {len(outputlist)} output files found in the OUTPUTS folder.')

    # make the list of output files
    f = open(scenario_path+'/file_list.txt', 'w')
    for output in outputlist:
        f.write(f'./OUTPUTS_{scenario}/{output} ')
        cord = output.split('_')[1:]
        f.write(cord[0]+' '+cord[1]+'\n')
    f.close()
    print ('    ... File list file created at:', scenario_path+'/file_list.txt')
    return scenario_path


def run_VICstats(CONFIG, scenario, scenario_path, time_scale):
    # forcing list file name
    forcinglist = f'{scenario_path}/file_list.txt'
    output_prefix = f'./{CONFIG.DIR["stats"]}/{scenario}'
    grid_resolution = '0.0625' # 1/16 degree
    col_list_file = './stats/col_list.txt'
    # send the command to run VICstats
    command = f'VicOutputASMStats {forcinglist} TRUE {output_prefix} {grid_resolution} {col_list_file} {CONFIG.STATS["from"]} 0{CONFIG.STATS["to"]} {time_scale} TRUE FALSE'
    # VicOutputASMStats ./OUTPUTS_O1/file_list.txt TRUE ./stats/test 0.0625 ./stats/col_list.txt 01012000 09302015 A TRUE TRUE
    # VicOutputASMStats ./OUTPUTS_O1/file_list.txt TRUE ./stats/O2 0.0625 ./stats/col_list.txt 10012005 09302015 V TRUE TRUE
    os.system('pwd')
    print (command)
    os.system(command)

    '''
    Usage: VicOutputASMStats <file list file> <Output ArcGrid: TRUE/FALSE> <output prefix> <grid resolution> <column list file> <start date> <end date> <V|A|S|M|W|D> <OVERWRITE: TRUE/FALSE> <PrtAllPeriods: TRUE/FALSE>

        This program produces either an ARC/INFO ASCII grid file
        (output ArcGrid = TRUE) or an XYZ file (Output ArcGrid = FALSE) of the average
        of the selected data column for the given time period.

        The following additional variables can be calculated by this
        program, and used with the standard list of summary metrics, the
        required columns are in the VIC files being processed.
        Add the variable names below to your statistics control file
        to include them in the analysis:
        - OUT_PE Penman potential evaporation, requires "OUT_R_NET",
          "OUT_GRND_FLUX", "OUT_WIND", "OUT_SURF_TEMP", "OUT_REL_HUMID",
          "OUT_AIR_TEMP",
        - OUT_TOTAL_RUNOFF is the sum of "OUT_RUNOFF" and "OUT_BASEFLOW",
        - OUT_TOTAL_SOIL_MOIST is the sum of "OUT_SOIL_MOIST" for each layer,
        - OUT_MGDD modified growing degree day (from mrcc.isws.illinois.edu),
          requires "IN_TMIN" and "IN_TMAX",
        - OUT_PLANT_DAY is a Boolean variable indicating whether or not soil
          surface conditions support planting, requires "OUT_SOIL_MOIST_0"
          and "OUT_SOIL_TEMP_0".  Also requires that a file with top soil
          layer field capacity [mm] be provided following the statistic
          definition in the soil control file.
        - OUT_MRCC_CHILL_HR is the number of chilling hours (fruit trees)
          based on MRCC methodology, requires "IN_TMIN" and "IN_TMAX".
        - OUT_UTAH_CHILL_HR is the number of chilling hours (fruit trees)
          based on UTAH methodology, requires "IN_TMIN" and "IN_TMAX".
        - OUT_DMWD is the number of working days defined by DRAINMOD,
          requires "OUT_PREC" and "OUT_SOIL_MOIST_0".  Also requires that
          a file with top soil layer saturation [mm] be provided following
          the statistic definition in the soil control file.
        - OUT_DSFW is the number of of days suitable for field work
          (Gramig et al, 2017), requires "IN_PREC", "IN_TMIN", "IN_TMAX",
          and "Soil Drainge Class".
        <file list> is a file containing the full grid file name and location,
                latitude and longitude of the grid cell, for each grid cell to be
                included.
        <output prefix> is the prefix (path and start of file name) for the
                output files that will be generated by this program.  A suffix
                will be added to all file names to separate individual output
                for each variable, and for each tperiod (year, season, month,
                etc). Files containing multi-year average statistics for annual,
                seasonal and monthly periods will use "9999" for
                the date in the file name.
        <grid resolution> is the resolution in degrees of the desired output
                grid.
        <column list file> is a multi-column ASCII file that lists the column
                name for each column to be output.  Followed by the statistic
                to be computed and a thresehold if required by the statistic.

                Statistic options include:
                - Mean value                            'mean',
                - Cumulative value                      'sum',
                - Standard Deviation                    'stdev',
                - Maximum value                         'max',
                - Day of maximum value                  'max_day',
                - Minimum value                         'min',
                - Day of minimum value                  'min_day',
                - First value                           'first',
                - Last value                            'last',
                - Last day over thres.                  'ldayo' <thres>,
                - Last day under thres.                 'ldayu' <thres>,
                - First day over thres.                 'fdayo' <thres>,
                - First day under thres.                'fdayu' <thres>,
                - Days over threshold                   'othres' <thres>,
                - Days under threshold                  'uthres' <thres>,
                - Average days over threshold           'avgdaysothres' <thres>,
                - Average days under threshold          'avgdaysuthres' <thres>,
                - Average value over threshold          'avgvalothres' <thres>,
                - Average value under threshold         'avgvaluthres' <thres>,
                - Sum value over threshold              'sumvalothres' <thres>,
                - Sum value (deficit) under threshold   'sumvaluthres' <thres>,
                - Consecutive days over threshold       'daysothres' <thres>,
                - Consecutive days under threshold      'daysuthres' <thres>,
                - Last day over thres before middle     'ldaymido' <thres>,
                - Last day under thres before middle    'ldaymidu' <thres>,
                - First day over thres after middle     'fdaymido' <thres>,
                - First day under thres after middle    'fdaymidu' <thres>,
                - Number of times threshold is crossed  'crossthres' <thres>,
                - RB Index (flashiness)                 'RBI',
                - TQ mean (days spent above mean)       'Tqmean',
                - Seven day low value                   '7daylow',
                - Quantile value                        'quan' <quantile>.

                NOTE: Any single value threshold can be replaced with
                "FILE <shortname> <filename>" to provide spatially
                distributed thresholds.  <shortname> is used to replace the
                threshold value in the output filename, and <filename> must
                be the same format (Arc Grid/XYZ) being used
                for overall processing.
        <start date> and <end date> are the starting and ending dates of the
                period of interest in MMDDYYYY format (MM = month, DD = day,
                YYYY = year - date must be 8 characters).
        <V|A|S|M|W|D> export Annual a(V)erage, (A)nnual, (S)easonal, (M)onthly,
                (W)eekly, (D)aily or annual repeating (P)eriod grids for all
                years in the file
                - Annual uses given start date to start year;
                - Seasonal uses Winter = DJF, Spring = MAM, Summer = JJA, and
                  Autumn = SON;
                - Weekly parses data into 7 day weeks starting with the given
                  start date.
                - Period requires a range in MM-DD_MM-DD format or key phrase
                  "grow" for dynamic growing season, for example
                  "P08-15_11-01" to define the fall working window of
                  August 15th to November 1st.
        <OVERWRITE> if set to TRUE then the output grid files will be
                overwritten.  The default is to replace values in existing
                files with new data.
        <PrtAllPeriods> if set to TRUE then the program will write all output
                files (all years, all seasons, etc), if set to FALSE only
                annual averages will be written.

    '''


def stat_VIC(CONFIG, scenario):
    # using the file_list in each scenario OUTPUTS folder, find the coordinates, find the row/column of the grid
    # read the file_list.txt of the current scenario
    print (f'Processing file_list.txt: ./{CONFIG.DIR["scenario"]}/OUTPUTS_{scenario}/file_list.txt')
    
    # make grid format numpy array that can be used for the output of the statistics.
    # the numpy array will be copied and filled with the statistic value for each variable and statistic according to the scale.
    grid_array, uni_col, uni_row, asc_header, lines = _get_empty_grid_array(scenario)    
    # print (grid_array.shape, len(uni_col), len(uni_row), asc_header)
    
    fromdate = '0'+str(CONFIG.STATS['from']) if len(str(CONFIG.STATS['from'])) == 7 else str(CONFIG.STATS['from'])
    todate = '0'+str(CONFIG.STATS['to']) if len(str(CONFIG.STATS['to'])) == 7 else str(CONFIG.STATS['to'])
    scale = CONFIG.STATS['scale']
    var_stat = _make_variable_stat_grid(grid_array, scale)
    
    # read the output files of the current scenario listed in the file_list.txt
    for line in lines:
        output_file = line.strip().split()[0]
        col_value = float(line.strip().split()[2])
        row_value = float(line.strip().split()[1])
        # find the index of the col and row in the uni_col and uni_row
        col_index = uni_col.index(col_value)
        row_index = uni_row.index(row_value)
        
        # read the output file, find the column with the variable name, and get the value of the variable for the fromdate to todate, and fill the grid_array with the value
        _get_value_from_output(output_file, var_stat, fromdate, todate, col_index, row_index)
            
    return None


def _get_empty_grid_array(scenario):
    import numpy as np
    with open(f'./OUTPUTS_{scenario}/file_list.txt', 'r') as f:
        lines = f.readlines()
        col = []
        row = []
        for i, line in enumerate(lines):
            # print(f'        {line.strip().split()}')
            col.append(float(line.strip().split()[2]))
            row.append(float(line.strip().split()[1]))
        # get the unique col and row, and difference between the unique col and row, to get the grid resolution
        uni_col = sorted(list(set(col)))
        uni_row = sorted(list(set(row)))
        grid_res = round(uni_col[1] - uni_col[0], 4)
        asc_header = f'''ncols         {len(uni_col)}
nrows         {len(uni_row)}
xllcorner     {min(uni_col)-(grid_res/2):<10.6f}
yllcorner     {min(uni_row)-(grid_res/2):<10.6f}
cellsize      {grid_res:<10.6f}
NODATA_value  -9999
    '''
        
        # make the empty numpy 2d array filled with np.nan for now using the size of uni_col and uni_row
        grid_array = np.full((len(uni_row), len(uni_col)), np.nan)
    return grid_array, uni_col, uni_row, asc_header, lines


def _make_variable_stat_grid(grid_array, scale):
    scale = 'S'
    # get the variable name for the statistics from the col_list.txt file in the stats folder
    with open('./stats/col_list.txt', 'r') as f:
        col_list = f.readlines()
        # first column is variable name and second column is statistic
        var_stat = []
        for line in col_list:
            parts = line.split()
            if len(parts) >= 2:
                # print (f'    ... Variable: {parts[0]}, Statistic: {parts[1]}')
                var_stat.append([parts[0], parts[1], grid_array.copy()])
    if scale.upper() == 'V':
        print (var_stat)
        return var_stat
    elif scale.upper() == 'S':
        # return the list with four copied var_stat inside for each season
        var_stat = [var_stat.copy() for _ in range(4)]
        print (var_stat)
        return var_stat


def _get_value_from_output(output_file, var_stat, fromdate, todate, col_index, row_index):
    import pandas as pd
    # read the output file using csv, skip 5 rows, line 6 is header, separator is tab
    output_df = pd.read_csv(output_file, skiprows=5, sep='\t')
    # strip the column names of the output_df
    output_df.columns = output_df.columns.str.strip()
    # clip the output_df to the fromdate and todate
    # if YEAR, MONTH, DAY columns exact match the fromdate and todate, then clip the output_df to the fromdate and todate
    # find index of the fromdate
    fromdate_index = output_df[(output_df['# YEAR'] == fromdate.year) & (output_df['MONTH'] == fromdate.month) & (output_df['DAY'] == fromdate.day)].index

    # find index of the todate
    todate_index = output_df[(output_df['# YEAR'] == todate.year) & (output_df['MONTH'] == todate.month) & (output_df['DAY'] == todate.day)].index

    # clip the output_df to the fromdate and todate
    if len(fromdate_index) > 0 and len(todate_index) > 0:
        output_df = output_df.loc[fromdate_index[0]:todate_index[0]]
    print (output_df)


def map_stats(CONFIG, usefiles, time_scale, var, stat, scenario):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import colors
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    usefiles = sorted(usefiles)
    # print (usefiles)
    
    """
    Reads and plots an ASCII grid file (.asc) as a map.

    Args:
        file_path (str): The path to the .asc file.
    """
    # make subplots as many as the usefiles in one column
    num_plots = len(usefiles)
    fig, axes = plt.subplots(num_plots, 1, figsize=(8, (3*num_plots)+1), sharex=True)
    
    # Ensure axes is always a list (when num_plots == 1, plt.subplots returns a single Axes object)
    if num_plots == 1:
        axes = [axes]

    # read the asc file and save them in a list of numpy arrays
    plot_data = []
    # print (usefiles)
    for usefile in usefiles:
        file_path = f'./stats/{usefile}'
        # print(f'    ... {file_path}')
        try:
            # Read the header of the ASCII grid file
            with open(file_path, 'r') as f:
                header = {}
                for i in range(6):
                    line = f.readline().strip().split()
                    header[line[0].lower()] = float(line[1])

            # Load the grid data using numpy, skipping the header
            grid_data = np.loadtxt(file_path, skiprows=6)

            # Get NODATA value from header and replace it with NaN for plotting
            nodata_value = header.get('nodata_value', -9999) # Default to -9999 if not found
            grid_data[grid_data == nodata_value] = np.nan
            usefilename = usefile.split('/')[-1].replace('.asc', '').replace('9999', '').split('_')
            usefilename = ' '.join([part for part in usefilename[:2]])
            # if scenario is monthly, add scenario at the end of userfilename
            if 'M' in time_scale or 'S' in time_scale:
                # 'scenario' is letter month, change this to number month
                month_dict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
                print (f'{usefilename},{month_dict.get(scenario)}, {np.nanmean(grid_data):.1f}, {np.nanmin(grid_data):.1f}, {np.nanmax(grid_data):.1f}')
            else:
                print(f'{usefilename.split(" ")[0]},{scenario},{np.nanmean(grid_data):.1f},{np.nanmin(grid_data):.1f},{np.nanmax(grid_data):.1f}')

            plot_data.append((grid_data, header))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred from usefile {usefile}: {e}")
    
    # choose the min max range for the colorbar based on the plot_data grid_data values
    all_data = np.concatenate([data[0].flatten() for data in plot_data])
    vmin = np.nanmin(all_data)
    vmax = np.nanmax(all_data)
    # normalize the colorbar to the min max range
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    
    images = []
    usefile_index=0
    for ax, (grid_data, header) in enumerate(plot_data):
        try:
            # Use imshow to display the grid data.
            # The 'viridis' colormap is a good default choice.
            # The 'origin' parameter is set to 'upper' to match the typical representation of grids.
            img = axes[ax].imshow(grid_data, norm=norm)
            images.append(img)
            # replot zero values with single gray color again to make them more visible.
            zero_mask = (grid_data == 0)
            gray_cmp = colors.ListedColormap(['gray'])
            axes[ax].imshow(np.where(zero_mask, 0, np.nan), cmap=gray_cmp)

            # set x-axis and y-axis to the correct coordinates
            x_start = header['xllcorner']
            y_start = header['yllcorner']
            cell_size = header['cellsize']
            # from x/y_start, to ncols/nrows, make the 5 ticks
            x_ticks = np.linspace(0, header['ncols'], num=5)
            y_ticks = np.linspace(0, header['nrows'], num=5)
            axes[ax].set_xticks(x_ticks)
            axes[ax].set_yticks(y_ticks)
            # reverse the yticks to match the coordinate system            
            xtick_labels = [f"{x_start + (cell_size*x_tick):.2f}" for x_tick in x_ticks]
            ytick_labels = [f"{y_start + (cell_size*y_tick):.2f}" for y_tick in y_ticks][::-1]  # reverse the ytick labels
            # print (f'>>> {usefiles[usefile_index]}: xtick_labels: {xtick_labels}, ytick_labels: {ytick_labels}')
                        
            # axes[ax].set_xticklabels(xtick_labels)
            # axes[ax].set_yticklabels(ytick_labels)

            # Set plot titles and labels
            if time_scale == 'S':
                axes[ax].set_title(f'{scenario}', fontsize=10)
            elif time_scale == 'A':
                title = f'{usefiles[usefile_index].split("_")[0]} {usefiles[usefile_index].split("_")[1].replace('9999','')}'
                axes[ax].set_title(title, fontsize=10)
            else:
                axes[ax].set_title(f'{usefiles[usefile_index].split("_")[0]}', fontsize=10)
            usefile_index += 1
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred plotting {usefiles[ax]}: {e}")
            

    # make entire figure share one horizontal oriented colorbar and push colorbar to the right of the figure not to overlap with the plots
    # divider = make_axes_locatable(axes[-1])
    # cax = divider.append_axes("bottom", size="5%")
    cax = fig.add_axes([0.1, 0.05, 0.8, 0.02]) # Create a standalone colorbar axis: [left, bottom, width, height]
    cbar = fig.colorbar(img, cax=cax, orientation='horizontal')
    # add , to the colorbar ticks for thousands separator, and set fontsize to 10
    cbar.ax.tick_params(labelsize=10)
    # make the colorbar ticks have comma as thousands separator if the vmax is greater than or equal to 1000
    if vmax >= 1000:
        cbar.ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    cbar.set_label(f'{outvar_2_word.get(var)}', fontsize=10)


    # save figure
    # fig.supxlabel('Longitude', fontsize=12)
    fig.supylabel('Latitude', fontsize=12)
    # put xlabel for the last subplot only
    axes[-1].set_xlabel('Longitude', fontsize=12)
    plt.subplots_adjust(bottom=0.10, left=0.12, top=0.99, hspace=0.05)
    # plt.tight_layout()
    plt.savefig(f'./stats/{scenario}_{var}_{stat}_{time_scale}.png', dpi=600)
    plt.close()


def run_stats(CONFIG, scenario, time_scale):
    forcings_path = make_file_list(CONFIG,scenario)
    print (f'>>> Running VICstats for scenario: {scenario} with time scale: {time_scale}...')
    run_VICstats(CONFIG, scenario, forcings_path, time_scale)
    # stat_VIC(CONFIG, scenario)
    # find the all output asc file in the stats folder
    asc_files = [asc for asc in os.listdir('./stats/') if asc.endswith('.asc')]
    
    # read the col_list.txt file to get the variable name
    with open('./stats/col_list.txt', 'r') as f:
        col_list = f.readlines()
        # first column is variable name and second column is statistic
        outvar = []
        statistics = []
        for line in col_list:
            parts = line.split()
            if len(parts) >= 2:
                outvar.append(parts[0])
                statistics.append(parts[1])
        # get the unique variable name and statistic, in case there are duplicates in the col_list.txt file
        outvar = list(set(outvar))
        statistics = list(set(statistics))
    
    return outvar, statistics
        

outvar_2_word = {
    'OUT_PREC': r'Precipitation (mm)',
    'OUT_RUNOFF': r'Surface Runoff (mm)',
    'OUT_BASEFLOW': r'Baseflow (mm)',
    'OUT_TOTAL_RUNOFF': r'Total Runoff (mm)',
    'OUT_SOIL_MOIST': r'Soil Moisture (mm)',
    'OUT_IRR_DEF': r'Irrigation Deficit (mm)',
    'OUT_LAKE_VOLUME': r'Pond Volume (m$^3$)',
    'OUT_LAKE_DEPTH': r'Pond Depth (m)',
    'OUT_LAKE_CHAN_OUT': r'Pond Channel Outflow (mm)',
    'OUT_LAKE_CHAN_OUT_V': r'Pond Channel Outflow (m$^3$/sec)',
    'OUT_TOTAL': r'Total outflow (mm)',
    }