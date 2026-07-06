import os
import pandas as pd

def readgrid(modelroot, modelsettings, outputcoordi, prefix_dict, var):
    """
    Read grid output files based on the provided model settings and output coordinates.

    Parameters:
    modelroot (str): The absolute path of the model root directory.
    modelsettings (dict): A dictionary containing model settings for the current global file.
    outputcoordi (str): The output coordinate string derived from the soil file.
    prefix_dict (dict): A dictionary mapping output prefixes to their corresponding parameters.
    var (string/list): A string or list(if multiple) of variables to read from the output files.

    Returns:
    None
    """
    
    outputdir = os.path.join(modelroot, modelsettings['RESULT_DIR'])
    # is var list or str?
    if isinstance(var, str):
        var = [var]
    var = _findprefixforvar(var, prefix_dict)
    
    merged_df = pd.DataFrame()
    for prefix in var:
        print (f"Reading output file for prefix: {prefix} and variables: {var[prefix]}")
        outputfile_path = os.path.join(modelroot, modelsettings['RESULT_DIR'], f"{prefix}_{outputcoordi}")
        var_df = _gettimeseries(outputfile_path, var[prefix], modelsettings)
        # concat the var_df to merged_df with matching "YEAR", "MONTH", "DAY" and "HOUR" columns
        if merged_df.empty:
            merged_df = var_df
        else:
            merged_df = pd.merge(merged_df, var_df, on=['YEAR', 'MONTH', 'DAY'] + (['HOUR'] if int(modelsettings['OUT_STEP']) < 24 else []), how='outer')
    
    return merged_df    
    
    
def _findprefixforvar(var, prefix_dict):    
    # using prefix_dict, find the output prefix for each variable in var, and read the corresponding output file
    # make var list component as dictionary with key as prefix and value as variable name {prefix: [variable1, variable2, ...]}
    var_dict = {}
    for variable in var:
        prefix = next((k for k, v in prefix_dict.items() if variable in v), None)
        if prefix is None:
            raise ValueError(f"The variable {variable} is not found in the prefix dictionary.")
        if prefix not in var_dict:
            var_dict[prefix] = []
        var_dict[prefix].append(variable)
    return var_dict


def _gettimeseries(outputfile_path, variables, modelsettings):
    # read the output file and find the column index of the variable
    if modelsettings['PRT_HEADER'] == 'TRUE':
        output_df = pd.read_csv(outputfile_path, sep='\s+', skiprows=5, header=0, low_memory=False)
        # column change due to the \# in the header.
        col_list = list(output_df.columns)[1:]
        # drop the last column which is empty
        output_df = output_df.drop(columns=output_df.columns[-1])
        output_df.columns = col_list
        # print (output_df.head())
    else:
        output_df = pd.read_csv(outputfile_path, sep='\s+', header=None, low_memory=False)

    # extract YEAR, MONTH, DAY columns and HOUR if TIME_STEP is less than 24 hours, and variable column
    target_columns = ['YEAR', 'MONTH', 'DAY']
    if int(modelsettings['OUT_STEP']) < 24:
        target_columns.append('HOUR')
    target_columns.extend(variables)
    var_series = output_df[target_columns]
    # print (var_series.head())
    return var_series
