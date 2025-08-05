# Simple RISC-V Assembler
Assembles simple RISC-V programs to .mem files for use by my CPU; because every good CPU needs its own assembler....

The assembler uses a two-pass style of compilation and manages a symbol table for use by the assembler. Using regular expressions, the assembler implements an instruction parsing engine to decode the different instruction formats and convert the mnemonics to hexadecimal. Additionally, the assembler handles errors within the assembly code like range checking of immediates, register/label validation, and constructing the machine code file instructions. The current version is implemented for the RV32i instruction set, except for instructions like `ecall` as this program is not intended, at least currently, for use on a system with an OS. I am considering adding this feature, as it would not require much work, due to the modular nature of the assembler.

The assembler itself is implemented in `rv32i_assembler.py` and provides the `assemble()` method to take the input file pointer and assemble the instructions found in the file, outputting to the output file pointer. This is the back end of the assembler, as the `assemble_test.py` file handles the front end responsibilities, like file validation, argument handling, etc.... `assemble()` returns an `AssemblerResults` object that can be used to understand the results of the assembly. The assembler uses [GCC style warnings](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html) to allow the user to tweak different settings within the compiler. These settings can be modified when instantiating the assembler object, by passing a string, bool dictionary of warning flags.

## Some Notes:
As the project title may suggest, this assembler is "simple". It takes takes assembly code with labels, instructions, and comments, and then converts the instructions to a binary file. This is because my primary reasons for developing this were to create .mem files for my RISC-V CPU project and getting better at Python. Hence why I picked Python, as much as I love the C programming language, I wanted to worry about creating the assembler, not hunting down a memory leak or something. Additionally, I wanted to be able to develop and run the program on Windows/any platform/not Linux, since I didn't have Linux machine access at the start. I have no plans to assemble large programs with this code, so speed/performance came second to ease of development and usability.

## Things I wish it could do
Here are some things I wish the assembler could do, that I may add in the future:
- Greater instruction support, whether that's RV32M or adding `ecall` or other instructions, it would expand the versatility
- String constant support (goes with the one below) - Would allow for string constants to be stored in the output memory file (although with current CPU design would need to be loaded into a data.mem file)
- More complex assembly files - adding support for detecting and parsing things like `.text`, `__global`, etc...

# Operation/Completed work:
## Preprocessor:
The preprocessor cleans out any comments and unecessary whitespace, as well as building a dictionary of labels and their respective program counters. Once the line is clean of comments, unnecessary whitespace, and labels (and does not contain just whitespace) then the instruction is clean and is appended to a list of the cleaned lines.

## Assembly:
### Instruction Parsing
For each of the cleaned lines, the instruction is then assembled with `assemble_instruction()`. Here, the instruction is parsed with `parse_instruction()`, where the assembler uses a regular expression to match the format of the instruction, where it returns the first matching group (the operation, or `opcode`) and a list of all of the remaining matching groups found, or `operands`. At this point, `parse_instruction()` does a manual string match of the operation to the six different types of RISC-V instructions, calling the respective `encode_X_type()` funciton where X is the letter of the instruction type.

### Different Encodings
These encoding functions are somewhat straightforward for some, and deceptively complex for others. Instructions that are R-type or U-type are fairly simple, as they only have one format or have a limited number of instructions. However, I-type instructions, for example, can take multiple different forms, such as `addi x12, x17, 3` or `lw x23, 24(x14)`, and the assembler must be able to handler the different formats. Additionally, because of how the `parse_instruction()` function operates, the `immd(rs1)` form of I-type instructions are caught as one operand. Due to this, the `decode_offset()` function must be used as it contains a regular expression that will separate these two operands. 

### Error Checking
Throughout this process, and the functions for all of the other instruction types, error checking of values, names (`validate_registers()`), and other errors is being flagged (In the future, checking for such errors may occur before the assembly of the instructions, during the first pass, to improve assembly performance). Immediate values are both range checked, and are converted from hexadecimal/binary in `deocde_immediate()` if written as such in the source code. From this point, the instruction is then built in a bitwise manner, where it is then appended to the memory list of assembled instructions.

### Memory padding
In my research, I found that Vivado will not accept .mem files that contain less memory than the memory that you've declared. Due to this, the rest of the memory is filled with zeros. The output file, as passed in the command line, is then written to, where each instruction is written as eight hexadecimal characters to represent the 32 bit instruction. This is done for all of the instructions in memory, and then the assembly is completed.
