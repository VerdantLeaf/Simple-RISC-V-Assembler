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

def display_menu(programs):
    """Displays menu to terminal showing different programs available for assembly

    Args:
        programs (string list): List of valid program names
    """
    # ok, this repeating syntax might be my new favorite thing
    print("\n" + "="*50)
    print("RV32I Assembly Program Menu")
    print("="*50)
    
    if not programs:
        print('No assembly programs found in the source directory.')
        return
    
    for i, program in enumerate(programs, 1):
        print(f"{i:2d}. {program}")
        
    print("\nOptions:")
    print("Enter number to assemble a specific program")
    print("q - quit")
    print("="*50)

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
        
    programs = get_program_files(args.source_dir)
    
    if not programs:
        print(f"No assembly programs found in '{args.source_dir}' directory")
        sys.exit(1)
        
    if args.assemble_all:
        print(f"Assembling all {len(programs)} programs...")
        results = []
        
        
        sys.exit(0)
        
    if args.assemble_simple:
        simple_programs = [p for p in programs if p.startswith('simple_')]
        if not simple_programs:
            print("No programs with 'simple_' prefix found.")
            sys.exit(1)
            
            
            
        sys.exit(0)

    print(f"Found {len(programs)} assembly programs in '{args.source_dir}'")
    
    while True:
        
        display_menu(programs)
        
        try:
            choice = input("\nEnter your choice: ").strip()

            if choice.lower() == 'q':
                print('\n\nGoodbye!')
                break
            
            try:
                choice_num = int(choice)            
                if 1 <= choice_num < len(programs):
                    program_name = programs[choice_num - 1]
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(programs)}, or 'q' to quit.")
                
            except ValueError:
                print(f"Invalid choice. Please enter a number between or 'q' to quit.")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()