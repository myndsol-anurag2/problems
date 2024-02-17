import os
def get_filenames(filepath):
    for files in os.listdir(filepath):
        if os.path.isfile(files):
            print(files)
            
get_filenames('/home/anurag/workspace/')