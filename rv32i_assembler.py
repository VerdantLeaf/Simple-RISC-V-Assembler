"""Assembler for simple RISC-V code for use by my RISC-V CPU"""

import re
import sys
import os


# Strategy: Two pass assembly - First pass collects labels and addresses while second pass does 
# the actual assembly into binary


class RV32IAssembler:
    """Contains all vars and methods for preprocess, assembly, and file writing"""
    def __init__(self):
        # opcodes - Add all RV32I, no support for fence, ecall, etc...
        self.opcodes = {
            # U-type
            "lui":      0b0110111,
            "auipc":    0b0010111,
            # J-type + JALR (call and rtn)
            "jal":      0b1101111,
            "jalr":     0b1100111,
            # B-type
            "beq":      0b1100011,
            "bne":      0b1100011,
            "blt":      0b1100011,
            "bge":      0b1100011,
            "bltu":     0b1100011,
            "bgeu":     0b1100011,
            # S-type
            "lb":       0b0000011,
            "lh":       0b0000011,
            "lw":       0b0000011,
            "lbu":      0b0000011,
            "lhu":      0b0000011,
            "sb":       0b0100011,
            "sh":       0b0100011,
            "sw":       0b0100011,
            # I-type
            "addi":     0b0010011,
            "slti":     0b0010011,
            "sltiu":    0b0010011,
            "xori":     0b0010011,
            "ori":      0b0010011,
            "andi":     0b0010011,
            "slli":     0b0010011,
            "srli":     0b0010011,
            "srai":     0b0010011,
            # R-type
            "add":      0b0110011,
            "sub":      0b0110011,
            "sll":      0b0110011,
            "slt":      0b0110011,
            "sltu":     0b0110011,
            "xor":      0b0110011,
            "srl":      0b0110011,
            "sra":      0b0110011,
            "or":       0b0110011,
            "and":      0b0110011,
        }
        # Define func3 values for each instruction 
        self.func3 = {
            # B-type
            "beq":      0b000,
            "bne":      0b001,
            "blt":      0b100,
            "bge":      0b101,
            "bltu":     0b110,
            "bgeu":     0b111,
            # S-type
            "lb":       0b000,
            "lh":       0b001,
            "lw":       0b010,
            "lbu":      0b100,
            "lhu":      0b101,
            "sb":       0b000,
            "sh":       0b001,
            "sw":       0b010,
            # I-type
            "jalr":     0b000,
            "addi":     0b000,
            "slti":     0b010,
            "sltiu":    0b011,
            "xori":     0b100,
            "ori":      0b110,
            "andi":     0b111,
            "slli":     0b001,
            "srli":     0b101,
            "srai":     0b101,
            # R-type
            "add":      0b000,
            "sub":      0b000,
            "sll":      0b001,
            "slt":      0b010,
            "sltu":     0b011,
            "xor":      0b100,
            "srl":      0b101,
            "sra":      0b101,
            "or":       0b110,
            "and":      0b111,
        }
        # Define func7 values for each instruction
        self.func7 = {
            # I-type
            "slli":     0b0000000,
            "srli":     0b0000000,
            "srai":     0b0100000,
            # R-type
            "add":      0b0000000,
            "sub":      0b0100000,
            "sll":      0b0000000,
            "slt":      0b0000000,
            "sltu":     0b0000000,
            "xor":      0b0000000,
            "srl":      0b0000000,
            "sra":      0b0100000,
            "or":       0b0000000,
            "and":      0b0000000,
        }
        # Define register names with all values
        self.registers = {
            # Names
            "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4, "t0": 5, "t1": 6, "t2": 7, 
            "s0": 8, "s1": 9, "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a5": 15,
            "a6": 16, "a7": 17, "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23, 
            "s8": 24, "s9": 25, "s10": 26, "s11": 27, "t3": 28, "t4": 29, "t5": 30, "t6": 31,
            # Reg numbers
            "x0": 0, "x1": 1, "x2": 2, "x3": 3, "x4": 4, "x5": 5, "x6": 6, "x7": 7, 
            "x8": 8, "x9": 9, "x10": 10, "x11": 11, "x12": 12, "x13": 13, "x14": 14, "x15": 15,
            "x16": 16, "x17": 17, "x18": 18, "x19": 19, "x20": 20, "x21": 21, "x22": 22, "x23": 23, 
            "x24": 24, "x25": 25, "x26": 26, "x27": 27, "x28": 28, "x29": 29, "x30": 30, "x31": 31, 
        }

        # Init mem, labels, PC [bytes], & NOP command
        self.labels = {}
        self.memory = []
        self.pc = 0
        self.nop = 0x00000013
        self.zero = 0x00000000
        self.max_instructions = 1024

    def preprocessor(self, lines):
        """First pass: Collect labels + addresses. Remove comments"""

        clean_lines = []
        self.pc = 0

        for line in lines:
            # Replaces everything after a # in a line with nothing
            line = re.sub(r'#.*$', '', line)
            line = line.strip()

            # Skip lines with no text on them
            if not line:
                continue

            # See if there is a label on this line to record the address
            label_match = re.match(r'^\s*([a-zA-Z0-9_\.]+)\s*:(.*)$', line)

            # use regex to see if label on line

            # If label, process label

            # Handle edge cases

            # If no comments and no label, instruction is now clean. Append
            clean_lines.append(line)

            # Each instruction is 4B
            self.pc += 4

        return clean_lines

    def parse_instruction(self, line):
        """Parses single instruction and returns opcode + operands"""
        # Split line into opcode and operands with regex.
        # Would not let me put this on one line...?
        opcode, operands = re.match(r'\s*([a-z]+)(?:\s+(.*))?$', line)
        return opcode, operands

    def encode_r_type(self, opcode, operands):
        """Encodes R-type instructions to binary"""

        rd = operands[0]
        r1 = operands[1]
        r2 = operands[2]

        if rd not in self.registers:
            raise ValueError(f"Invalid register name: {rd}")
        if r1 not in self.registers:
            raise ValueError(f"Invalid register name: {r1}")
        if r2 not in self.registers:
            raise ValueError(f"Invalid register name: {r2}")

        f7 = self.func7[opcode]
        f3 = self.func3[opcode]
        op = self.opcodes[opcode]
        # Assemble instruction
        instruction = (f7 << 25) | (r2 << 20) | (r1 << 15) | (f3 << 12) | (rd << 7) | op

        return instruction

    def encode_i_type(self, opcode, operands):
        """Encodes I-type instructions to binary"""
        
        # TODO: This doesn't handle JALR or save/loads with the offset formats.
        if opcode == "jalr":
            if len(operands) == 3:
                rd = operands[0]
            elif len(operands) == 2:
                rd = "ra"
            else:
                raise ValueError(f"Invalid operand count for JALR: {len(operands)}")
        # Handle load instructions with formats
        elif opcode in ["lb", "lh", "lw", "lbu", "lhu"]:
            if len(operands) != 2: # invalid form
                raise ValueError(f"Load instruction requires 2 operands") # todo: Complete
            rd = operands[0]

            # Parse
        else:
            rd = self.registers[operands[0]]
            r1 = self.registers[operands[1]]
            immd = operands[2]

            if rd not in self.registers:
                raise ValueError(f"Invalid register name: {rd}")
            if r1 not in self.registers:
                raise ValueError(f"Invalid register name: {r1}")
            if immd > 2048 or immd < -2048:
                raise ValueError(f"Immediate value is out of range: {immd}")

            f3 = self.func3[opcode]
            op = self.opcodes[opcode]

            instruction = (immd << 20) | (r1 << 15) | (f3 << 12) | (rd << 7) | op
            return instruction

    def encode_s_type(self, opcode, operands):
        """Encodes S-type instructions to binary"""

    def encode_b_type(self, opcode, operands, current_pc):
        """Encodes B-type instructions to binary"""

    def encode_j_type(self, opcode, operands, current_pc):
        """Encodes J-type instructions to binary"""

    def encode_u_type(self, opcode, operands):
        """Encodes U-type instructions to binary"""

    def assemble_instruction(self, line, current_pc):
        """Assembles one instruction to machine code"""

        opcode, operands = self.parse_instruction(line)

        if opcode in ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and"]:
            return self.encode_r_type(opcode, operands)   
        elif opcode in ["addi", "slti", "sltiu", "xori", "ori", "andi", "slli", "srli", "srai", "jalr", # JALR
                        "lb", "lh", "lw", "lbu", "lhu"]: # These take the i type form as well, need to encode as such
            return self.encode_i_type(opcode, operands)
        elif opcode in ["sb", "sh", "sw"]:
            return self.encode_s_type(opcode, operands)
        elif opcode in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
            return self.encode_b_type(opcode, operands, current_pc)
        elif opcode in ["jal"]:
            return self.encode_j_type(opcode, operands, current_pc)
        elif opcode in ["lui", "auipc"]:
            return self.encode_u_type(opcode, operands)
        else:
            raise ValueError(f"Unsupported instruction: {opcode}")
        
    def assemble(self, input_file, output_file):
        """Runs the entire assembly procedure"""

        with open(input_file, 'r', encoding=ascii) as file:
            lines = file.readlines()

        # Run preprocessor and clean
        cleaned_lines = self.preprocessor(lines)

        # If program is too large, throw error
        if len(cleaned_lines) > self.max_instructions:
            print(f"Number of instructions in file at {input_file} larger than memory size!")
            print(f"Cannot assemble! Max number of instructions is {self.max_instructions}")
            return False

        # Second pass is actually assembling the instructions
        self.pc = 0
        for line in cleaned_lines:
            try:
                instruction = self.assemble_instruction(line, self.pc)
                self.memory.append(instruction)
                self.pc +=4
            except Exception as e:
                print(f"Error assembling instruction '{line}': {e}")
                return False

        # .mem file needs to fill the entire memory
        while len(self.memory) < self.max_instructions: # Fill remaining memory with zeros 
            self.memory.append(self.zero)

        # Write each assembled instruction in to the output .mem file as an 8 character hex sequence
        with open(output_file, 'w', encoding=ascii) as file:
            for instr in self.memory:
                file.write(f"{instr:08x}\n")

        print(f"Successfully assembled {len(cleaned_lines)} instructions to {output_file}")
        return True

def main():
    """Assembles simple RISC-V assembly instructions into machine code stored in .mem files"""
    if len(sys.argv) != 3:
        print("Improper usage.\nUsage is: python assembler.py input.s output.mem")
        return

    input_file = sys.argv[1] # Python isn't a cmd line arg (My C brain is losing it)
    output_file = sys.argv[2] # Also prints don't need a new line, this language is cheating
    assembler = RV32IAssembler()

    if not os.path.exists(input_file): # Check if input exists
        print("Input file at path '{input_file}' not found")
        return

    assembler.assemble(input_file, output_file) # Call assembler

if __name__ == "__main__":
    main()
