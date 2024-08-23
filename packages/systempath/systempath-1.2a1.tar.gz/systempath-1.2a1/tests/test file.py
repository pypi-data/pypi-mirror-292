# import gqylpy
from systempath import *

file = File('tree/4.txt')

data = [
    ['Name', 'Age', 'City'],
    ['Alice', '30', 'New York'],
    ['Bob', '25', 'Los Angeles'],
    ['Name', 'Age', 'City'],
    ['Alice', '30', 'New York'],
    ['Bob', '25', 'Los Angeles']
]

file.yaml.dump(data)
print(file.yaml.load())
