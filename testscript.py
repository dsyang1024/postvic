# test
# call library in the postvic package folder
import sys


sys.path.insert (0, '../postvic')
import postvic as pv


# default variables
modelroot = r"C:\Github\postvic\test" #for laptop
# modelroot = r"C:\Users\dsyan\Documents\Github\postvic\test" # for home desktop
globaldir = 'GLOBALFILES'


# first input is absolute path of the model root directory,
# second input is the direcotry of the global files from the root directory
# this function will bring all the model settings from the global files in the directory
# mendatory
modelsettingslist = pv.modelinfo.getmodelinfo(modelroot, globaldir)


# first input is absolute path of the model root directory,
# second input is the modelsettingslist from the previous function
# this function will check if the result directories exist, if not, it will remove the modelsettings from the list
# if the result directories exist, it will check if the output files exist, if not, it will print a message and exit
# optional
pv.modelinfo.getmodeldirs(modelroot, modelsettingslist)




# gridcell scale analysis, this function use the gridcell number given in the soil file listed in the global file
#! the given global file must be in the modelsettingslist, otherwise it will print a message and exit
# mendatory
globalfile = 'global_A_set_1_sub_1.txt'
cellnumber = 83861 # in int format, not string format


# get the valid file name of the output based on the global file and soil file to prevent errors.
# Three return values will be used in the next function to read the output files.
modelsettings, outputcoordi, prefix_dict = pv.gridanalysis.getfromglobal(modelroot, globalfile, cellnumber, modelsettingslist)


# list of graphs you want to make, the first column is the variable name, the second column is the unit, and the third column is the graph type.
# mendatory
gravic_list = [
    ["OUT_RUNOFF", "D", "L"],
    ["OUT_BASEFLOW", "D", "L"],
    ["OUT_DRAINFLOW", "D", "L"]
    ]
pv.gridanalysis.gravic(gravic_list, modelroot, modelsettings, outputcoordi, prefix_dict)
