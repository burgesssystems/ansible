#!/usr/bin/env python3.8

import json, os, socket, pprint, smtplib, requests
import pandas as pd
import argparse
import datetime

#from pandas.io.json import json_normalize
from pandas import json_normalize
from flatten_json import flatten

# Setup the CMK API endpoint
api_url_base = 'http://admin-cmk-01.root.local/cmkocisyd/check_mk/view.py'

# Setup the CMK authorisation header - this uses the automation user and secret key
headers = {
           'Authorization': f"Bearer automation XSHLLIWOHVHVAHLAWKAY",
            "Accept": "application/json",
            'Content-Type': 'application/json'}

# Passing in the AllHostsByGroup CMK view as the data source
params = {'filter': '', 'opthost_group': '', 'search': 'Search', 'view_name': 'AllHostsByGroup', 'output_format': 'json', '_username': 'automation', '_secret': 'XSHLLIWOHVHVAHLAWKAY'}

response = requests.get(api_url_base, headers=headers, params=params)

response_dict = json.loads(response.text)

# Generating a Pandas DataFrame from the returned JSON data
df = pd.DataFrame(response_dict, columns= ['hg_name','host','labels'])

df = df.drop(df[df.hg_name == "hg_name"].index)

params = {'filter': '', 'opthost_group': '', 'search': 'Search', 'view_name': 'AllHostLabels', 'output_format': 'json', '_username': 'automation', '_secret': 'XSHLLIWOHVHVAHLAWKAY'}

response = requests.get(api_url_base, headers=headers, params=params)

response_dict = json.loads(response.text)

df_labels = pd.DataFrame(response_dict, columns= ['host','labels'])
df_labels = df_labels.drop(0)

#print(df_labels)
#df_hosts.drop_duplicates(["host","labels"])
#df_hosts = df_hosts.sort_index()
#df_hosts['host'].drop_duplicates().sort_values()
#print(df_hosts.to_string())


# Grouping the hosts by CMK host group
df_grouped = df.groupby('hg_name')

print('{')

# Output the _meta element to improve performance
print('    "_meta": {')
print('        "hostvars": {')
host_cnt = 1
for row_index, row in df_labels.iterrows():
    cmk_host = row['host']
    cmk_labels = row['labels']
    label_cnt = 1
    if row['labels']:
        for key,value in cmk_labels.items():
            if 'domainname' in str(key):
                host_domainname = value
        print('            "' + cmk_host + '.' + host_domainname + '": {')
        #print(cmk_labels)
        #if cmk_host == "evttsdb01":
            #print(cmk_host)
            #print(cmk_labels.items())
        for key,value in cmk_labels.items():
                #print(cmk_host)
            if label_cnt < len(cmk_labels):
                print('                "' + str(key) + '": [')
                print('                    "' + str(value) + '"' )
                print('                ],')
            else:
                print('                "' + str(key) + '": [')
                print('                    "' + str(value) + '"' )
                print('                ]')
                print('                ')



            #if label_cnt < len(cmk_labels):
            #    print('                "' + str(key) + '" : [')
            #    print('                    "' + str(value) + '",' )
            #else:
            #    print('                "' + str(key) + '" : [')
            #    print('                    "' + str(value) + '"' )
            #print('                ]')
            label_cnt = label_cnt + 1
    if host_cnt < len(df_labels):
        print('            },')
    else:
        print('            }')
    #print(label_cnt)
    host_cnt = host_cnt + 1
    #print('            },')
            #print("value:" + str(value))
            #if 'ORACLE_SID' in str(key):
            #    oracle_sid = value
            #    print(oracle_sid)

print('        }')
print('    },')
# For each CMK host group we loop through the hosts and generate the JSON in ansible format
grp_cnt = 1
for group_name, df_group in df_grouped:

    if group_name != "hosts":
        print('    ' + '"' +  group_name + '"' + ':{')
        print('        "hosts":[')
    else:
        print('    ' + '"' +  group_name + '"' + ':[')
    # Setup the record iterator for the host group - required for the JSON formatting when multiple hosts in group
    row_cnt = 1
    # Loop through each row in the host group and extract the hostname and CMK host labels
    for row_index, row in df_group.iterrows():
        # Setup the output values for the hostname and labels
        cmk_host = row['host']
        cmk_labels = row['labels']
        # Extact the domainname label where it exists
        for key,value in cmk_labels.items():
            if 'domainname' in str(key):
                host_domainname = value
        # Format the hostname as fully qualified hostname if the domain exists
        if host_domainname:
            host_value = cmk_host + '.' + host_domainname
        else:
            host_value = cmk_host
        # Generate host JSON for each host
        if row_cnt < len(df_group):
            print('            "' + host_value + '",')
        else:
            print('            "' + host_value + '"')
        row_cnt = row_cnt + 1
        host_domainname = ''
    row_cnt = 0
    if group_name != "hosts":
        print('        ]')
        if grp_cnt < len(df_grouped):
            print('    },')
        else:
            print('    }')
        grp_cnt = grp_cnt + 1
    else:
        print('            ],')

print('}')


if_grouped = df.groupby('hg_name')

