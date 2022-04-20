from src.dtaf_core.lib.artifactory_lib import download
import sys
import os
import json

commit_id = sys.argv[1]

username = 'sys_cluster'
password = '0okm9ijn*UHB&YGV'

url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/logs/ST COV %s/" % (commit_id)
dest = 'stcovdir'
download(url=url, username=username, password=password, dest=dest)

file_list = os.listdir('./stcovdir')
cov_dict = {}

for i in file_list:
    with open('./stcovdir/' + i, 'rt') as file:
        content = json.loads(file.read())
        if not cov_dict:
            cov_dict = content
        else:
            for k, v in content.items():
                try:
                    lis1 = content[k]
                    lis2 = cov_dict[k]
                    for i in range(len(lis1)):
                        if lis1[i] is True and lis2[i] is False:
                            lis2[i] = True
                    cov_dict[k] = lis2
                except KeyError:
                    continue

lines = 0
true_lines = 0
print('Filename\tLines\tCovered\tRatio')
for k, v in cov_dict.items():
    all_line = 0
    cover_line = 0
    while None in v:
        v.remove(None)
    for i in v:
        all_line += 1
        lines += 1
        if i == True:
            cover_line += 1
            true_lines += 1
    try:
        print("%s\t%s\t%s\t%s" % (
            k, all_line, cover_line, int(round(cover_line / all_line, 2) * 100)) + "%")
    except ZeroDivisionError:
        print("%s\t%s\t%s\t%s" % (k, all_line, cover_line, 100) + "%")

with open('st_result.txt', 'wt') as file:
    file.write(str(int(round(true_lines / lines, 2) * 100)))
