#!/usr/bin/python
##-------------------------------------------------------------------
## @copyright 2015 DennyZhang.com
## File : detect_suspicious_process.py
## Author : DennyZhang.com <denny@dennyzhang.com>
## Description : http://www.dennyzhang.com/suspicious_process/
##        python ./detect_suspicious_process.py
##        python ./detect_suspicious_process.py --whitelist_file /tmp/whitelist.txt
## --
## Created : <2016-01-15>
## Updated: Time-stamp: <2017-05-22 17:11:52>
##-------------------------------------------------------------------
import argparse
import subprocess

################################################################################
# TODO: move to common library
def string_in_regex_list(string, regex_list):
    import re
    for regex in regex_list:
        regex = regex.strip()
        if regex == "":
            continue
        if re.search(regex, string) is not None:
            # print "regex: %s, string: %s" % (regex, string)
            return True
    return False

################################################################################
DEFAULT_WHITE_LIST = '''
/sbin/getty -.*
dbus-daemon .*
 acpid -c /etc/acpi/events -s /var/run/acpid.socket$
 atd$
 cron$
 /lib/systemd/systemd-udevd --daemon$
 /lib/systemd/systemd-logind$
 dbus-daemon --system --fork$
 /usr/sbin/sshd -D$
 rsyslogd$
 /usr/sbin/mysqld$
 /usr/sbin/apache2 -k start$
'''

COMMAND_GET_NONKERNEL = '''
sudo ps --ppid 2 -p 2 -p 1 --deselect \
-o uid,pid,rss,%cpu,command \
--sort -rss,-cpu
'''

def get_nonkernel_process():
    process_list = subprocess.check_output(COMMAND_GET_NONKERNEL, shell=True)
    return process_list

def load_whitelist(fname):
    if fname is None:
        print("No white list file is given. Use default value.")
        wlist = DEFAULT_WHITE_LIST
    else:
        print("load white list from %s" % fname)
        with open(fname) as current_file:
            wlist = current_file.readlines()
    return wlist

def list_process(process_list, white_list):
    tmp = []
    for line in process_list.split("\n"):
        line = line.strip()
        if line == "":
            continue
        if not string_in_regex_list(line, white_list.split("\n")):
            tmp.append(line)
    return tmp

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--whitelist_file', required=False,
                        help="config file for whitelist", type=str)
    args = parser.parse_args()
    white_list = load_whitelist(args.whitelist_file)
    nonkernel_process_list = get_nonkernel_process()
    process_list = list_process(nonkernel_process_list, white_list)

    # Remove header
    print("Identified processes count: %d." % (len(process_list) - 1))
    print("\n".join(process_list))
## File : detect_suspicious_process.py ends
