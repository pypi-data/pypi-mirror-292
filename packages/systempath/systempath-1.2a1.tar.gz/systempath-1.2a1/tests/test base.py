from systempath import tree

from typing import Generator, Iterator

x = tree('../')
print(x)

print(next(x))
print(next(x))
print('--')


for i in x:
    print(i)
