from src.dtaf_core.lib.artifactory_lib import upload
import time
import sys
import os
import re
import json

commit_id = sys.argv[1]

if os.path.exists('./st_coverage_dict'):
    with open('./st_coverage_dict') as file:
        cov_dict = json.loads(file.read())
else:
    cov_dict = {}

file_list = os.listdir('./htmlcov')
cov_html_list = []
for i in file_list:
    if not i == 'index.html' and i.endswith('html'):
        cov_html_list.append(i)

for i in cov_html_list:
    with open('./htmlcov/' + i, 'rt') as obj:
        content = obj.read()
    res = re.findall('<p id="t(\d*)"([\s\S]*?)>', content)
    file_path_res = re.findall('<h1>Coverage for <b>([\s\S]*)</b>', content)
    if file_path_res:
        file_path = file_path_res[0]
        if cov_dict.get(file_path) is None:
            cov_dict[file_path] = [False] * len(res)
        if cov_dict[file_path]:
            for i2 in res:
                if 'pln' in i2[1]:
                    cov_dict[file_path][int(i2[0]) - 1] = None
                elif not 'mis' in i2[1]:
                    cov_dict[file_path][int(i2[0]) - 1] = True

with open('./st_coverage_dict', 'wt') as file:
    file.write(json.dumps(cov_dict))

with open('./st_coverage_dict', 'rt') as file:
    content = json.loads(file.read())  # type:dict

lines = 0
true_lines = 0
for k, v in content.items():
    while None in v:
        v.remove(None)
    for i in content[k]:
        lines += 1
        if i == True:
            true_lines += 1

print(int(round(true_lines / lines, 2) * 100))

username = 'sys_cluster'
password = '0okm9ijn*UHB&YGV'

url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/logs/ST COV %s/" % (commit_id)
source = './st_coverage_dict'
filename = './%s' % (time.time())

with open('./st_coverage_dict', 'rt') as file1:
    with open(filename, 'wt') as file2:
        file2.write(file1.read())

upload(source=filename, url=url, username=username, password=password)
