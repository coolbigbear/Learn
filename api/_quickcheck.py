import sys
print(f"Python {sys.version}")
# Just check if modules can be imported (not connecting to Docker)
import pytest
print(f"pytest: {pytest.__version__}")
