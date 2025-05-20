import re
import sys
import os


# Strategy: Two pass assembly - First pass collects labels and addresses while second pass does 
# the actual assembly into binary

class RV32IAssembler:

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

            # use regex to see if label on line

            # If label, process label

            # Handle edge cases

            # If no comments and no label, instruction is now clean. Append
            clean_lines.append(line)

            # Each instruction is 4B
            self.pc += 4

        return clean_lines

    def parseInstruction(self, line):
        """Parses single instruction and returns opcode + operands"""


    def encodeRType(self, opcode, operands):
        """Encodes R-type instructions to binary"""

    def encodeIType(self, opcode, operands):
        """Encodes I-type instructions to binary"""

    def encodeSType(self, opcode, operands):
        """Encodes S-type instructions to binary"""

    def encodeBType(self, opcode, operands):
        """Encodes B-type instructions to binary"""

    def encodeJType(self, opcode, operands):
        """Encodes J-type instructions to binary"""

    def encodeUType(self, opcode, operands):
        """Encodes U-type instructions to binary"""