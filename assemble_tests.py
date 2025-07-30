"""Script for assembling all of the test programs in /prog and placing them in /bin"""

from pathlib import Path
import os
import shutil

# Want to keep this pretty lightweight and simple

# Collect the program names in the /prog directory

# Create nice menu to ask user which of the programs they would like to assemble 
# The user can include the -A flag in the cmd line args to instead automatically assemble all the tests
# The user can include the -S flag in the cmd line args to instead automatically assemble all the tests with the "simple_" prefix

# Use shutil to run the python assembler, setting output files to the bin directory

# Collect any warnings/errors on assembler execution
# Print something nice to the terminal/user with the results of assembly

# Return to the menu to ask the user which program they would like to assemble