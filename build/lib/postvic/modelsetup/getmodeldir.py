# get the directory of the model simulation
def get_model_dir():
    import os
    import sys

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory (model directory)
    model_dir = os.path.dirname(script_dir)

    return model_dir