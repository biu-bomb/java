import os

ignore_dirs = ['.git', '.idea', '.imgs']
allow_suffix = ['md', 'MD', 'png', 'gif']
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
dirs.sort(reverse = True)
with open(index, 'w+', encoding='utf-8') as f:
    for d in dirs:
        f.write(f'# {d}\r\n')
        for item in os.listdir(d):
            if item.split(".")[-1] in allow_suffix:
                f.write(f'- [{item}]({d}/{item})\r\n')
