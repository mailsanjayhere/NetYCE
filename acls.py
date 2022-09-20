# This script looks for the standard/extended acls, prefix-lists.
# Lists out them if they are used or not used...
# If they are called and not created yet.. will notify those as well
import sys

host = sys.argv[1]
type = sys.argv[2]
acls = []
used_acls = []
with open("/opt/yce/"+host,"r") as f:
        config = f.readlines()
        for line in config:
                if "access-list" in line:
                        words = line.split()
                        i = words.index("access-list")
                        if (words[i+1] == "standard") or (words[i+1] == "extended"):
                                if words[i+2] not in acls:
                                        acls.append(words[i+2])
                        else:
                                if words[i+1] not in acls:
                                        acls.append(words[i+1])
                if "ip prefix-list" in line:
                        words = line.split()
                        if words[2] not in acls:
                                acls.append(words[2])
                elif "access-class" in line:
                        words = line.split()
                        i = words.index("access-class")
                        if words[i+1] not in used_acls:
                                used_acls.append(words[i+1])
                elif "access-group" in line and not "access-group name" in line:
                        words = line.split()
                        i = words.index("access-group")
                        if words[i+1] not in used_acls:
                                used_acls.append(words[i+1])
                elif ("match as-path" in line ) or ("match ip next-hop" in line) or ("snmp-server community" in line) or ("ip pim rp-address" in line) or ("match access-group name" in line) or ("match ip address" in line) or ("match ip address prefix-list" in line) or ("distance" in line):
                        words = line.split()
                        if words[-1] not in used_acls:
                                used_acls.append(words[-1])
#print(acls)
#print(used_acls)
unused = list(set(acls) - set(used_acls))
undefined = list(set(used_acls) - set(acls))

if (type == "undefined") and (len(sys.argv) == 3):
  if len(undefined):
    print("No")
  else:
    print("Yes")
elif (type == "unused") and (len(sys.argv) == 3):
  if len(unused):
    print("No")
  else:
    print("Yes")
#else:
#  print("Undefined acls : ",undefined)
#  print("Unused acls : ",unused)


x=""
if (type == "undefined") and (len(sys.argv) == 4):
  for i in undefined:
    x= x+i+" , "
  print(x.rstrip(" , "))

x=""
if (type == "unused") and (len(sys.argv) == 4):
  for i in unused:
    x=x+i+" , "
  print(x.rstrip(" , "))
