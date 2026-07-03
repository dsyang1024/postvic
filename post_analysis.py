#!/apps/external/apps/conda/2024.09/bin/python

# -*- coding: utf-8 -*-

import sys, os
system_variables = sys.argv
sys.path.insert(0, './SCRIPTS')

# ignore warnings
import warnings
warnings.filterwarnings("ignore")

# moving to the SCENARIOS folder
try:
    os.chdir('./SCENARIOS')
except FileNotFoundError:
    print("SCENARIOS folder not found.")
    sys.exit()

'''
This is for DK's post analysis of the Wabash model.
FDC and lake analysis from the VIC model output will be done here.
All the results and routed results should be saved in the SCENARIOS folder in the format of 'OUTPUTS_#' and 'OUTPUTS_ROUTED_#'.

Total 40 functions for this analysis script.

===== ===== ===== ===== ===== ===== ===== ===== ====== ====== ===== =====


TODO : route file will be end with *_discharge.txt anyway. so change it to find any *_discharge.txt suffix in the _ROUTED folder.
TODO : flow_compare function should be able to receive multiple criteria.
'''

#? system parameters ========================================================
# routefilenames = [
#     # 'Wabash_03322985_discharge.txt',
#     'Wabash_03325000_discharge.txt',
#     'Wabash_03335500_discharge.txt',
#     'Wabash_03336000_discharge.txt'
# ]
# lakefilenames = ['96044']
soilfilename = '../INPUTS/ALL_SOIL.asc' #should have all the soil even though they are separated.
# soil file will be used only for the matching grid code and coordinate for reading the output file
default_scenario = 'No_Pond' # for the default scenario, only name is needed

#? ==========================================================================

print()
print(' Post Analysis of the VIC Model for multi-scenarios'.center(120, '='), end='\n\n')

import post_analysis_variable as pav
CONFIG, refresher, route_flag, lake_flag, routefilenames, lakefilenames, toi_flag, toi, growing_season, scelist0, ts, map_flag, target, flowtype, default_scenario, default_global = pav.variable_reader(system_variables, soilfilename)

if route_flag == True:
    import post_analysis_route as par
    print(' Routed Analysis '.center(100, '='))

    # get the scenario list for the route analysis
    scelist = par.get_scenarios(scelist0)
    # scelist = ['OUTPUTS_ROUTED_Base','OUTPUTS_ROUTED_base_withdrawal', 'OUTPUTS_ROUTED_nolake']

    for routefilename in routefilenames:
        # set up the folders for the routed analysis
        par.folder_setup(routefilename, refresher)

        # validate the routed output files using the observed dataset in the 'OBSERVED' folder
        par.sim_vali(scelist, routefilename, toi[0], toi[1], default_scenario, ts)
        # par.water_balance_check(scelist, routefilename, toi[0], toi[1], ts)

        # if -v option is not selected, the length of the scelist will be > 1
        if len(scelist) > 1:
            # if any of scenario does not have the routefilename, skip the entire process for the routefilename
            for scenario in scelist:
                if not os.path.exists(os.path.join(scenario, routefilename)):
                    print(f'   ... {routefilename} does not exist in {scenario} folder, skipping the entire process for this routefilename...')
                    break
            else:
                # if all scenarios have the routefilename, then proceed with the analysis
                # get the FDC from the routed output files
                par.get_FDC(default_scenario, scelist, routefilename, toi[0], toi[1], ts, flowtype)

                # get the Richard-Baker Index from the routed output files
                par.RBI(scelist, routefilename, toi[0], toi[1], ts)

                # get the hydrographs for peakflows from the routed output files
                # get the cross-correlation for each scenario will be done here
                par.hydrograph_plot(scelist, routefilename, toi[0], toi[1], default_scenario, ts, peak_number=CONFIG.ROUTE['peaknum'])

                # get the flow comparison for each scenario
                #! you can choose growing season option by adding growing_season = True
                par.flow_compare(scelist, routefilename, toi[0], toi[1], default_scenario, ts, flowtype=flowtype, criteria='threshold', threshold=CONFIG.ROUTE['POT'], tick_interval=2000, growing_season=growing_season)
        
        pass





if lake_flag == True:
    import post_analysis_lake as pal
    print('\n\n',' Individual Lake Analysis '.center(120, '='))
    
    # get the scenario list for the lake analysis
    scelist = pal.get_scenarios(scelist0)
    # scelist.remove('OUTPUTS_No_Lake')

    if map_flag == False:
        for lakefilename in lakefilenames:
            # set up the folders for the lake analysis
            pal.folder_setup(CONFIG, lakefilename, refresher)

            # read the forcing data for analysis
            forcing_df = pal.read_forcing(CONFIG, lakefilename, toi[0], toi[1], default_scenario, default_global)

            lakefilename = f'{CONFIG.LAKE["prefix"]}_{lakefilename}'
            # make the boxplot for the lake depth from each scenario
            yrange = [0, 3.0] # for the lake depth plot
            # pal.lake_boxplot('OUT_LAKE_VOLUME', '$m^{3}$', scelist, lakefilename, toi[0], toi[1])
            # pal.lake_boxplot('OUT_LAKE_DEPTH', '$m$', scelist, lakefilename, toi[0], toi[1])

            # make the antpcp scplot for the lake depth from each scenario
            # pal.lake_depth_scplot(forcing_df, scelist, lakefilename, toi[0], toi[1], yrange=yrange)

            # get the lake depth results for each scenario
            pal.lake_timeseries_plot(CONFIG, forcing_df, scelist, lakefilename, toi[0], toi[1])

            # get the hydrology results for each scenario
            # pal.lake_hydrology_timeseries_plot(forcing_df, scelist, lakefilename, toi[0], toi[1])
            
            # map the data
            # pal.map_lake(scelist, lakefilename, toi[0], toi[1], default_scenario, target)

        pass

    else:
        for lakefilename in lakefilenames:
            # set up the folders for the lake analysis
            pal.folder_setup(lakefilename, refresher)

            # map the data
            pal.map_lake(scelist, lakefilename, toi[0], toi[1], default_scenario, target)

        pass


print('\n\n', ' End of Post Analysis '.center(120, '='), end='\n\n')