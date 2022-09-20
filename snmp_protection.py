# Hostname is the input for this file.. 
# This file would fetch the configuration and then look for any lines with snmp-community that don't have ACL attached to it..
import sys
import re

regex = '^[0-9]+$'
not_digit=0
def check(string):
      # pass the regular expression
     # and the string in search() method
    if not (re.search(regex, string)):
        not_digit = 1

host = sys.argv[1]

with open("/opt/yce/"+host,"r") as f:
        config = f.readlines()
        for line in config:
                if "snmp-server community" in line:
                        acl_no = line.split()[-1]
                        check(acl_no)

if not_digit == 1:
        print('No')
else:
        print('Yes')
