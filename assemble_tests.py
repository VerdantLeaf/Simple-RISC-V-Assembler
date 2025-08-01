"""Script for assembling all of the test programs in /prog and placing them in /bin"""

from pathlib import Path
import os
import sys
import argparse
import rv32i_assembler
from rv32i_assembler import RV32IAssembler

# Want to keep this pretty lightweight and simple

# Collect the program names in the /prog directory. Include optional argument to set custom source dir

# Create nice menu to ask user which of the programs they would like to assemble 
# Include optional -A flag to automatically assemble all the tests
# Inlcude optional -S flag to automatically assemble all the tests with the "simple_" prefix

# Use the assembler object to assemble each test and place into the bin dir. Include optional argument to set custom destination directory

# Collect any warnings/errors on assembler execution
# Print something nice to the terminal/user with the results of assembly

# Return to the menu to ask the user which program they would like to assemble. If the A or S flag was passed, exit immediately. Allow Q (case insensitive) to be a quit command as well

def get_program_files(source_dir):
    """Collects all the assembly program files from the source directory

    Args:
        source_dir (string): The name of hte source directory to search from
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return []
    
    # Look for assembly files
    extensions = ['.s', '.asm', '.rv32i']
    programs = []
    
    for ext in extensions:
        programs.extend(source_path.glob(f"*{ext}"))

    return sorted([p.stem for p in programs])

def main():
    parser = argparse.ArgumentParser(
        description="Semi-automation of RV32I program assembler",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--source_dir', '-s',
        default='prog',
        help='Source directory containing assembly programs (default: prog)'
    )
    
    parser.add_argument(
        '--dest_dir', '-d',
        default='bin',
        help='Destination directory for assembled binaries (default: bin)'
    )
    
    parser.add_argument(
        '-A', '--assemble-all',
        action='store_true',
        help='Autoamtically assemble all programs and exit'
    )
    
    parser.add_argument(
        '-S', '--assemble-simple',
        action='store_true',
        help='Automatically assemble all programs with "simple_" prefix and exit'
    )
    
    args = parser.parse_args()
    
    try:
        assembler = RV32IAssembler()
    except Exception as e:
        print(f"Error initializing assembler: {e}")
        sys.exit(1)




if __name__ == "__main__":
    main()