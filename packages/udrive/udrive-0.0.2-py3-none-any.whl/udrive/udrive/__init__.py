import os
import sys

# Insertar la ruta de "ufibre" en sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ufibre"))

try:
    import ufibre
    print("udrive: ufibre imported")
except ImportError:
    print("udrive: ufibre not imported")
    pass

# Opcional: si quieres exponer funcionalidades de ufibre en udrive
try:
    find_any = ufibre.find_any
    find_all = ufibre.find_all
except AttributeError:
    print("udrive: Error accessing ufibre functions")


from .version import get_version_str
__version__ = get_version_str()
del get_version_str
