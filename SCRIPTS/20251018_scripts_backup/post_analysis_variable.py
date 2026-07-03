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
      ... ./run_vic_commands.csh
      ... ./Submit_VIC_Runs.csh
      ... ./make_scenarios.py
  in addition, water withdrawal file 'withdrawals.txt' in the [INPUTS] folder. with build scripts in Python.
  
  The directory structure is as follows ============================================================================
  
      ... Model Root folder
          /FORCINGS
          /GLOBALFILES
          /INPUTS
              Ⳑ withdrawals.txt
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
          ./make_scenarios.py
          ./scenarios.csv
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
      -v          : validate the routed discharge with the observed data in the OBSERVED folder
                    (this function will run sim_vali function in the post_analysis_route.py script)
      -m          : map the lake variable for the lake grid in each scenario (this will turn on the lake flag)
                    if this option is on, only map function will be work
      -d          : diagnostic mode for the lake analysis (default: off)
                    this will run the diagnosis functions in the post_analysis_diagnosis.py script
                    this diagonostic mode is for the lake water balance diagnosis only
  
  
  * route and lake flags are independent to each other and must be specified separately.
  * Default scenario for the scenario comparison will be assigned in the post_analysis.py script(case sensitive)
    to read the forcing and set the default analysis period.
  * all the grid based analysis will be done in the lake analysis.
  
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
  
  created by DK @ 2025
