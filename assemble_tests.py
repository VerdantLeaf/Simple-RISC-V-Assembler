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
        source_dir (str): The name of hte source directory to search from
        
    Returns:
        list: Str list of all of the assembly programs in the dir
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
    print(f"Enter [1-{len(programs)}] to assemble a specific program")
    print("q - quit")
    print("="*50)

def assemble_program(assembler, source_dir, dest_dir, program_name, warning_flags=None):
    """Assembles a single program into binary form

    Args:
        assembler (RV32IAssembler): Assembler object to use
        source_dir (str): Source directory to search for the program
        dest_dir (str): Destination directory to place the binary file
        program_name (str): Name of the program to assemble

    Returns:
        dict: Dictionary describing the results of the assembly
    """


    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    # Ensure that destination actually exusts
    dest_path.mkdir(parents=True, exist_ok=True)
    
    source_file = None
    extensions = ['.s', '.asm', '.rv32i']
    # Check for all extensions and name combinations
    for ext in extensions:
        potential_file = source_path / f"{program_name}{ext}"
        if potential_file.exists():
            source_file = potential_file
            break
        
    if not source_file:
        return {
            'program': program_name,
            'success': False,
            'error': f"Source file not found for '{program_name}'"
        }

    # Assembles to .mem files
    output_file = dest_path / f"{program_name}.mem"
    
    try:
        
        # Set warning flags, if assembler supports it
        if warning_flags and hasattr(assembler, 'set_warning_flags'):
            assembler.set_warning_flags(warning_flags)
        elif warning_flags and hasattr(assembler, 'warning_flags'):
            assembler.warning_flags = warning_flags
        
        result = assembler.assemble(str(source_file), str(output_file))
        
        return {
            'program': program_name,
            'success': True,
            'source': str(source_file),
            'output': str(output_file),
            'warnings': False, # Add warning messages to the assembler
            'result': result
        }
    except Exception as e:
        return {
            'program': program_name,
            'success': False,
            'warnings': False, # See above for add to assembler
            'error': str(e),
            'source;': str(source_file)
        }

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
    
    # Add GCC style warnings
    parser.add_argument(
        '-Wall',
        action='store_true',
        help='Enable all warnings (like gcc -Wall)'
    )
    
    parser.add_argument(
        '-Werror',
        action='store_true',
        help='Treat all warnign as errors (like gcc -Werror)'
    )
    
    parser.add_argument(
        '-Wextra',
        action='store_true',
        help='Enable extra warnings (like gcc -Wextra)'
    )
    
    parser.add_argument(
        '-w',
        action='store_true',
        help='Suppress all warnings (like gcc -w)'
    )
    
    parser.add_argument(
        '-Wpedantic',
        action='store_true',
        help='Enable pedantic warnings for strict RISC-V compliance'
    )
    
    parser.add_argument(
        '-Wno-unused-label',
        action='store_true',
        help='Suppress warnings about unused labels'
    )
    
    parser.add_argument(
        '-Wno-immediate-range',
        action='store_true',
        help='Suppress warnings about immediate value ranges'
    )
    
    args = parser.parse_args()
    
    # Warning flag dictionary
    warning_flags = {
        'error_on_warning': args.Werror,
        'all_warnings': args.Wall,
        'extra_warnings': args.Wextra,
        'suppress_all': args.w,
        'pedantic': args.Wpedantic,
        'no_unused_label': args.Wno_unused_label,
        'no_immediate_range': args.Wno_immediate_range
    }
    
    # Check for conflicting flags
    if args.w and (args.Wall or args.Wextra or args.Wpedantic):
        print("Warning: -w flag suppresses all warnings, other warning flags will be ignored")
    
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