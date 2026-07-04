# test
# call library in the postvic package folder
import sys, os


sys.path.insert (0, '../postvic')
import postvic as pv



modelroot = r"C:\Users\dsyan\Documents\Github\postvic\test"
globaldir = 'GLOBALFILES'


# first input is absolute path of the model root directory,
# second input is the direcotry of the global files from the root directory
# this function will bring all the model settings from the global files in the directory
modelsettingslist = pv.modelinfo.getmodelinfo(modelroot, globaldir)


# first input is absolute path of the model root directory,
# second input is the modelsettingslist from the previous function
# this function will check if the result directories exist, if not, it will remove the modelsettings from the list
# if the result directories exist, it will check if the output files exist, if not, it will print a message and exit
pv.modelinfo.getmodeldirs(modelroot, modelsettingslist)


# gridcell scale analysis, this function use the gridcell number given in the soil file listed in the global file
# which global file your simulation used?
globalfile = 'global_A_set_1_sub_1.txt'
cellnumber = 83861 # in int format, not string format


# get the valid file name of the output based on the global file and soil file to prevent errors.
# Three return values will be used in the next function to read the output files.
modelsettings, outputcoordi, prefix_dict = pv.gridanalysis.getfromglobal(modelroot, globalfile, cellnumber, modelsettingslist)


# read the output file and return a dataframe with the variables you want to read.
var = ['OUT_RUNOFF', 'OUT_BASEFLOW', 'OUT_LAKE_VOLUME'] # var can be string or list of strings.
output_df = pv.readfiles.readgrid(modelroot, modelsettings, outputcoordi, prefix_dict, var)

# what do you want to do?
# make a line plot
# make a box plot



