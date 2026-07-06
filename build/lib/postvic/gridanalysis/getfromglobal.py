import os
import pandas as pd


def getfromglobal(modelroot, globalfile, cellnumber, modelsettingslist):
    """
    This function reads the output files for a specific grid cell from the specified global file and returns the data as a dictionary.

    Args:
        modelroot (str): The absolute path of the model root directory.
        globalfile (str): The name of the global file to read.
        cellnumber (int): The grid cell number to extract data for.
        modelsettingslist (list): A list of model settings.

    Returns:
        tuple: A tuple containing the output coordinates and a dictionary of output prefixes.
            - outputcoordi (str): The output coordinates for the specified grid cell.
            - prefix_dict (dict): A dictionary containing output prefixes and their corresponding parameters.
    """
    cdir = os.getcwd()
    os.chdir(modelroot)
    modelsettings = next((ms for ms in modelsettingslist if os.path.basename(ms['globalfiles']) == globalfile), None)
    if modelsettings is None:
        raise ValueError(f"The global file {globalfile} is not found in the modelsettingslist.")

    outputcoordi = _findoutputcoordi(modelroot, cellnumber, modelsettings)
    prefix_dict = _findoutputprefix(modelsettings['globalfiles'])
    
    return modelsettings, outputcoordi, prefix_dict


    
def _findoutputcoordi(modelroot, cellnumber, modelsettings):
        
    # check if the globalfile is in the modelsettingslist
    globalfile_path = modelsettings.get('globalfiles')
    # get the modelsetting for the globalfile
    
    output_path = os.path.join(modelroot, modelsettings.get('RESULT_DIR'))
    
    # read soil file to get the output file name
    soilfile = modelsettings.get('SOIL')
    
    # read the soil file to get the output file name in dataframe format
    soil_df = pd.read_csv(soilfile, sep='\s+', header=None)
    
    # find the row with the cellnumber with the first column equal to 1
    soil_row = soil_df[(soil_df[0] == 1) & (soil_df[1] == cellnumber)]
    if soil_row.empty:
        raise ValueError(f"The cell number {cellnumber} is not found or not active in the soil file {soilfile}.")
    else:
        # get the output file name from the soil_row
        outputcoordi = f"{soil_row.iloc[0, 2]}_{soil_row.iloc[0, 3]}"
        # print (f"Output coordinate for cell number {cellnumber} is {outputcoordi}.")
        
    return outputcoordi


def _findoutputprefix(globalfile_path):
    # print (f"Finding output prefix for global file {globalfile_path}.")
    # read the global file and find the line index where N_OUTFILES is defined
    with open(globalfile_path, 'r') as globalfile:
        globalfile = globalfile.readlines()
        
    # find the indeces of the line where 'OUTFILE' is defined
    outfile_indices = [i for i, line in enumerate(globalfile) if line.startswith('OUTFILE')]
    outfile_indices.extend([len(globalfile)])  # add the end of the file as the last index
    # print (f"OUTFILE indices are {outfile_indices}.")
    # between the index ahead and the next index, the line is the output parameters, assign them to each output prefix {prefix:[parameter1, parameter2, ...], prefix2:[parameter1, parameter2, ...], ...} format
    prefix_dict = {}
    for i in range(len(outfile_indices)-1):
        prefix = globalfile[outfile_indices[i]].split()[1]
        output_parameters = [line.split()[1] for line in globalfile[outfile_indices[i]+1:outfile_indices[i+1]] if line.startswith('OUTVAR')]
        prefix_dict[prefix] = output_parameters
    # print (f"Output prefix dictionary is {prefix_dict}.")
    
    return prefix_dict





