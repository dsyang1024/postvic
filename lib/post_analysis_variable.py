import sys, os
import copy
import post_analysis_diagnosis as pad

# import post_analysis

intro_block = '''
  This is multi-scenario analysis of the VIC model.
  All the results and routed results should be saved in the [SCENARIOS] folder,
  in the root directory ,in the format of 'OUTPUTS_#' and 'OUTPUTS_ROUTED_#'.
  * # = scenario name or number

  USAGE: python post_analysis.py [options]=[arguments]
  
  For the detailed folder structure, please refer three command files below:
      ... ./INPUTS/build_inputfiles.py
      ... ./INPUTS/build_inputfiles_functions.py
          to build the input files for the VIC model for different scenarios

      ... ./run_vic_commands.csh
      ... ./Submit_VIC_Runs.csh
          to run the VIC model for different scenarios using the built input files
  
  The directory structure is as follows ============================================================================
  
      ... Model Root folder
          /FORCINGS
          /GLOBALFILES
          /INPUTS
              Ⳑ build_inputfiles.py
                ...
          /OUTPUTS
          /OUTPUTS_ROUTED
          /ROUTING_FILES
          /SCENARIOS
              Ⳑ OUTPUTS_1
              Ⳑ OUTPUTS_2
              Ⳑ OUTPUTS_ROUTED_1
              Ⳑ OUTPUTS_ROUTED_2
                ...
          ./run_vic_commands.csh
          ./Submit_VIC_Runs.csh
          ./post_analysis.py
  ==================================================================================================================
          
  There are variables you can use when using this script:

  <Analysis condition arguments>
      -h, help    : show this introduction block
      -r, route   : run the routed discharge analysis
      -l, lake    : run the lake analysis
      1 or 0      : refresh the result folders, 1=on 0=off (default: 0)
      -l=         : run the lake analysis for the given grid numbers, use comma to separate the
                    multiple grid numbers without space (i.e. l=96044,82218)
                    l=all option will run the analysis for all the grid numbers in the soil file
      -ts=        : simulation timestep, default is 24 (hr). if it is subdaily,
                    should be ts=3 or 4 depends on the OUT_STEP variable in the global file
      -t=YYYY-YYYY: set the time of interest for the analysis in year
                    (default: read from default scenario's global file)
      -target=    : target variable to be mapped in the lake analysis (default: veg_frac)
                    other options are 'OUT_RUNOFF' and 'OUT_BASEFLOW'
      -f=         : flow type for the FDC analysis in the routed discharge analysis (default: entire flow)
                    options are: 1: high flow, 2: moist condition, 3: mid flow, 4: dry condition, 5: low flow
                    use -f=1-3 for high to mid flow, -f=3-5 for mid to low flow analysis

  <Trigger type arguments>
      -g          : run the growing season analysis (default: False) for the route analysis
                    (*under development)
      -c          : check the simulation results from each of the scenarios from the error and out messages
                    made by the cluster SLURM using the ../Submit_VIC_Runs.csh file
                    <this function will be merged to the diagnostic mode in the future>
      -m          : map the lake variable for the lake grid in each scenario (this will turn on the lake flag)
                    if this option is on, only map function will be work
  
  <Diagnostic mode arguments>
      -v          : validate the routed discharge with the observed data in the OBSERVED folder
                    (this function will run sim_vali function in the post_analysis_route.py script)
                    -t= option can be used to set the time of interest for the validation
      -stats=      : statistic mode for the lake analysis (default: off)
                    this will run the statistics functions in the post_analysis_diagnosis.py script
                    scenario name and time scale should be given
                    example usage: -stats=No_Pond/V (No_Pond scenario, annual average)
                                   -stats=With_Pond/M (With_Pond scenario, monthly)
                    time scale options: V (Annual Average), A (Annual), S (Seasonal), M (Monthly),
                                        W (Weekly), D (Daily), P (Period)
      -one       : run one grid only for testing variable (this is for the quick testing mode only)
                   this mode will run the first grid from the scenario folder
  
  
  * route and lake flags are independent to each other and must be specified separately.
  * Default scenario for the scenario comparison will be assigned in the post_analysis.py script(case sensitive)
    to read the forcing and set the default analysis period.
  * all the grid based analysis will be done in the lake analysis.
  
  
  created by DK @ 2025
'''

