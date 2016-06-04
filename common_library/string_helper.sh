#!/bin/bash -e
##-------------------------------------------------------------------
## @copyright 2016 DennyZhang.com
## Licensed under MIT
##   https://raw.githubusercontent.com/DennyZhang/devops_public/master/LICENSE
##
## File : string_helper.sh
## Author : Denny <denny@dennyzhang.com>
## Description :
## --
## Created : <2016-01-08>
## Updated: Time-stamp: <2016-06-04 11:36:17>
##-------------------------------------------------------------------
function source_string() {
    # Global variables needed to enable the current script
    local env_parameters=${1?}
    IFS=$'\n'
    for env_variable in $env_parameters; do
        eval "$env_variable"
    done
    unset IFS
}

function remove_hardline() {
    # handle \n\r of Windows OS
    local str=$*
    echo "$str" | tr -d '\r'
}

function string_strip_whitespace() {
    # handle \n\r of Windows OS
    local str=$*
    str=$(echo "${str}" |sed -e 's/^[ \t]*//g')
    str=$(echo "${str}" |sed -e 's/[ \t]*$//g')
    echo "$str"
}

function string_strip_comments() {
    local my_str=${1?}
    my_str=$(echo "$my_str" | grep -v '^ *#')
    echo "$my_str"
}

function parse_ip_from_string() {
    # get ip addresses from string
    # Sample: 
        # parse_ip_from_string "{ 'common_basic':
        #        {
        #        # service hosts: deploy service to which host
        #        'couchbase_hosts':['172.17.0.2', '172.17.0.3'],
        #        'elasticsearch_hosts':['172.17.0.2', '172.17.0.3'],
        #        'mdm_hosts':['172.17.0.3', '172.17.0.4'],
        #        'haproxy_hosts':['172.17.0.2','172.17.0.3'],
        #        'nagios_server':'172.17.0.4',"
    # -->
    #      172.17.0.2
    #      172.17.0.3
    #      172.17.0.4
    local my_str=${1?}
    echo -e "$my_str" | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | sort | uniq
}
######################################################################
## File : string_helper.sh ends