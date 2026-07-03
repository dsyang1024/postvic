import os


# directory of the output files
cl_output_dir = "/home/yang2309/Desktop/WBS_prac/WABASH_CL/OUTPUTS/"
my_output_dir = "/home/yang2309/Desktop/Thesis/chapter1/SCENARIOS/OUTPUTS_No_Pond/"
# compare the number of output files
cl_files = os.listdir(cl_output_dir)
my_files = os.listdir(my_output_dir)
# if in the my_files, leave names only contains 'fluxes'
my_files = [f for f in my_files if 'fluxes' in f]

if len(cl_files) != len(my_files):
    print("The number of output files are different!")
else:
    print("The number of output files are the same as", len(cl_files))

# check cl_files and my_files are identical or not and if not, print the different names
cl_files_set = set(cl_files)
my_files_set = set(my_files)
if cl_files_set == my_files_set:
    print("The simulated grids are identical.")
else:
    print("The simulated grids are different.")
    print("Files in CL but not in my output:", cl_files_set - my_files_set)
    print("Files in my output but not in CL:", my_files_set - cl_files_set)

idtcl = 0
# read individual files and compare the contents.
for f in cl_files:
    with open(os.path.join(cl_output_dir, f), 'r') as cl_file:
        cl_content = cl_file.read()
    with open(os.path.join(my_output_dir, f), 'r') as my_file:
        my_content = my_file.read()
    if cl_content == my_content:
        print("File", f, "is identical.")
        idtcl += 1
    
print (f"Total identical files: {idtcl} out of {len(cl_files)}")