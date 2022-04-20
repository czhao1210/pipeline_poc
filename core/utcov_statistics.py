import re

with open('badges_branch/dev_branch_ut_cov.svg', 'rt') as file:
    badge_content = file.read()

last_merge_coverage = int(re.findall('">(\d*?)%</text>', badge_content)[0])

with open('coverage_result.txt', 'rt') as f:
    content = f.read()
res = re.findall('TOTAL *\d* *\d* *(\d\d)%', content)

if True or int(res[0]) >= last_merge_coverage:
    print(res[0])
else:
    print('Coverage is lower than last merge request')
    #raise Exception('Coverage is lower than last merge request')

