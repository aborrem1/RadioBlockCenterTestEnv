import subprocess
import re

VBoxPath = 'C:\\Program Files\\Oracle\\VirtualBox\\'

result = subprocess.run(['VBoxManage', 'list', 'runningvms'], shell=True, cwd=VBoxPath, capture_output=True, text=True)
print("stdout:" + result.stdout)

#regex = '"........"'

#list = re.findall(regex, result.stdout)
#'(?<=\").*?\"'
p = re.compile(r'"(.*?)"')
list = p.findall(result.stdout)
print(list)
exit()



list = result.stdout.split('\n')
print(list)
print(len(list))
for astr in list:
    newstr = astr.split('"')
    print(newstr)

#result.stdout.rfind('"',)

#list = result.stdout.split(' ')
#print(list)