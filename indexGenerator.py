import os

ignore_dirs = ['.git', '.idea']
index = 'README.MD'

if os.path.exists(index):
    os.remove(index)

dirs = []
for d in os.listdir('.'):
    if d in ignore_dirs:
        continue
    if os.path.isfile(d):
        continue
    dirs.append(d)

with open(index, 'w+', encoding='utf-8') as f:
    for d in dirs:
        f.write(f'# {d}\r\n')
        for item in os.listdir(d):
            f.write(f'- [{item}]({d}/{item})\r\n')
