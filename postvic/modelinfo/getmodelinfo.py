import os, copy


def getmodelinfo(modelroot, globalfilesdir):
    """_summary_
    This function reads global files from the specified directory, retrieves the list of global files, and extracts model settings from each global file.

    Args:
        modelroot (str): The absolute path of the model root directory.
        globalfilesdir (str): The directory of the global files relative to the modelroot directory.

    Returns:
        _list_: _list of dictionaries containing model settings for each global file_
    """
    globalfilesdir = os.path.join(modelroot, globalfilesdir)
    _readglobals(globalfilesdir)
    globallist = _getglobalfiles(globalfilesdir)
    modelsettingslist = _getmodelsettings(globallist)
    return modelsettingslist



def _readglobals(globalfilesdir):
    """
    Read global files from the specified directory.
    
    Parameters:
    globalfilesdir (str): The directory name of the global files.
    
    Returns:
    None
    """
    # Implementation of reading global files goes here
    # check the directory exists
    if not os.path.isdir(globalfilesdir):
        raise ValueError(f"The directory {globalfilesdir} does not exist.")
    else:
        print(f"Reading global files from directory: {globalfilesdir}")
        
        
def _getglobalfiles(globalfilesdir):
    globallist = os.listdir(globalfilesdir)
    print (f"{len(globallist)} global files found in {globalfilesdir}")
    # make global file list with only with the name of files in the directory
    globallist = [os.path.join(globalfilesdir, f) for f in globallist if os.path.isfile(os.path.join(globalfilesdir, f))]
    # globallist = [globalfilesdir + "/" + f for f in globallist]
    return globallist


def _getmodelsettings(globallist):
    modelsettingslist = []
    for globalfile_path in globallist:
        modelsettings = {}
        modelsettings['globalfiles'] = globalfile_path
        # print (f'\n  GLOBALFILE       : {modelsettings["globalfiles"]}')
        par_list = ['STARTYEAR', 'STARTMONTH', 'STARTDAY', 'ENDYEAR', 'ENDMONTH', 'ENDDAY',
                    'LAKES', 'MONTHLY_CONTROL', 'WITHDRAWAL',
                    'NLAYER', 'SOIL', 'VEGPARAM', 'VEGLIB', 'FORCING1',
                    'RESULT_DIR', 'N_OUTFILES', 'OUTFILE', 'PRT_HEADER', 'TIME_STEP', 'OUT_STEP']
        for par in par_list:
            value = __findparameterinfile(globalfile_path, par)
            if value is not None:
                # print(f"  {par:<16} : {value}")
                modelsettings[par] = value
        modelsettingslist.append(modelsettings)
        
        # export the modelsettingslist to one csv file, each row is one modelsettings, each column is one parameter
        # if the parameter is list format, convert it to string format with '/' as separator
        writesettingslist = copy.deepcopy(modelsettingslist)
        for modelsettings in writesettingslist:
            for key, value in modelsettings.items():
                if isinstance(value, list):
                    modelsettings[key] = '/'.join(value)
        import csv
        csv_file = 'modelsettingslist.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=writesettingslist[0].keys())
            writer.writeheader()
            writer.writerows(writesettingslist)

        
    return modelsettingslist


def __findparameterinfile(globalfile_path,parameter_name):
    """
    Find the value of a parameter in a file. in the file, parameter value is always the next value after the parameter name
    
    Parameters:
    globalfile_path (str): The path to the global file.
    parameter_name (str): The name of the parameter to find.
    
    Returns:
    str: The value of the parameter if found, otherwise None.
    """
    with open(globalfile_path, 'r') as file:
        if parameter_name != "OUTFILE":
            for line in file:
                if line.startswith(parameter_name):
                    # split the line with whitespace
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]  # Return the value after the parameter name
        else:
            lines = [line for line in file.readlines() if line.startswith(parameter_name)]
            outfile_names = []
            for line in lines:
                parts = line.split()
                if len(parts) > 1:
                    outfile_names.append(parts[1])  # Collect all outfile names
            return outfile_names  # Return the list of outfile names
    return None




