import os
import time

from systempath import tree, Directory


# x = tree('tree')
x = Directory(b'tree').tree(omit_dir=True)

for i in x:
    if b'7777' in i.contents:
        print(i)