'''
  i.e. post_analysis.py -v -t=2006-2015
       will do routed discharge validation with the observed data in the 'OBSERVED' folder
       from 2006 to 2015 for the default route file name set in post_analysis.py
  
  i.e. post_analysis.py -r -l
       will do both route and lake analysis with the refreshing result folders option on for the default route and
       lake file name in post_analysis.py script in all scenario folders. The time of the interest will follow the
       simulation period in the given default global file in the script. The results folder will not be refreshed.
  
  i.e. post_analysis.py 1 -r Wabash_03336000_discharge.txt
       will do route analysis only refreshing result folders option on for the file
       'Wabash_03336000_discharge.txt' in scenario folders.
       *use when you have specific route file name that is not given in the post_analysis.py script.
  
  i.e. post_analysis.py 0 -l -l=96044 
       will do lake analysis only without refreshing result folders for the file 'LAKE_40.28125_-85.96875',
       which is for the grid number 96044 and'LAKE_41.28125_-84.96875' in all scenario folders.
  
  i.e. post_analysis.py -r t=2006-2015 -target=OUT_RUNOFF
       will do routed discharge analysis without refreshing results folder for the default route file name in
       post_analysis.py script from 2006 to 2015 for all scenarios. In addition, it will map the mean annual runoff
       for the lake grid in each scenario.
'''


def variable_reader(variables, soilfilename):
    # print ('variables:', variables)
    variables.remove('./post_analysis.py')
    """
    check the flags for the analysis
    """
    help_check(variables)
    
    CONFIG = get_config()
    
    default_scenario = CONFIG.SCE['default']

    refresher = refresher_check(variables)

    route_flag, lake_flag = analysis_flag(variables)
    
    # if any variable in the variables has '-M=' in it, then it will be used as the mode of the analysis
    map_flag, target, vali_flag = False, CONFIG.MAP['target'], False
    
    if any(i.startswith('-M=') for i in variables):
        mode = get_mode(variables)
        
        if mode == 'C':
            print ('• Analysis mode: Simulation checker\n')
            # sim_checker()
            sys.exit()
            
        elif mode == 'S':
            print ('• Analysis mode: Stats\n')
            # initialize the diagnostic mode
            pad.run_diag(CONFIG)
            sys.exit()
            
        elif mode == 'V':
            print ('• Analysis mode: Validation\n')
            vali_flag = True
            print (f'• Vali flag    : {vali_flag}')
            route_flag = True
            
        elif mode == 'M':
            print ('• Analysis mode: Mapping\n')
            map_flag, lake_flag, target = map_flag_check(CONFIG, True, lake_flag)
            
        else:
            print (f'• Analysis mode: {mode} is not available.\n  Check helper with -h option.\n')
            map_flag = False


    toi_flag, toi = timeofinterest_check(CONFIG, variables, default_scenario)

    ts, default_global = timestep_check(CONFIG, default_scenario)

    growing_season = CONFIG.TOI['growing_season']
    
    flowtype = flowtype_checker(variables)
    
    scelist = get_scenarios(CONFIG, default_scenario, vali_flag)
    
    print()
    routefilenames = get_route_filenames(CONFIG)
    
    print()
    lakefilenames = get_lake_filenames(CONFIG)
    

    return CONFIG, refresher, route_flag, lake_flag, routefilenames, lakefilenames, toi_flag, toi, growing_season, scelist, ts, map_flag, target, flowtype, default_scenario, default_global



def help_check(variables):
    # check the help flag
    if '-h' in variables or 'help' in variables:
        print (intro_block)
        print('\n\n',' End of Script '.center(120, '='))
        sys.exit()
    else:
        print('-h, help variables will provide the introduction to use this script.\n')


