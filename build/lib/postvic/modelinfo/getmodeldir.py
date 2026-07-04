def getmodeldir(globalfilesdir):
    # get the directory of the model simulation
    import os
    import sys
    # check the given directory exists
    if not os.path.exists(globalfilesdir):
        print("The given directory does not exist: " + globalfilesdir)
        sys.exit(1)