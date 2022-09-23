#!/usr/bin/python3
# To execute in the scenario use below line
# script_exec -s /home/yce/config.py -o <node>
import pymysql
import sys

# Simple argument  validation
if(len(sys.argv) != 2):
    print("ERROR: c2_workaround.py Argument missing")
    exit()

# Arguments
hostname = sys.argv[1] # "CMDB"

# Global
host = 'localhost'
user = ''
password = ''
db = 'YCE'

_connection_dict = {
    'host': host,
    'user': user,
    'port': 3306,
    'password': password,
    'database': db,
}

_replace_list = [
    ["\n", ''],
    ["\r", ''],
    ["{", "\\{"],
    ["}", "\\}"],
]

def escape_template(output):
    for t in output:
        for f in _replace_list:
            t = str.replace(t, f[0], f[1])
        return(t)

def unescape_template(output):
    for t in output:
        for f in _replace_list:
            t = str.replace(t, f[1], f[0])
        return(t)

def connect(d):
    connection = pymysql.connect(binary_prefix=True, **d)
    return connection.cursor()

def q(session, query):
    session.execute(query)
    a = session.fetchone()
    if not a:
        return False
    else:
        return a

cursor = connect(_connection_dict)
query = '''SELECT Config_text FROM NCCM.Nccm_diff_all where Nccm_id in (
SELECT Max(Nccm_id) FROM NCCM.Nccm_diff_all WHERE Nodename LIKE '%s' );''' % (hostname)

# Get the template
output = q(cursor, query)
output = str(output)
output = output.split("\\n")
with open(hostname,"w") as f:
	for line in output:
		f.write(line.strip('+')+"\n")
		#print(line)

'''
if output:
    print(escape_template(output))
    #print(unescape_template(output))
else:
    print("ERROR: config %s not found" % hostname)