def get_config(file='../VIC_config.csv'):
    """_summary_

    Args:
        file (str, optional): _file path of the config file_. Defaults to 'VIC_config.csv'.

    Returns:
        _dict_: _dictionary of the config values_
    """
    from post_analysis_variable_importer import Config
    CONFIG = Config(file)
    # print ('DIR:', CONFIG.DIR)
    # print ('SCE:', CONFIG.SCE)
    # print ('TOI:', CONFIG.TOI)
    # print ('ROUTE:', CONFIG.ROUTE)
    # print ('MAP:', CONFIG.MAP)
    # print ('STATS:', CONFIG.STATS)
    return CONFIG


def get_mode(variables):
    """_summary_
        this function will find the mode of the analysis based on the variable '-M='
        the Mode this tool provide is following:
        1. simulation checker (-M=C)
        2. diagnosis (-M=D)
        3. mapping (-M=M)
        4. stats (-M=S)
    Args:
        variables (_list_): _variables given through CLI_
    """
    mode = [i for i in variables if i.startswith('-M=')][0]
    mode = mode.split('=')[1]
    return mode



##################################################################################################
########################## subroutines for the variable reader function ##########################
##################################################################################################



def refresher_check(variables):
    # check the refresh flag
    if '1' in variables:
        refresher = True
    else:
        refresher = False

    print(f'• Refresher    : {refresher}')

    # check the output directories (FDC, hydrographs, lake_antpcp_scplot, lake_boxplot, lake_hydrology_timeseries, lake_timeseries, map)
    #  if the directories are not present, create them
    if 'FDC' not in os.listdir():
        os.mkdir('FDC')
    if 'hydrographs' not in os.listdir():
        os.mkdir('hydrographs')
    if 'lake_antpcp_scplot' not in os.listdir():
        os.mkdir('lake_antpcp_scplot')
    if 'lake_boxplot' not in os.listdir():
        os.mkdir('lake_boxplot')
    if 'lake_hydrology_timeseries' not in os.listdir():
        os.mkdir('lake_hydrology_timeseries')
    if 'lake_timeseries' not in os.listdir():
        os.mkdir('lake_timeseries')
    if 'map' not in os.listdir():
        os.mkdir('map')

    
    return refresher


def timestep_check(CONFIG, default_scenario):
    global_dir = f'../{CONFIG.DIR["global"]}'
    default_global = CONFIG.DIR['global_reference']
    # check the timestep flag
    ts = CONFIG.TOI['timestep']
    if ts < 24:
        print(f'• Timestep     : {ts} Hours')
    if ts == 24:
        print(f'• Timestep     : Daily')

    return ts, default_global


def analysis_flag(variables):
    # check the route and lake flags
    if '-r' in variables or '-l' in variables or 'route' in variables or 'lake' in variables:
        if '-r' in variables or 'route' in variables:
            route_flag = True
        else:
            route_flag = False
        
        if '-l' in variables or 'lake' in variables:
            lake_flag = True
        else:
            lake_flag = False
    else:
        route_flag = False
        lake_flag = False


    print(f'• Route flag   : {route_flag}')
    print(f'• Lake flag    : {lake_flag}')

    return route_flag, lake_flag


def get_route_filenames(CONFIG):
    # if ROUTE has multiple keys with 'name#', then it will be used as the route file names for the analysis
    if any(key.startswith('name') for key in CONFIG.ROUTE.keys()):
        routefilenames = [CONFIG.ROUTE[key] for key in CONFIG.ROUTE.keys() if key.startswith('name')]
    print ('• Route file   :')
    # print each route file name with 15 spaces in front of it
    for routefilename in routefilenames:
        print ('                 '+routefilename)
    return routefilenames

