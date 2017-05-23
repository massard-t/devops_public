#!/usr/bin/python
##-------------------------------------------------------------------
## @copyright 2017 DennyZhang.com
## Licensed under MIT
##   https://raw.githubusercontent.com/DennyZhang/devops_public/master/LICENSE
##
## File : git_pull_codedir.py
## Author : Denny <denny@dennyzhang.com>
## Description :
## Dependency:
##        pip install GitPython
## --
## Created : <2017-03-24>
## Updated: Time-stamp: <2017-05-22 17:12:13>
##-------------------------------------------------------------------
import os
import sys
import logging
import argparse
# Notice: Need to run: pip install GitPython
import git

log_file = "/var/log/%s.log" % (os.path.basename(__file__).rstrip('\.py'))
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())
SEPARATOR = ","

def git_pull(code_dir):
    logging.info("Run git pull in %s", code_dir)
    if os.path.exists(code_dir) is False:
        logging.error("Code directory(%s): doesn't exist", code_dir)
        sys.exit(1)
    os.chdir(code_dir)
    current_git = git.cmd.Git(code_dir)
    output = current_git.pull()
    return output

# Sample python git_pull_codedir.py --code_dirs "/data/code_dir/repo1,/data/code_dir/repo2"
if __name__ == '__main__':
    # TODO: Put code parsing in function
    parser = argparse.ArgumentParser()
    parser.add_argument('--code_dirs', required=True,
                        help="Code directories to pull. If multiple, separated by comma",
                        type=str)
    l = parser.parse_args()
    code_dirs = l.code_dirs

    for code_dir in code_dirs.split(SEPARATOR):
        git_output = git_pull(code_dir)
        if git_output == 'Already up-to-date.':
            has_changed = False
        else:
            has_changed = True
            logging.info("Code has changed in %s. Detail: %s" , code_dir, git_output)

    if git_output is True:
        sys.exit(1)
    else:
        sys.exit(0)
## File : git_pull_codedir.py ends
