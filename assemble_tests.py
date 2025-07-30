"""Script for assembling all of the test programs in /prog and placing them in /bin"""

from pathlib import Path
import os
import shutil


# Collect the program names in the /prog directory

# Use shutil to run the python assembler, setting outputs to 