def get_lake_filenames(CONFIG):
    # if LAKE has multiple keys with 'name#', then it will be used as the lake file names for the analysis
    if any(key.startswith('name') for key in CONFIG.LAKE.keys()):
        lakefilenames = [str(CONFIG.LAKE[key]) for key in CONFIG.LAKE.keys() if key.startswith('name')]
    print ('• Lake file    :')
    # print each lake file name with 15 spaces in front of it
    for lakefilename in lakefilenames:
        print ('                 '+str(lakefilename))
    return lakefilenames


def timeofinterest_check(CONFIG, variables, default_scenario):
    """
    check the time of interest for the analysis
    """
    global_file = f'../{CONFIG.DIR["global"]}/{CONFIG.DIR["global_reference"]}'
    with open(global_file, 'r') as f:
        global_lines = f.readlines()
        # find the forcing data info
        '''
        STARTYEAR	1980	# year model simulation starts
        STARTMONTH	09	# month model simulation starts
        STARTDAY	30	# day model simulation starts
        ENDYEAR 	2015	# year model simulation ends
        ENDMONTH	09	# month model simulation ends
        ENDDAY		30	# day model simulation ends
        SKIPYEAR 	5	# Number of years of output to omit from the output files
        '''
        for line in global_lines:
            if 'STARTYEAR' in line:
                styear = int(line.split()[1])
            if 'SKIPYEAR' in line:
                skipyear = int(line.split()[1])
                styear_default = styear + skipyear
            if 'ENDYEAR' in line:
                endyear_default = int(line.split()[1])
        toi_default = [styear_default, endyear_default]    
    
     # check the time of interest flag
    if CONFIG.TOI['from'] is not '' and CONFIG.TOI['to'] is not '':
        toi_flag = True
        toi = [CONFIG.TOI['from'], CONFIG.TOI['to']]
        # toi = [i for i in variables if '-t=' in i][0]
        # toi = toi.split('=')[1]
        # toi = [int(toi[:4]), int(toi[5:])]
        if toi[0] >= toi_default[0] and toi[1] <= toi_default[1]:
            print (f'• Time flag    : {toi_flag} ({toi[0]}-{toi[1]})')
        else:
            print (f'• Time flag    : ERROR ({toi[0]}-{toi[1]})')
            print (f'   ... ERROR: check the time of interest, it should be between {toi_default[0]} and {toi_default[1]}')

    else:
        toi_flag = False
        toi = copy.deepcopy(toi_default)
        print (f'• Time flag    : {toi_flag} ({toi[0]}-{toi[1]})')

    return toi_flag, toi


def get_scenarios(CONFIG, default_scenario, vali_flag):
    """_summary_
    this function will automatically get the list of scenarios in the current 'SCENARIOS' directory
    Returns:
        scelist (list): this is the list of scenarios in the current directory in string format
    """
    print('\n• List of scenarios in the current directory')
    if vali_flag == True:
        # if validation flag is on, then only the default scenario will be used
        scelist = [default_scenario]
    else:
        if CONFIG.SCE['analysis'] == 'all':
            # Going to print the list of output folders in the current directory
            # output folders are usually named as 'output_1', 'output_2', etc.
            # so we can use this to get the list of output folders
            scelist = [f for f in os.listdir('./') if os.path.isdir(os.path.join('./', f))]
            # if 'ROUTED' in list component, then remove it
            scelist = [f for f in scelist if 'ROUTED' not in f]
            scelist = [f[8:] for f in scelist if 'OUTPUTS' in f]
            # sort the list
            scelist.sort()
            # print each of the folders in each line using for loop
            # if ROUTE has multiple keys with 'name#', then it will be used as the route file names for the analysis
        elif '/' in CONFIG.SCE['analysis']:
            scelist = CONFIG.SCE['analysis'].split('/')
            scelist = [f for f in scelist if f in scelist]
        else:
            print(f'   ... No scenario is selected for the analysis based on the config file: {CONFIG.SCE["analysis"]}')
            print(f'       check the config file and make sure the scenario names are correct.')
            scelist = []        

    if default_scenario in scelist:
        # get the default scenario to the first position and push everything else to the right
        scelist.remove(default_scenario)
        scelist.insert(0, default_scenario)
        print('   ... ', end='| ')
        for i in range(len(scelist)):
            print(scelist[i]+'*', end=' | ') if scelist[i] == default_scenario else print(scelist[i], end=' | ')
        print(f'\n   ... Total {len(scelist)} scenarios; (* = default scenario)')
        
    else:
        print(f'   ... Default scenario: {default_scenario} is not in the scenarios list,\n       please check the output folder name in the SCENARIOS directory.')
    # and then compare the lake depths in each of these folders
    return scelist


