import sys
# syslog file
file1 = sys.argv[1]

# yce_events file
file2 = sys.argv[2]

with open(file1,'r') as f:
    text1 = f.readlines()


with open(file2,'r') as f:
    text2 = f.readlines()

new_list = [] # list to capture the yce_events that match with the syslog
new_list1=[] # list to capture all the yce_events
for l1 in text1:
    if 'Track' in l1:
        t1 = l1.split()[2]
        new_list1.append(l1)
        for l2 in text2:
            if '/ipsla_' in l2:
                if t1 == l2.split()[3]:
                    #print(t1,l1.split()[3],l1,l2)
                    new_list.append(l1)

new_list1 = set(new_list1)
new_list = set(new_list)
d = new_list1.difference(new_list)
d = list(d)
d.sort()
for l in d:
  print(l.strip('\n'))
