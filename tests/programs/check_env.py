import os
import sys

var_name = sys.argv[1]
print(os.getenv(var_name))
