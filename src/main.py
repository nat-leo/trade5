from src.datahandler import data_handler
from src.subpackage2 import submodule2

def printf(phrase):
    return data_handler.addOne(phrase)

print(printf(5))