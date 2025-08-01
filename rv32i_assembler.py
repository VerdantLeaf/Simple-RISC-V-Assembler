"""Assembler for simple RISC-V code for use by my RISC-V CPU"""

import re
import sys
import os


# Strategy: Two pass assembly - First pass collects labels and addresses while second pass does 
# the actual assembly into binary


class RV32IAssembler:
    """Contains all vars and methods for preprocess, assembly, and file writing"""
    def __init__(self, warning_Flags=None):
        # Warning system
        self.warning_flags = warning_Flags or {}
        self.warnings = []
        self.unused_labels = set()
        # Init mem, labels, PC [bytes], & NOP command
        self.labels = {}
        self.used_labels = set()
        self.memory = []
        self.pc = 0
        self.nop = 0x00000013
        self.max_instructions = 1024

        # Reverse mapping of isntr type to check membership easier
        self.type_to_mnemonics = {
            "U": {"lui", "auipc"},
            "J": {"jal", "jalr"},
            "B": {"beq", "bne", "blt", "bge", "bltu", "bgeu"},

            "S": {"sb", "sh", "sw"},
            "I": {"addi", "slti", "sltiu", "xori", "ori", "andi", "slli", "srli", "srai", "lb", "lh", "lw", "lbu", "lhu"},
            "R": {"add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and",}
        }
        
        # opcodes - Use structured dictionary
        self.opcodes = {
            # U-type
            "lui":      {"opcode": 0b0110111, "type" : "U"},
            "auipc":    {"opcode": 0b0010111, "type" : "U"},
            # J-type + JALR (call and rtn)
            "jal":      {"opcode": 0b1101111, "type" : "J"}, 
            "jalr":     {"opcode": 0b1100111, "type" : "J"}, 
            # B-type
            "beq":      {"opcode": 0b1100011, "type" : "B"}, 
            "bne":      {"opcode": 0b1100011, "type" : "B"}, 
            "blt":      {"opcode": 0b1100011, "type" : "B"}, 
            "bge":      {"opcode": 0b1100011, "type" : "B"}, 
            "bltu":     {"opcode": 0b1100011, "type" : "B"}, 
            "bgeu":     {"opcode": 0b1100011, "type" : "B"}, 
            # S-type
            "sb":       {"opcode": 0b0100011, "type" : "S"}, 
            "sh":       {"opcode": 0b0100011, "type" : "S"}, 
            "sw":       {"opcode": 0b0100011, "type" : "S"}, 
            # I-type
            "addi":     {"opcode": 0b0010011, "type" : "I"}, 
            "slti":     {"opcode": 0b0010011, "type" : "I"}, 
            "sltiu":    {"opcode": 0b0010011, "type" : "I"}, 
            "xori":     {"opcode": 0b0010011, "type" : "I"}, 
            "ori":      {"opcode": 0b0010011, "type" : "I"}, 
            "andi":     {"opcode": 0b0010011, "type" : "I"}, 
            "slli":     {"opcode": 0b0010011, "type" : "I"}, 
            "srli":     {"opcode": 0b0010011, "type" : "I"}, 
            "srai":     {"opcode": 0b0010011, "type" : "I"}, 
            "lb":       {"opcode": 0b0000011, "type" : "I"}, 
            "lh":       {"opcode": 0b0000011, "type" : "I"}, 
            "lw":       {"opcode": 0b0000011, "type" : "I"}, 
            "lbu":      {"opcode": 0b0000011, "type" : "I"}, 
            "lhu":      {"opcode": 0b0000011, "type" : "I"}, 
            # R-type
            "add":      {"opcode": 0b0110011, "type" : "R"}, 
            "sub":      {"opcode": 0b0110011, "type" : "R"}, 
            "sll":      {"opcode": 0b0110011, "type" : "R"}, 
            "slt":      {"opcode": 0b0110011, "type" : "R"}, 
            "sltu":     {"opcode": 0b0110011, "type" : "R"}, 
            "xor":      {"opcode": 0b0110011, "type" : "R"}, 
            "srl":      {"opcode": 0b0110011, "type" : "R"}, 
            "sra":      {"opcode": 0b0110011, "type" : "R"}, 
            "or":       {"opcode": 0b0110011, "type" : "R"}, 
            "and":      {"opcode": 0b0110011, "type" : "R"}, 
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
        
    def emit_warning(self, warning_type, message, line_num=None):
        """Emits a warning based on current warning flags

        Args:
            warning_type (str): The type of the warning encountered
            message (str): The message for the warning
            line_num (int, optional): The line number of the warning. Defaults to None.

        Raises:
            ValueError: Raised if warnings are treated as errors
        """
        
        if self.warning_flags.get('suppress_all', False):
            return
        # Check if specific warning is disabled
        if warning_type == 'unused_label' and self.warning_flags.get('no_unused_label', False):
            return 
        if warning_type == 'immediate_range' and self.warning_flags.get('no_immediate_range', False):
            return
        
        # Format warning mesage
        if line_num is not None:
            warning_msg = f"Warning (line {line_num}): {message}"
        else:
            warning_msg = f"Warning: {message}"
            
        self.warnings.append(warning_msg)
        
        # Print warning unless suppressed
        if not self.warning_flags.get('suppress_all', False):
            print(warning_msg, file=sys.stderr)
            
        # Treat warning as error if flag is set
        if self.warning_flags.get('error_on_warning', False):
            raise ValueError(f"Error (Werror): {message}")
        
    def should_warn(self, warning_type):
        """Check if a warning type should be emitted

        Args:
            warning_type (str): The type of the warning 

        Returns:
            bool: True if it should be emitted, false if not
        """
        if self.warning_flags.get('suppress_all', False):
            return False
        
        if warning_type == 'unused_label':
            return not self.warning_flags.get('no_unused_label', False)
        elif warning_type == 'immediate_range':
            return not self.warning_flags.get('no_immediate_range', False)

        return True

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

            # If the label doesn't exist in the label dict, then take the string + current
            # PC and add it to the labels dict
            if label_match not in self.labels:
                self.labels[label_match] = {label_match, self.pc}

            # If no comments and no label, instruction is now clean. Append
            clean_lines.append(line)

            # Each instruction is 4 Bytes
            self.pc += 4

        return clean_lines

    def parse_instruction(self, line):
        """Parses single instruction and returns opcode + operands"""
        # Split line into opcode and operands with regex.
        opcode, operands = re.match('\s*([a-z]+)\s*(.*)$', line)
        return opcode, operands

    def decode_offset(self, operand):
        """Parses a operands of the style imm(rs1), returning the match, if any"""
        # Look for a number that may be positive or negative, then look for opening parenthesis
        # then look for a set of letters/numbers w/i the parenthesis, use operands[1] to match
        return re.match('(-?\d+)\(([a-zA-Z0-9]+)\)', operand) 

    def decode_immediate(self, imm_str, opcode):
        """Parses an immediate number in either dec, hex, or bin"""
        try:
            if imm_str.startswith("0x"):
                imm = int(imm_str, 16)
            elif imm_str.startswith("0b"):
                imm = int(imm_str, 2)
            else:
                imm = int(imm_str)
        except ValueError:
            raise ValueError(f"Invalid immediate: {imm_str}")
        
        if self.should_warn('immediate_range'):
            if opcode in self.type_to_mnemonics["I"] or opcode in self.type_to_mnemonics["S"] and not (-2048 <= imm < 2048):
                self.emit_warning('immediate_range', f"Immediate value {imm}, may be out of typical range (-2048 to 2047)")
            elif opcode in self.type_to_mnemonics["B"] and not (-4096 <= imm < 4096):
                self.emit_warning('immediate_range', f"Immediate value {imm}, may be out of typical range (-4096 to 4095)")
            elif opcode in self.type_to_mnemonics["J"] and not (-1048576 <= imm < 1048574):
                self.emit_warning('immediate_range', f"Immediate value {imm}, may be out of typical range (-1048576 to 1048574)")
            elif opcode in self.type_to_mnemonics["J"] and not (imm % 2 == 0):
                self.emit_warning('immediate_range', f"Immediate value {imm} for jump is not instruction aligned")
            elif opcode in self.type_to_mnemonics["U"] and not (0 <= imm < (1 << 20)):
                self.emit_warning('immediate_range', f"Immediate value {imm}, may be out of typical range (-4096 to 4095)")
            
        
        return imm
    
    def validate_registers(self, rd_str= None, rs1_str= None, rs2_str= None):
        """Validates registers from the registers dictionary"""
        registers = []

        if rd_str is not None:
            if rd_str in self.registers:
                registers.append(self.registers[rd_str])
            else:
                raise ValueError(f"Invalid register name: {rd_str}")
        
        if rs1_str is not None:
            if rs1_str in self.registers:
                registers.append(self.registers[rs1_str])
            else:
                raise ValueError(f"Invalid register name: {rs1_str}")
            
        if rs2_str is not None:
            if rs2_str in self.registers:
                registers.append(self.registers[rs2_str])
            else:
                raise ValueError(f"Invalid register name: {rs2_str}")

        return registers

    def encode_r_type(self, opcode, operands):
        """Encodes R-type instructions to binary"""

        rd_str = operands[0]
        rs1_str = operands[1]
        rs2_str = operands[2]

        registers = self.validate_registes(self, rd_str, rs1_str, rs2_str)

        rd = registers[0]
        rs1 = registers[1]
        rs2 = registers[2]

        f7 = self.func7[opcode]
        f3 = self.func3[opcode]
        op = self.opcodes[opcode]
        # Assemble instruction
        instruction = (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op
        return instruction

    def encode_i_type(self, opcode, operands):
        """Encodes I-type instructions to binary"""
        
        if opcode == "jalr":
            if len(operands) == 3:  # jalr rd, rs1, imm
                rd_str = operands[0]
                rs1_str = operands[1]
                imm_str = operands[2]
            elif len(operands) == 2:    # jalr rs1, imm (rd implied as ra)
                rd_str = "ra"
                rs1_str = operands[0]
                imm_str = operands[1]
            else:
                raise ValueError(f"Invalid operand count for JALR: {len(operands)}")
            
        # Handle loads with different formats: lw rd, imm(rs1)
        elif opcode in ["lb", "lh", "lw", "lbu", "lhu"]:

            if len(operands) != 2: # invalid form
                raise ValueError(f"Load instruction requires 2 operands, number of operands: {len(operands)}")
            
            rd_str = operands[0]
            # Look for a number that may be positive or negative, then look for opening parenthesis
            # then look for a set of letters/numbers w/i the parenthesis, use operands[1] to match
            match = self.decode_offset(self, operands[1])
            # IF we didn't find a match, the instruction format is invalid
            if not match:
                raise ValueError(f"Instruction format for load is invalid: {operands[1]}")

            imm_str = match.group(1) # Returns the immediate
            rs1_str = match.group(2) # Returns the first source register

        else:
            if len(operands) != 3:
                raise ValueError(f"I-type instruction requires 3 operands: {opcode}{', '.join(operands())}")

            rd_str = operands[0]
            rs1_str = operands[1]
            imm_str = operands[2]

        registers = self.validate_registers(self, rd_str=rd_str, rs1_str=rs1_str)

        rd = registers[0]
        rs1 = registers[1]

        imm = self.decode_immediate(self, imm_str)

        # if it's a shift, then can only shift by 31 at the most
        if opcode in ["slli", "srli", "srai"]:
            if not (0 <= imm < 32):
                raise ValueError(f"Shift amount out of range (0-31): {imm}")

            # SRAI uses a different func7
            f7 = self.func7[opcode]
            imm = (f7 << 5) | (imm & 0x1F)
        # Else, just check if in standard bounds & then encode
        else:
            if not (-2048 <= imm < 2048):
                if self.should_warn('immediate_range'):
                    
                # Allow proceeding though

            # Encode imm
            imm = imm & 0xFFF

        # Build instruction
        instruction = (imm << 20) | (rs1 << 15) | (self.func3[opcode] << 12) | (rd << 7) | self.opcodes[opcode]
        return instruction

    def encode_s_type(self, opcode, operands):
        """Encodes S-type instructions to binary"""

        if len(operands) != 2:
            raise ValueError(f"Error: Save instruction requires format of 'rs2 offset(rs1)', number of operands: {len(operands)}")
        
        rs2_str = operands[0]
        match = self.decode_offset(self, operands[1])

        if not match:
            raise ValueError(f"Error: Could not parse offset in save instruction!\tOperand: {operands[1]}")

        imm_str = match.group(1)
        rs1_str = match.group(2)

        registers = self.validate_registers(self, rs1_str=rs1_str, rs2_str=rs2_str)

        rs1 = registers[0]
        rs2 = registers[1]

        imm = self.decode_immediate(self, imm_str)

        if not (-2048 <= imm_str < 2048):  # Can probably bundle this into the decode imm func if we pass the opcode also
             if self.should_warn('immediate_range'):
                    self.emit_warning('immediate_range', f"Immediate value {imm}, may be out of typical range")

        imm_11_5 = (imm >> 5) & 0x7F # Grab upper 7 bits
        imm_4_0 = imm & 0x1F

        instruction = ((imm_11_5) << 25) | (rs2 << 20) | (rs1 << 15) | (self.func3[opcode] << 12) | (imm_4_0 << 7) | self.opcodes[opcode]
        return instruction

    def encode_b_type(self, opcode, operands, current_pc):
        """Encodes B-type instructions to binary"""

        # B type instruction form: beq rs1, rs2, offset. len(operands) == 3, should
        if len(operands) != 3:
            raise ValueError(f"Branch type instruction requires three operands, number of operands: {len(operands)}")
        
        rs1_str = operands[0]
        rs2_str = operands[1]
        label = operands[2]

        registers = self.validate_registers(self, rs1_str=rs1_str, rs2_str=rs2_str)

        rs1 = registers[0]
        rs2 = registers[1]

        if label not in self.labels:
            raise ValueError(f"Undefined label: {label}")
        # Labels dictionary uses the label to hash to a PC value
        target_addr = self.labels[label]
        imm = target_addr - current_pc

        if not (-4096 <= imm < 4096) or imm % 2 != 0:
            raise ValueError(f"Branch offset is out of range or not a multiple of 2: {imm}")

        imm_12 = (imm >> 12) & 0x1
        imm_11 = (imm >> 11) & 0x1
        imm_10_5 = (imm >> 5) & 0x3F
        imm_4_1 = (imm >> 1) & 0xF

        instruction = (imm_12 << 31) | (imm_10_5 << 25)  | (rs2 << 20) | (rs1 << 15) | (self.func3[opcode] << 12) | (imm_4_1 << 8) | (imm_11 << 7) | self.opcodes[opcode]
        return instruction

    def encode_j_type(self, opcode, operands, current_pc):
        """Encodes J-type instructions to binary"""

        # Validate count of operands
        if len(operands) == 2: # jal rd, label
            rd_str = operands[0]
            label = operands[1]
        elif len(operands) == 1: # jal label (imply rd = ra)
            rd_str = "ra"
            label = operands[0]
        else:
            raise ValueError(f"J-type instruction requires one or two operands: {opcode} {', '.join(operands)}")

        # opcode is the string of the instruction's opcode
        # operands is a list of strings that are the different groupings of operands within the instruction
        
        registers = self.validate_registers(self, rd_str=rd_str)

        rd = registers[0]

        if label not in self.labels:
            raise ValueError(f"Invalid label name. {label} is not referenced anywhere in the source code")
        
        target_addr = self.labels[label]
        offset = target_addr - current_pc

        if not (-1048576 <= offset < 1048576) or offset % 2 != 0:
            raise ValueError(f"Jump offset is out of range or not a multiple of 2: {offset}")
        
        imm_20 = (offset >> 20) & 0x1
        imm_10_1 = (offset >> 1) & 0x3FF
        imm_11 = (offset >> 11) & 0x1
        imm_19_12 = (offset >> 12) & 0x7F

        instruction = (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12) | (rd << 7) | self.opcodes[opcode]["opcode"]
        return instruction

    def encode_u_type(self, opcode, operands):
        """Encodes U-type instructions to binary"""

        if len(operands) != 2:
            raise ValueError(f"Invalid operand count in U-type instruction, opcode: {opcode}, operands: {', '.join(operands)}")
        
        rd_str = operands[0]
        imm_str = operands[1]

        registers = self.validate_registers(self, rd_str=rd_str)
        rd = registers[0]

        imm = self.decode_immediate(self, imm_str)

        if  and self.should_warn('immediate_range'):
            self.emit_warning('immediate_range', f"Immediate value {imm}, may be out of typical range")
        
        instruction = (imm << 12) | (rd << 7) | self.opcodes[opcode]
        return instruction

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
            self.memory.append(self.nop)

        # Check for unused labels
        if self.should_warn('unused_label'):
            for unused_label in self.unused_labels:
                self.emit_warning('unused_label', f"Label '{unused_label} is defined but never used")

        # Write each assembled instruction in to the output .mem file as an 8 character hex sequence
        with open(output_file, 'w', encoding=ascii) as file:
            for instr in self.memory:
                file.write(f"{instr:08x}\n")

        print(f"Successfully assembled {len(cleaned_lines)} instructions to {output_file}")
        return True
