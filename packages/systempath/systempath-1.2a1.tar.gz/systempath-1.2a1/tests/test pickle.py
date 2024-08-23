import pickle
from systempath import *

x = pickle.dumps(Path("x"))
print(repr(pickle.loads(x)))

x = pickle.dumps(File("x"))
print(repr(pickle.loads(x)))

x = pickle.dumps(Directory("x"))
print(repr(pickle.loads(x)))

x = pickle.dumps(SystemPath("x"))
print(repr(pickle.loads(x)))

x = pickle.dumps(Open("x"))
print(repr(pickle.loads(x)))

x = pickle.dumps(Content("x"))
print(repr(pickle.loads(x)))

x = pickle.dumps(File("x").ini())
print(repr(pickle.loads(x)))
