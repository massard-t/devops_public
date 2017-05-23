#!/usr/bin/python
##-------------------------------------------------------------------
## @copyright 2017 DennyZhang.com
## Licensed under MIT
##   https://raw.githubusercontent.com/DennyZhang/devops_public/master/LICENSE
##
## File : cleanup_old_files.py
## Author : Denny <denny@dennyzhang.com>
## Created : <2017-05-03>
## Updated: Time-stamp: <2017-05-22 17:11:43>
## Description :
##    Remove old files in a safe and organized way
## Sample:
##    # Remove files: Check /opt/app and remove files naming "app-.*-SNAPSHOT.jar". But keep latest 2 copies
##    python cleanup_old_files.py --working_dir "/opt/app" --filename_pattern "app-.*-SNAPSHOT.jar" \
##               --cleanup_type file --min_copies 3 --min_size_kb 10240
##
##    # Only list delete candidates, instead of perform the actual changes
##    python cleanup_old_files.py --working_dir "/opt/app" --filename_pattern "app-.*-SNAPSHOT.jar" \
##               --examine_only
##
##    # Remove files: Only cleanup files over 200MB
##    python cleanup_old_files.py --working_dir "/opt/app" --filename_pattern "app-.*-SNAPSHOT.jar" \
##               --cleanup_type file --min_size_kb 204800
##
##    # Remove folders: Cleanup subdirectories, keeping latest 2 directories
##    python cleanup_old_files.py --working_dir "/opt/app" --filename_pattern ".*" --cleanup_type directory
##-------------------------------------------------------------------
import os
import sys
import argparse
import re
import shutil

import logging
log_file = "/var/log/%s.log" % (os.path.basename(__file__).rstrip('\.py'))

logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())

def get_size_mb(start_path = '.'):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size/(1000*1000)

def list_old_files(files, min_copies, min_size_kb):
    tmp = []
    files.sort(key=os.path.getmtime, reverse=True)
    i = 0
    for current_file in files:
        if os.path.isfile(current_file) is False:
            continue
        # skip too small files
        filesize_kb = os.stat(f).st_size/1000
        if filesize_kb < min_size_kb:
            continue
        i = i + 1
        if i > min_copies:
            tmp.append(f)
    return tmp

def list_old_folders(files, min_copies):
    tmp = []
    files.sort(key=os.path.getmtime, reverse=True)
    i = 0
    for current_file in files:
        if os.path.isdir(current_file) is False:
            continue
        i += 1
        if i > min_copies:
            tmp.append(current_file)
    return tmp

if __name__ == '__main__':
    # get parameters from users
    # TODO: Put args checking in function
    parser = argparse.ArgumentParser()
    parser.add_argument('--working_dir', required=True,
                        help="Perform cleanup under which directory", type=str)
    parser.add_argument('--examine_only', dest='examine_only', action='store_true', default=False,
                        help="Only list delete candidates, instead perform the actual removal")
    parser.add_argument('--filename_pattern', required=False, default=".*",
                        help="Filter files/directories by filename, before cleanup", type=str)
    parser.add_argument('--cleanup_type', required=False, default='file',
                        help="Whether to perform the cleanup for files or directories", type=str)
    parser.add_argument('--min_copies', default=3, required=False,
                        help='minimal copies to keep, before removal.', type=int)
    parser.add_argument('--min_size_kb', default=100, required=False,
                        help='When remove files, skip files too small. It will\
                        be skipped when removing directories', type=int)
    l = parser.parse_args()

    working_dir = l.working_dir
    examine_only = l.examine_only
    cleanup_type = l.cleanup_type.lower()
    filename_pattern = l.filename_pattern
    min_copies = l.min_copies
    min_size_kb = l.min_size_kb

    logging.info("Start to run cleanup for folder: %s." % working_dir)
    if os.path.exists(working_dir) is False:
        logging.warning("Directory(%s) doesn't exists." % (working_dir))
        sys.exit(0)

    os.chdir(working_dir)
    files = [f for f in os.listdir(".") if re.search(filename_pattern, f)]
    logging.info("List all matched entries:")
    for f in files:
        size_mb = get_size_mb(f)
        logging.info("%s\t%sM" % (f, "{:10.2f}".format(size_mb)))

    if cleanup_type == 'file':
        l = list_old_files(files, min_copies, min_size_kb)
    else:
        l = list_old_folders(files, min_copies)

    if l == []:
        logging.info("No matched files/directories to be removed.")
        sys.exit(0)
    else:
        if examine_only is True:
            logging.info("Below files/directories are selected to be removed: %s.\n"\
                         "Skip following removal, since --examine_only has\
                         already been given.", ",".join(l))
            sys.exit(0)
        else:
            # Perform the actual removal
            for f in l:
                if cleanup_type == 'file':
                    logging.info("REMOVE file. %s/%s" % (working_dir, f))
                    os.remove(f)
                else:
                    logging.info("REMOVE folder: %s/%s" % (working_dir, f))
                    # TODO: error handling
                    shutil.rmtree(f)
            logging.info("Cleanup is done.")
## File : cleanup_old_files.py ends
