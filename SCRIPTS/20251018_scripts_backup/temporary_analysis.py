#!/apps/external/apps/conda/2024.09/bin/python

# -*- coding: utf-8 -*-

import pandas as pd
import os
import post_analysis_lake as pal


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 70, fill = '█', printEnd = "\r"):
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


styear = 1985
endyear = 2001
scelist = ['OUTPUTS_Pond', 'OUTPUTS_1b', 'OUTPUTS_1c', 'OUTPUTS_2b', 'OUTPUTS_2c', 'OUTPUTS_3b', 'OUTPUTS_3c']
# scelist = ['OUTPUTS_2c', 'OUTPUTS_3b', 'OUTPUTS_3c']

print(scelist, '\n')
for scenario in scelist:
    print (scenario)
    if scenario in os.listdir():
        lakefilenames = os.listdir(os.path.join('./', scenario))
        lakefilenames = [name for name in lakefilenames if name.startswith('LAKE_')]
        # lakefilenames = lakefilenames[:2]
        print (len(lakefilenames), 'files found in', scenario)

        countzero = 0
        filecount = 0
        for lakefilename in lakefilenames:
            flines = pal.read_lake(scenario, lakefilename, styear, endyear)
            # count how many values are smaller than 0 in the ' OUT_LAKE_DEPTH' column
            countzerotemp = (flines[' OUT_LAKE_DEPTH'] <= 0).sum()
            # print column names of flines
            filecount += 1
            printProgressBar(filecount, len(lakefilenames), prefix = 'Progress:', suffix = 'Reading...')
        countzero += countzerotemp

        print(scenario, ' :: ', countzero, '\n')
