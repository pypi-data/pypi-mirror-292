from systempath import *

# # Path
# print(Path)
# print(Path.__module__)
# print(Path.__name__)
# print(Path.__qualname__)
# print('-----------------')
#
# # ReadOnly
# print(Path.__base__)
# print(Path.__base__.__module__)
# print(Path.__base__.__name__)
# print(Path.__base__.__qualname__)
# print('-----------------')
#
# # ReadOnlyMode
# print(Path.__class__)
# print(Path.__class__.__module__)
# print(Path.__class__.__name__)
# print(Path.__class__.__qualname__)
# print('-----------------')
#
# # MasqueradeClass
# print(Path.__class__.__class__)
# print(Path.__class__.__class__.__module__)
# print(Path.__class__.__class__.__name__)
# print(Path.__class__.__class__.__qualname__)
# print('-----------------')


# import copy
#
# x = copy.deepcopy(Path)
# print(x)
#
# path = Path('.')
# x = copy.deepcopy(path)
# print(repr(x))
#
# print('ReadOnly:')
# x = copy.deepcopy(Path.__base__)
# print(x)
# print(x.__module__)
# print(x.__name__)
# print(x.__qualname__)
#
# print('ReadOnlyMode:')
# x = copy.deepcopy(Path.__class__)
# print(x)
# print(x.__module__)
# print(x.__name__)
# print(x.__qualname__)
#
# print('MasqueradeClass:')
# x = copy.deepcopy(Path.__class__.__class__)
# print(x)
# print(x.__module__)
# print(x.__name__)
# print(x.__qualname__)


import pickle

print('Path:')
x = pickle.dumps(Path)
x = pickle.loads(x)
print(x)
print(x.__module__)
print(x.__name__)
print(x.__qualname__)

print('Path instance:')
path = Path('.')
x = pickle.dumps(path)
x = pickle.loads(x)
print(repr(x))
print(x.__module__)
print(x.__dict__)

# print('ReadOnly:')
# x = pickle.dumps(Path.__base__)
# x = pickle.loads(x)
# print(x)
# print(x.__module__)
# print(x.__name__)
# print(x.__qualname__)
#
# print('ReadOnlyMode:')
# x = pickle.dumps(Path.__class__)
# x = pickle.loads(x)
# print(x)
# print(x.__module__)
# print(x.__name__)
# print(x.__qualname__)
#
# print('MasqueradeClass:')
# x = pickle.dumps(Path.__class__.__class__)
# x = pickle.loads(x)
# print(x)
# print(x.__module__)
# print(x.__name__)
# print(x.__qualname__)