def map_flag_check(CONFIG, map_flag, lake_flag):
    # check the map flag
    lake_flag = True
    target = CONFIG.MAP['target']

    return map_flag, lake_flag, target


def flowtype_checker(variables):
    flownames = {1:'high flow', 2:'moist cond.', 3:'mid flow', 4:'dry cond.', 5:'low flow'}
    # check the flowtype variable
    flowtype = [i for i in variables if i.startswith('-f=')]
    if flowtype != []:
        flowtype = flowtype[0].split('=')[1]
        # check if there is - in the flowtype
        if '-' in flowtype:
            flowtype = [int(i) for i in flowtype.split('-')]
            flowtypenames = [flownames[i] for i in flowtype if i in flownames.keys()]
            print(f'• Flowtype     : {flowtype} ({" - ".join(flowtypenames)})')
        else:
            flowtype = [int(flowtype)]
            flowtypenames = [flownames[i] for i in flowtype if i in flownames.keys()]
            print(f'• Flowtype     : {flowtype} ({" - ".join(flowtypenames)})')
        if flowtype == [0]:
            print(f'• Flowtype     : Entire flow')
    else:
        flowtype = [0]
        print(f'• Flowtype     : Entire flow')

    return flowtype


def sim_checker():
    # !check the simulation results from each of the scenarios from the run message from the cluster run
    # only available when you ran the model from the cluster using ./Submit_VIC_Runs.csh file in the root directory
    print ('\n\n>>> Simulation checker is running')
    msglist = os.listdir('../RUN_MESSAGES/')
    msglist = [f[:-4] for f in msglist if '.out' in f]
    print (f'   ... Total {len(msglist)} simulation messages found')

    for i in range(len(msglist)):
        with open(os.path.join('../RUN_MESSAGES/', msglist[i]+'.err'), 'r') as f:
            flines = f.readlines()
            print(f'\n   ... {i+1}) '+' '.join(flines[0].split()[:2]), end=' | ')
        with open(os.path.join('../RUN_MESSAGES/', msglist[i]+'.err'), 'r') as f:
            flines = f.readlines()

            # find the line with the cell number
            celllist = []
            cellinenum = []
            for i in range(len(flines)):
                if 'cell: ' in flines[i]:
                    # split the line with the comma and space
                    # and then take the second element
                    celllist.append(flines[i].split()[1].replace(',',''))
                    cellinenum.append(i)
            # count the water balance error
            werrcount = 0
            werrcell = []
            werrrange = []
            for j in range(len(celllist)-1):
                checklines = flines[cellinenum[j]:cellinenum[j+1]]
                for k in checklines:
                    if 'Total Cumulative Water Error for Grid Cell' in k:
                        checkline = k.split()
                        if abs(float(checkline[-1])) > 0:
                            werrcount += 1
                            werrcell.append(celllist[j])
                            werrrange.append(checkline[-1])
            if werrcount == 0:
                print('No water balance error found')
            else:
                print(f'{werrcount} water balance error found ({min(werrrange)} / {max(werrrange)})', end='')
        
        # print the cell numbers with the errors
        if werrcount > 0:
            for i in range(len(werrcell)):
                if i % 10 == 0:
                    print('\n            ', end='')
                print(f'{werrcell[i]}', end=' ')
            print()
    
    sys.exit()


def init_diag_mode(variables):
    diag_mode = [i for i in variables if i.startswith('-d=')][0]
    # initialize the diagnostic mode
    pad.receive_var(diag_mode)

# end of the script