import postvic as pv


def gravic(gravic_list, modelroot, modelsettings, outputcoordi, prefix_dict):
    
    var = [item[0] for item in gravic_list]  # Extract variable names from gravic_list
    timescale = [item[1] for item in gravic_list]  # Extract timescale from gravic_list
    graphtype = [item[2] for item in gravic_list]  # Extract graph type from gravic_list
    output_df = pv.readfiles.readgrid(modelroot, modelsettings, outputcoordi, prefix_dict, var)
    
    
    for item in gravic_list:
        print(f"Processing {item[0]} with unit {item[1]} and type {item[2]}")
        