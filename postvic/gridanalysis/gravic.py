import postvic as pv
import pandas as pd
from matplotlib import pyplot as plt


def gravic(gravic_list, modelroot, modelsettings, outputcoordi, prefix_dict):
    
    var = [item[0] for item in gravic_list]  # Extract variable names from gravic_list
    timescale = [item[1] for item in gravic_list]  # Extract timescale from gravic_list
    graphtype = [item[2].upper() for item in gravic_list]  # Extract graph type from gravic_list
    output_df = pv.readfiles.readgrid(modelroot, modelsettings, outputcoordi, prefix_dict, var)
    # make DATE column using YEAR, MONTH, DAY columns
    output_df['DATE'] = pd.to_datetime(output_df[['YEAR', 'MONTH', 'DAY']])
    # make DATE column as index
    output_df.set_index('DATE', inplace=True)
    
    for item in gravic_list:
        print(f"Processing {item[0]} with unit {item[1]} and type {item[2]}")
        
        if "D" in item[1]:
            # resample to daily values
            if 'VOLUME' in item[0]:
                # If the variable is a volume, sum the values for daily aggregation
                output_df = output_df.resample('D').sum()
            else:
                output_df = output_df.resample('D').mean()
        elif "M" in item[1]:
            # resample to monthly values
            if 'VOLUME' in item[0]:
                # If the variable is a volume, sum the values for monthly aggregation
                output_df = output_df.resample('ME').sum()
            else:
                output_df = output_df.resample('ME').mean()
        
        plt.figure()
        if "L" in item[2]:
            # make line plot
            plt.plot(output_df.index, output_df[item[0]], label=item[0])
            plt.xlabel('Time')
            plt.ylabel(f"{item[0]} ({item[1]})")
            plt.title(f"{item[0]} over Time")
            plt.legend()
            plt.grid()
            plt.show()
        elif "X" in item[2]:
            # make box plot
            plt.boxplot(output_df[item[0]])
            plt.ylabel(f"{item[0]} ({item[1]})")
            plt.title(f"{item[0]} Distribution")
            plt.show()
        elif "SC" in item[2]:
            # make scatter plot
            plt.scatter(output_df.index, output_df[item[0]])
            plt.xlabel('Time')
            plt.ylabel(f"{item[0]} ({item[1]})")
            plt.title(f"{item[0]} vs Time")
            plt.show()
        else:
            print(f"Unknown graph type: {item[2]}")
