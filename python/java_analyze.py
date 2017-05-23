#!/usr/bin/python
##-------------------------------------------------------------------
## File : java_analyze.py
## Description :
## --
## Created : <2017-01-25>
## Updated: Time-stamp: <2017-05-22 17:12:19>
##-------------------------------------------------------------------
import sys
import os
import argparse
import json
import requests

################################################################################
# Common functions
def analyze_gc_logfile(gc_logfile, apikey):
    print("Call rest api to parse gc log: http://www.gceasy.io.")

    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    url = "http://api.gceasy.io/analyzeGC?apiKey=%s" % (apikey)
    res = requests.post(url, data=open(gc_logfile, "r"), headers=headers)

    if res.status_code != 200:
        print("ERROR: http response is not 200 OK. status_code: %d. content: %s..."
              % (res.status_code, res.content[0:40]))
        return False

    content = res.content
    loaded = json.loads(content)
    print("graphURL: %s" % (loaded["graphURL"]))

    if '"isProblem":true' in content:
        print("ERROR: problem is found.")
        return False

    return True

def analyze_jstack_logfile(jstack_logfile, apikey, min_runnable_percentage):
    print("Call rest api to parse java jstack log: http://www.fastthread.io.")

    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    url = "http://api.fastthread.io/fastthread-api?apiKey=%s" % (apikey)
    res = requests.post(url, data=open(jstack_logfile, "r"), headers=headers)

    if res.status_code != 200:
        print("ERROR: http response is not 200 OK. status_code: %d. content: %s..."
              % (res.status_code, res.content[0:40]))
        return False

    content = res.content
    loaded = json.loads(content)
    threadstate = loaded["threadDumpReport"][0]["threadState"]
    threadcount_runnable = int(threadstate[0]["threadCount"])
    threadcount_waiting = int(threadstate[1]["threadCount"])
    threadcount_timed_waiting = int(threadstate[2]["threadCount"])
    threadcount_blocked = int(threadstate[3]["threadCount"])

    print("%d threads in RUNNABLE, %d in WAITING, %d in TIMED_WAITING, %d in BLOCKED."
          % (threadcount_runnable, threadcount_waiting,
             threadcount_timed_waiting, threadcount_blocked))
    print("graphURL: %s" % (loaded["graphURL"]))
    threadcount_total = threadcount_runnable + threadcount_waiting + \
                        threadcount_timed_waiting + threadcount_blocked
    if (float(threadcount_runnable)/threadcount_total) < min_runnable_percentage:
        print("ERROR: only %s threads are in RUNNABLE state. Less than %s." %
              ("{0:.2f}%".format(float(threadcount_runnable)*100/threadcount_total),
               "{0:.2f}%".format(min_runnable_percentage*100)))
        return False

    return True

################################################################################
## Generate gc log: start java program with -Xloggc enabled
## Generate java jstack log: jstack -l $java_pid
##
## Sample: Run with environment variables.
##
##   # analyze gc logfile:
##   export JAVA_ANALYZE_ACTION="analyze_gc_logfile"
##   export JAVA_ANALYZE_LOGFILE="/tmp/gc.log"
##   export JAVA_ANALYZE_APIKEY="29792f0d-5d5f-43ad-9358..."
##   curl -L https://raw.githubusercontent.com/TOTVS/.../java_analyze.py | bash
##
##   # analyze jstack logfile:
##   export JAVA_ANALYZE_ACTION="analyze_jstack_logfile"
##   export JAVA_ANALYZE_LOGFILE="/tmp/jstack.log"
##   export JAVA_ANALYZE_APIKEY="29792f0d-5d5f-43ad-9358..."
##   curl -L https://raw.githubusercontent.com/TOTVS/.../java_analyze.py | bash
##
## Sample: Run with argument parameters.
##   python ./java_analyze.py --action analyze_gc_logfile \\
##            --logfile /tmp/gc.log --apikey "29792f0d..."
##   python ./java_analyze.py --action analyze_jstack_logfile \
##            --logfile /tmp/jstack.log --apikey "29792f0d..."
##
if __name__ == '__main__':
    # TODO: put parsing outside of main
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', default='', required=False,
                        help="Supported action: analyze_gc_logfile or analyze_jstack_logfile",
                        type=str)
    parser.add_argument('--logfile', default='', required=False,
                        help="Critical log file to parse", type=str)
    parser.add_argument('--apikey', default='', required=False,
                        help="API key to call gceasy.io and fastthread.io",
                        type=str)
    parser.add_argument('--minrunnable', default=0.40, required=False,
                        help="If too many threads are not in RUNNABLE state, we raise alerts",
                        type=float)

    ARGS = parser.parse_args()
    ACTION = ARGS.action
    LOGFILE = ARGS.logfile
    APIKEY = ARGS.apikey
    # Get parameters via environment variables, if missing
    if ACTION == "" or ACTION is None:
        ACTION = os.environ.get('JAVA_ANALYZE_ACTION')
    if LOGFILE == "" or LOGFILE is None:
        LOGFILE = os.environ.get('JAVA_ANALYZE_LOGFILE')
    if APIKEY == "" or APIKEY is None:
        APIKEY = os.environ.get('JAVA_ANALYZE_APIKEY')

    # input parameters check
    if ACTION == "" or ACTION is None:
        print("ERROR: mandatory parameter of action is not given.")
        sys.exit(1)
    if LOGFILE == "" or LOGFILE is None:
        print("ERROR: mandatory parameter of logfile is not given.")
        sys.exit(1)
    if APIKEY == "" or APIKEY is None:
        print("ERROR: mandatory parameter of apikey is not given.")
        sys.exit(1)

    ############################################################################
    # main logic
    if ACTION == "analyze_gc_logfile":
        if analyze_gc_logfile(LOGFILE, APIKEY) is False:
            print("ERROR: problems are detected in gc log(%s)." % (LOGFILE))
            sys.exit(1)
        else:
            print("OK: no problem found when parsing gc log(%s)." % (LOGFILE))
    elif ACTION == "analyze_jstack_logfile":
        if analyze_jstack_logfile(LOGFILE, APIKEY, ARGS.minrunnable) is False:
            print("ERROR: problems are detected in jstack log(%s)." %
                  (LOGFILE))
            sys.exit(1)
        else:
            print("OK: no problem found when parsing jstack log(%s)." %
                  (LOGFILE))
    else:
        print("ERROR: not supported action(%s)." % (ACTION))
        sys.exit(1)
## File : java_analyze.py ends
