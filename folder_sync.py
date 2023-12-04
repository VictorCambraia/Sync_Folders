import argparse
import filecmp
import shutil
import os
from datetime import date, datetime
import time


def sync_dirs(source, replica, log_path):

    dirs_cmp = filecmp.dircmp(source, replica) 
        
    # Create things from source to replica    
    for thing in dirs_cmp.left_only:

        thing_name = os.path.join(source, thing)
        copy_name = os.path.join(replica, thing)

        if os.path.isdir(thing_name):
            # shutil.copytree(thing_name, copy_name) # Not possible to log
            copy_dir(thing_name, copy_name, log_path)

        else:
            shutil.copy(thing_name, copy_name)
            log_sync(log_path, "create", copy_name)

    # Delete things that are not in source anymore
    for thing in dirs_cmp.right_only:

        thing_name = os.path.join(replica, thing)

        if os.path.isdir(thing_name):
            # shutil.rmtree(thing_name) # Not possible to log
            remove_dir(thing_name, log_path)

        else:
            os.remove(thing_name)
            log_sync(log_path, "delete", thing_name)

    # Update files that are not updated
    for file in dirs_cmp.diff_files + dirs_cmp.funny_files:

        file_name = os.path.join(source, file)
        copy_name = os.path.join(replica, file)

        os.remove(copy_name)
        shutil.copy(file_name, copy_name)
        log_sync(log_path, "update", copy_name)

    # Goes to other directories   
    for dir in dirs_cmp.common_dirs:

        dir_source = os.path.join(source, dir)
        dir_replica = os.path.join(replica, dir)

        sync_dirs(dir_source, dir_replica, log_path)

    return

def copy_dir(thing_name, copy_name, log_path):
    os.mkdir(copy_name)

    for root, dirs, files in os.walk(thing_name):
        for file in files:
            shutil.copy(os.path.join(thing_name, file), os.path.join(copy_name, file))
            log_sync(log_path, "create", os.path.join(copy_name, file))
        for dir in dirs:
            copy_dir(os.path.join(thing_name, dir), os.path.join(copy_name, dir), log_path)
    
    return

def remove_dir(thing_name, log_path):

    for root, dirs, files in os.walk(thing_name):
        for file in files:
            os.remove(os.path.join(thing_name, file))
            log_sync(log_path, "delete", os.path.join(thing_name, file))
        for dir in dirs:
            remove_dir(os.path.join(thing_name, dir), log_path)

    os.rmdir(thing_name)        
    return


def log_sync(log_path, type, file_path):

    f = open(log_path, "a")
    now = str(datetime.now())

    if type == "create":
        text = os.path.basename(file_path) + " file CREATED in the folder " + os.path.dirname(file_path) + " at the time " + now + "\n"

    elif type == "delete":
        text = os.path.basename(file_path) + " file DELETED from the folder " + os.path.dirname(file_path) + " at the time " + now + "\n"

    elif type == "update":
        text = os.path.basename(file_path) + " file UPDATED in the folder " + os.path.dirname(file_path) + " at the time " + now + "\n"

    f.write(text)
    f.close()

    print(text)
    return    


# Construct the argument parser
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument("-s", "--source", required=True, help="source path")
ap.add_argument("-r", "--replica", required=True, help="replica path")
ap.add_argument("-p", "--period", required=True, help="sync period")
ap.add_argument("-l", "--log", required=True, help="log file path")
args = vars(ap.parse_args())

# Get the arguments
source_path = str(args['source'])
replica_path = str(args['replica'])
log_path = str(args['log'])
sync_period = int(args['period'])

while True:
    sync_dirs(source_path, replica_path, log_path)

    # One of many ways to get sync periodically
    time.sleep(sync_period)

