#!/usr/bin/python
# -------------------------------------------------------------------
# @copyright 2017 DennyZhang.com
# Licensed under MIT
# https://raw.githubusercontent.com/DennyZhang/devops_public/master/LICENSE
##
# File : backup_docker_volumes.py
# Author : Denny <denny@dennyzhang.com>
# Description :
# Usage:
##            python /usr/sbin/backup_docker_volumes.py --docker_volume_list \
##               "cijenkins_volume_backup,cijenkins_volume_jobs,cijenkins_volume_workspace" \
# --volume_dir "/var/lib/docker/volumes" --backup_dir "/data/backup/"
# --
# Created : <2017-05-12>
# Updated: Time-stamp: <2017-05-22 17:11:54>
# -------------------------------------------------------------------
import os
import argparse
from datetime import datetime
import shutil

import logging
log_file = "/var/log/%s.log" % (os.path.basename(__file__).rstrip('\.py'))

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())


def get_backup_fname(backup_dir, volume_name):
    return "%s/%s-%s" % (backup_dir, volume_name,
                         datetime.now().strftime('%Y-%m-%d-%H%M%S'))


def get_size_mb(start_path='.'):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1000 * 1000)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        source = os.path.join(src, item)
        destination = os.path.join(dst, item)
        if os.path.isdir(source):
            # TODO: better way to copy while skip symbol links
            try:
                shutil.copytree(source, destination, symlinks, ignore)
            except shutil.Error:
                logging.exception(
                    'Warning: Some directories not copied under %s.', source)
            except OSError:
                logging.exception(
                    'Warning: Some directories not copied under %s.', source)
                # logging.warning('Some directories not copied. Error: %s' % e)
        else:
            shutil.copy2(source, destination)

##########################################################################


def backup_volume(volume_dir, volume_name, backup_dir):
    src_dir = "%s/%s" % (volume_dir, volume_name)
    dst_dir = get_backup_fname(backup_dir, volume_name)
    logging.info("Backup %s to %s.", src_dir, dst_dir)
    if os.path.exists(dst_dir) is False:
        os.makedirs(dst_dir)

    # run recursive backup
    copytree(src_dir, dst_dir)

    # TODO: trap the error message
    return True


if __name__ == '__main__':
    # get parameters from users
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--docker_volume_list',
        required=True,
        default=".*",
        help="The list of volumes to backup. Separated by comma",
        type=str)
    parser.add_argument(
        '--volume_dir',
        required=False,
        default="/var/lib/docker/volumes",
        help="The directory of the docker volumes",
        type=str)
    parser.add_argument('--backup_dir', required=False, default="/data/backup",
                        help="Where to store the backupsets", type=str)
    l = parser.parse_args()
    volume_dir = l.volume_dir
    backup_dir = l.backup_dir
    docker_volume_list = l.docker_volume_list

    # Create backup directory, if missing
    if os.path.exists(backup_dir) is False:
        logging.warning(
            "Warning: backup directory(%s) doesn't exist. Create it in advance.", backup_dir)
        os.makedirs(backup_dir)

    for volume_name in docker_volume_list.split(','):
        backup_volume(volume_dir, volume_name, backup_dir)

    # list folder size
    logging.info("List folders under %s.", backup_dir)
    logging.info("{0:70} {1}".format("Folder Name", "SIZE"))
    folder_list = sorted(os.listdir(backup_dir))
    for directory in folder_list:
        size_mb = get_size_mb("%s/%s" % (backup_dir, directory))
        logging.info(
            "{0:70} {1}MB".format(
                directory, str(
                    "{:10.2f}".format(size_mb))))
# File : backup_docker_volumes.py ends
