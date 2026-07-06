import os, sys

def getmodeldirs(modelroot,modelsettingslist):
    """_summary_
    This function checks if the result directories exist, if not, it will remove the modelsettings from the list
    if the result directories exist, it will check if the output files exist, if not, it will print a message and exit
    Args:
        modelroot (_string_): _absolute path of the model root directory_
        modelsettingslist (_list_): _list of model settings in dictionary format_
    """
    cdir = os.getcwd()
    os.chdir(modelroot)
    modelsettingslist = _varifydirs(modelsettingslist)
    _gridcount(modelsettingslist)
    os.chdir(cdir)
    
    
def _varifydirs(modelsettingslist):
    # check if the directories exist, if not, remove the modelsettings from the list
    temp = []
    for modelsetting in modelsettingslist:
        result_dir = modelsetting.get('RESULT_DIR') if modelsetting.get('RESULT_DIR') else None
        # print(f"Checking directory: {result_dir}")
        if result_dir and not os.path.isdir(result_dir):
            print(f"Directory {result_dir} does not exist. Removing model settings from the list.")
            sys.exit(1)
        else:
            temp.append(modelsetting)
            # print(f"Directory {result_dir} exists.")
    return temp


def _gridcount (modelsettingslist):
    # count the number of grids of each global file using the soil file
    for modelsetting in modelsettingslist:
        outputslist = os.listdir(modelsetting.get("RESULT_DIR"))
        soilfile = modelsetting.get("SOIL") if modelsetting.get("SOIL") else None
        # read the soil file
        with open(soilfile, 'r') as f:
            lines = f.readlines()
            total_soil = len(lines)
            active_soil = 0
            for line in lines:
                if line.startswith('1'):
                    parts = line.split()
                    # check if the output files exist in the result directory
                    for name in modelsetting.get("OUTFILE"):
                        if f'{name}_{parts[2]}_{parts[3]}' not in outputslist:
                            print (f"Output file {modelsetting.get('RESULT_DIR')}/{name}_{parts[2]}_{parts[3]} is missing.")
                            sys.exit(1)
                    active_soil += 1
        # print (f"  {modelsetting.get('globalfiles')} has {active_soil}/{total_soil} active")
                        
        

        