'''


def variable_reader(variables, given_routefilenames, soilfilename, given_lakefilenames, default_scenario):

    variables.remove('./post_analysis.py')
    """
    check the flags for the analysis
    """
    help_check(variables)

    if '-c' in variables:
        sim_checker()


    refresher = refresher_check(variables)

    route_flag, lake_flag = analysis_flag(variables)

    toi_flag, toi = timeofinterest_check(variables, default_scenario)

    ts = timestep_check(variables, default_scenario)

    growing_season = growing_check(variables)
    
    route_flag, vali_flag = vali_check(variables, default_scenario, route_flag)

    map_flag, lake_flag = map_flag_check(variables, lake_flag)

    target = target_map(variables)

    flowtype = flowtype_checker(variables)
    
    scelist = get_scenarios(default_scenario, vali_flag)
    

    print()
    routefilenames = route_variable_check(variables, route_flag, given_routefilenames)
    
    print()
    lakefilenames = lake_variable_check(variables, lake_flag, soilfilename, given_lakefilenames)

    # check the validation flag


    return refresher, route_flag, lake_flag, routefilenames, lakefilenames, toi_flag, toi, growing_season, scelist, ts, map_flag, target, flowtype


def help_check(variables):
    # check the help flag
    if '-h' in variables or 'help' in variables:
        print (intro_block)
        print('\n\n',' End of Script '.center(120, '='))
        sys.exit()
    else:
        print('-h, help variables will provide the introduction to use this script.\n')



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


def timestep_check(variables, default_scenario):
    # check the timestep flag
    # if any variable in the variables startswith 'ts=', then it will be used
    ts = any(i.startswith('ts=') for i in variables)
    if ts == True:
        ts = [i for i in variables if i.startswith('ts=')][0]
        ts = int(ts.split('=')[1])
    else:
        with open(f'../GLOBALFILES/global_{default_scenario}.txt', 'r') as f:
            global_lines = f.readlines()
            for i in global_lines:
                if i.startswith('OUT_STEP'):
                    ts = int(i.split()[1])
    if ts < 24:
        print(f'• Timestep     : {ts} Hours')
    if ts == 24:
        print(f'• Timestep     : Daily')

    return ts


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


def route_variable_check(variables, route_flag, given_routefilenames):
    """
    check the file names if they are given
    """
    if route_flag == True:
        routefilenames = [i for i in variables if '.txt' in i]
        if routefilenames == []:
            print ('Route file name is not given in the arguments. Dafault file name in the post_analysis will be used.')
            routefilenames = given_routefilenames
            for routefilename in routefilenames:
                print ('   ... '+routefilename)
        else:
            print ('Route file name is given as:')
            for routefilename in routefilenames:
                print ('   ... '+routefilename)
    else:
        routefilenames = given_routefilenames

    return routefilenames


def lake_variable_check(variables, lake_flag, soilfilename, given_lakefilenames):
    """
    check the file names if they are given
    possible options are:
    l=all
    l=89999,87777
    this function will find the grid number from the soil file and match with the coordinates to read the file from the outputs folder
    """

    # read the soil file to get the grid numbers
    with open(soilfilename, 'r') as f:
        soil_lines = f.readlines()
        # find the grid numbers and put them in a dictionary gridnumber: gridcoord
        grid_dic = {}
        for line in soil_lines:
            gridnumber = line.split()[1]
            gridcoord = '_'.join(line.split()[2:4])
            grid_dic[gridnumber] = gridcoord
                

    if lake_flag == True:
        lakefilenames = [i for i in variables if i.startswith('l=')]
        if lakefilenames == []:
            lakefilenames = given_lakefilenames
            print ('>>> Lake: File name(s) are not given in the arguments.')
            print (f'          Dafault grid {given_lakefilenames} in the post_analysis.py will be analyzed.')
            for i in range(len(lakefilenames)):
                    # check if the grid number is in the dictionary
                    if lakefilenames[i] in grid_dic.keys():
                        lakefilenames[i] = 'LAKE_' + grid_dic[lakefilenames[i]]
            for lakefilename in lakefilenames:
                gridcode = dict((v,k) for k,v in grid_dic.items())
                print (f'   ... {lakefilename} ({gridcode[lakefilename[5:]]})')
        else:
            if lakefilenames == ['l=all']:
                print ('>>> Lake: All the grids with the lake will be analyzed.')
            elif 'l=' in lakefilenames[0]:
                print ('>>> Lake: Lake file name is given in the arguments as:')
                lakefilenames = lakefilenames[0][2:].split(',')
                for i in range(len(lakefilenames)):
                    # check if the grid number is in the dictionary
                    if lakefilenames[i] in grid_dic.keys():
                        lakefilenames[i] = 'LAKE_' + grid_dic[lakefilenames[i]]
                for lakefilename in lakefilenames:
                    gridcode = dict((v,k) for k,v in grid_dic.items())
                    print (f'   ... {lakefilename} ({gridcode[lakefilename[5:]]})')
    else:
        lakefilenames = []

    return lakefilenames


def timeofinterest_check(variables, default_scenario):
    """
    check the time of interest for the analysis
    """

    with open(f'../GLOBALFILES/global_{default_scenario}.txt', 'r') as f:
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


    toi = [variable for variable in variables if '-t=' in variable]
    
     # check the time of interest flag
    if toi != []:
        toi_flag = True
        toi = [i for i in variables if '-t=' in i][0]
        toi = toi.split('=')[1]
        toi = [int(toi[:4]), int(toi[5:])]
        if toi[0] >= toi_default[0] and toi[1] <= toi_default[1]:
            print (f'• Time flag    : {toi_flag} ({toi[0]}-{toi[1]})')
        else:
            print (f'• Time flag    : ERROR ({toi[0]}-{toi[1]})')
            print (f'   ... ERROR: check the time of interest, it should be between {toi_default[0]} and {toi_default[1]}')

    else:
        toi_flag = False
        toi = copy.deepcopy(toi_default)
        print (f'Time flag    : {toi_flag} ({toi[0]}-{toi[1]})')

    return toi_flag, toi


def growing_check(variables):
    """
    check the growing season flag
    """
    if '-g' in variables:
        growing_season = True
    else:
        growing_season = False

    print(f'• Growing flag : {growing_season} (Deactivated now, use in the script)')

    return growing_season


def vali_check(variables, default_scenario, route_flag):
    # check the validation flag
    if '-v' in variables:
        variables.remove('-v')
        vali_flag = True
        route_flag = True
        # set the route flag to True if validation is on
        route_flag = True
        print('• Validation   : True')
    else:
        vali_flag = False
        route_flag = route_flag

    return route_flag, vali_flag


def get_scenarios(default_scenario, vali_flag):
    """_summary_
    this function will automatically get the list of scenarios in the current 'SCENARIOS' directory
    Returns:
        scelist (list): this is the list of scenarios in the current directory in string format
    """
    if vali_flag == True:
        # if validation flag is on, then only the default scenario will be used
        scelist = [default_scenario]
    else:
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
    print ('\n• List of scenarios in the current directory')
        
    if default_scenario in scelist:
        # get the default scenario to the first position and push everything else to the right
        scelist.remove(default_scenario)
        scelist.insert(0, default_scenario)
        print('   ... ', end='| ')
        for i in range(len(scelist)):
            print(scelist[i]+'*', end=' | ') if scelist[i] == default_scenario else print(scelist[i], end=' | ')
        # print(*scelist, sep=' | ', end=' |\n')
        print(f'\n   ... Total {len(scelist)} scenarios; (* = default scenario)')
        
    else:
        print(f'   ... Default scenario: {default_scenario} is not in the scenarios list,\n       please check the output folder name in the SCENARIOS directory.')
    # and then compare the lake depths in each of these folders
    return scelist


def map_flag_check(variables, lake_flag):
    # check the map flag
    if '-m' in variables:
        map_flag = True
        lake_flag = True
    else:
        map_flag = False
        lake_flag = lake_flag

    print(f'• Map flag     : {map_flag}')

    return map_flag, lake_flag


def target_map(variables):
    # check the target variable for the lake mapping
    target = [i for i in variables if i.startswith('-target=')]
    if target != []:
        target = target[0].split('=')[1]
        print(f'• Map target   : {target}')
    else:
        target = 'veg_frac'
        print(f'• Map target   : {target}')

    return target


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





# end of the script