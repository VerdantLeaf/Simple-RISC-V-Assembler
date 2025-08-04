# Simple RISC-V Assembler
Assembles simple RISC-V programs to .mem files for use by my CPU; because every good CPU needs its own assembler....

The assembler uses a two-pass style of compilation and manages a symbol table for use by the assembler. Using regular expressions, the assembler implements an instruction parsing engine to decode the different instruction formats and convert the mnemonics to hexadecimal. Additionally, the assembler handles errors within the assembly code like range checking of immediates, register/label validation, and constructing the machine code file instructions. The current version is implemented for the RV32i instruction set, except for instructions like `ecall` as this program is not intended, at least currently, for use on a system with an OS.

However, allowing the assembler to create the different text and data sections of the output file. Additionally, doing other things to make it a "real" assembler would increase the utility. For now though, I need it for my purposes and I'll expand it if I need to/should.

## Error and warning system:
The `rv32i_assembler.py` file has become a standalone object that files like `assemble_tests.py` can instantiate and use to assemble their own programs. Results are returned from the `assemble()` method and describes what the results of the assembly was - were there errors/warnings, or was there an internal error to the program itself, as well as the messages for each error. The line number of the warning/error from the original sourcce file should be included in all messages (haven't fully tested that yet)

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

### 
