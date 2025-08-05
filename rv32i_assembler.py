"""Assembler for simple RISC-V code for use by my RISC-V CPU"""

import re
import sys
import os


# Strategy: Two pass assembly - First pass collects labels and addresses while second pass does 
# the actual assembly into binary
class Alert:
    def __init__(self, type, message, line_num, warning_type = None):
        self.type = type,
        self.message = message,
        self.line_num = line_num
        self.warning_type = warning_type or None

class AssemblerResults:
    def __init__(self):
        self.success = False
        self.alerts = [] # List of Alert objects

class RV32IAssembler:
    """Contains all vars and methods for preprocess, assembly, and file writing"""
    def __init__(self, warning_Flags=None):
        # Warning system
        self.warning_flags = warning_Flags or {}
        self.warnings = []
        # Init mem, labels, PC [bytes], & NOP command
        self.labels = {}
        self.referenced_labels = []
        self.memory = []
        self.pc = 0
        self.NOP = 0x00000013
        self.MAX_INSTRUCTIONS = 1024
        self.line_nums = []
        
        self.current_line_index = 1
        
        self.AssemblerResults = AssemblerResults()        

        # opcodes - Use structured dictionary
        self.opcodes = {
            "lui":      {"opcode": 0b0110111, "type" : "U"},
            "auipc":    {"opcode": 0b0010111, "type" : "U"},
            "jal":      {"opcode": 0b1101111, "type" : "J"}, 
            "jalr":     {"opcode": 0b1100111, "type" : "I"}, 
            "beq":      {"opcode": 0b1100011, "type" : "B"}, 
            "bne":      {"opcode": 0b1100011, "type" : "B"}, 
            "blt":      {"opcode": 0b1100011, "type" : "B"}, 
            "bge":      {"opcode": 0b1100011, "type" : "B"}, 
            "bltu":     {"opcode": 0b1100011, "type" : "B"}, 
            "bgeu":     {"opcode": 0b1100011, "type" : "B"}, 
            "sb":       {"opcode": 0b0100011, "type" : "S"}, 
            "sh":       {"opcode": 0b0100011, "type" : "S"}, 
            "sw":       {"opcode": 0b0100011, "type" : "S"}, 
            "addi":     {"opcode": 0b0010011, "type" : "I"}, 
            "slti":     {"opcode": 0b0010011, "type" : "I"}, 
            "sltiu":    {"opcode": 0b0010011, "type" : "I"}, 
            "xori":     {"opcode": 0b0010011, "type" : "I"}, 
            "ori":      {"opcode": 0b0010011, "type" : "I"}, 
            "andi":     {"opcode": 0b0010011, "type" : "I"}, 
            "slli":     {"opcode": 0b0010011, "type" : "I", "subtype" : "shift"}, 
            "srli":     {"opcode": 0b0010011, "type" : "I", "subtype" : "shift"}, 
            "srai":     {"opcode": 0b0010011, "type" : "I", "subtype" : "shift"}, 
            "lb":       {"opcode": 0b0000011, "type" : "I", "subtype" : "load"}, 
            "lh":       {"opcode": 0b0000011, "type" : "I", "subtype" : "load"}, 
            "lw":       {"opcode": 0b0000011, "type" : "I", "subtype" : "load"}, 
            "lbu":      {"opcode": 0b0000011, "type" : "I", "subtype" : "load"}, 
            "lhu":      {"opcode": 0b0000011, "type" : "I", "subtype" : "load"}, 
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

        self.parse_count = 0
       
    def reset_assembler(self):
        self.warnings = []
        self.unused_labels = set()
        self.labels = {}
        self.used_labels = set()
        self.memory = []
        self.line_nums = []
        self.pc = 0

    def get_type(self, mnemonic):
        return self.opcodes.get(mnemonic, {}).get("type", None)
        
    def should_warn(self, warning_type):

        type = warning_type.lower()
        
        if self.warning_flags.get('suppress_all', False):
            return False
        if type == 'unused_label':
            return not self.warning_flags.get('no_unused_label', False)
        elif type == 'immediate_range':
            return not self.warning_flags.get('no_immediate_range', False)

        return True
        
    def record_alert(self, alert_type, message, warning_type = None):

        type = alert_type.lower()

        if  type == "warning":
            # See if the warning should be suppressed    
            if self.warning_flags.get('suppress_all', False):
                return
            if warning_type == 'unused_label' and self.warning_flags.get('no_unused_label', False):
                return
            if warning_type == 'immediate_range' and self.warning_flags.get('no_immediate_range', False):
                return 
        # Record the alert
        alert = Alert(type, message, self.line_nums[self.current_line_index], warning_type)
        # Append to results
        self.AssemblerResults.alerts.append(alert)

    def preprocessor(self, lines):
        """First pass: Collect labels + addresses. Remove comments"""

        clean_lines = []
        self.pc = 0
        line_num = 1

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
            if label_match:
                label = label_match.group(1)
                if label_match not in self.labels:
                    self.labels[label] = self.pc
                    
            elif label_match is None:
                # If no comments and no label, instruction is now clean. Append
                clean_lines.append(line)
                self.line_nums.append(line_num)

            # Each instruction is 4 Bytes
            self.pc += 4
            line_num += 1

        return clean_lines

    def parse_instruction(self, line):
        """Parses single instruction and returns opcode + operands"""
        # Split line into opcode and operands with regex.
        match = re.match(r'\s*([a-z]+)\s*(.*)$', line)
        opcode, operand_str = match.groups()
        operands = [op for op in re.split(r'[,\s]+', operand_str.strip()) if op]
        return opcode, operands

    def parse_offset(self, operand):
        """Parses a operands of the style imm(rs1), returning the match, if any"""
        # Look for a number that may be positive or negative, then look for opening parenthesis
        # then look for a set of letters/numbers w/i the parenthesis, use operands[1] to match
        return re.match('(-?\d+)\(([a-zA-Z0-9]+)\)', operand) 

    def decode_immediate(self, opcode, imm_str = None, label= None, current_pc = None):
        """Parses an immediate number in either dec, hex, or bin"""
        
        type = self.get_type(opcode) 

        if type == "B" or type == "J":

            if label == None or current_pc == None:
                self.record_alert("internal", f"No label or pc provided for branch/jump instruction")
                raise ValueError
            elif label not in self.labels:
                self.record_alert("error", f"Instruction references non-existent label")
                raise ValueError
            
            target_addr = self.labels[label]
            imm = target_addr - current_pc
            
            if label not in self.referenced_labels: # Add to referenced list if not already referenced
                self.referenced_labels.append(label)
            
        else:
            if imm_str == None:
                self.record_alert("internal", "No immediate string passed to non-branch/jump insrtuction")
                raise ValueError
            try:
                if imm_str.startswith("0x"):
                    imm = int(imm_str, 16)
                elif imm_str.startswith("0b"):
                    imm = int(imm_str, 2)
                else:
                    imm = int(imm_str)
            except ValueError:
                self.record_alert("error", "Invalid immediate value, '{imm_str}'")
                raise ValueError
        
        if self.should_warn('immediate_range'):       
      
            if type == "I" or type == "S" and not (-2048 <= imm < 2048):
                self.record_alert("warning", f"Immediate value {imm}, may be out of typical range (-2048 to 2047)", warning_type='immediate_range')
                
            elif type == "B" and not (-4096 <= imm < 4096):
                self.record_alert("warning", f"Immediate value {imm}, may be out of typical range (-4096 to 4095)", warning_type='immediate_range')
                
            elif type == "J" and not (-1048576 <= imm < 1048574):
                self.record_alert("warning", f"Immediate value {imm}, may be out of typical range (-1048576 to 1048574)", warning_type='immediate_range')
                
            elif type == "J" and not (imm % 2 == 0): # Should be 4 to be 32b aligned?
                self.record_alert("error", f"Jump offset value, {imm}, is not instruction aligned")
                raise ValueError
                
            elif type == "U" and not (0 <= imm < (1 << 20)):
                self.record_alert("warning", f"Upper mmediate value {imm}, is out of range", warning_type= 'immediate_range')
        
        return imm
    
    def validate_registers(self, rd_str= None, rs1_str= None, rs2_str= None):
        """Validates registers from the registers dictionary"""
        registers = []

        if rd_str is not None:
            if rd_str in self.registers:
                registers.append(self.registers[rd_str])
            else:
                self.record_alert("error", f"Invalid register name: {rd_str}")
                raise ValueError
        
        if rs1_str is not None:
            if rs1_str in self.registers:
                registers.append(self.registers[rs1_str])
            else:
                self.record_alert("error", f"Invalid register name: {rs1_str}")
                raise ValueError
            
        if rs2_str is not None:
            if rs2_str in self.registers:
                registers.append(self.registers[rs2_str])
            else:
                self.record_alert("error", f"Invalid register name: {rs2_str}")
                raise ValueError

        return registers

    def encode_r_type(self, opcode, operands):
        """Encodes R-type instructions to binary"""

        rd_str = operands[0]
        rs1_str = operands[1]
        rs2_str = operands[2]

        registers = self.validate_registers(rd_str=rd_str, rs1_str=rs1_str, rs2_str=rs2_str)

        rd = registers[0]
        rs1 = registers[1]
        rs2 = registers[2]

        f7 = self.func7[opcode]
        f3 = self.func3[opcode]
        op = self.opcodes[opcode]["opcode"]
        # Assemble instruction
        instruction = (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op
        return instruction

    def encode_i_type(self, opcode, operands):
        """Encodes I-type instructions to binary"""
        try:
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
                    self.record_alert("error", f"Invalid operand count for jalr instruction: {len(operands)}")
                    raise ValueError
                
            # Handle loads with different formats: lw rd, imm(rs1)
            elif self.opcodes[opcode].get("subtype", '') == "load":
            
                if len(operands) != 2: # invalid form
                    self.record_alert("error", f"Load instruction requires 2 operands, not {len(operands)}")
                    raise ValueError
                
                rd_str = operands[0]
                # Look for a number that may be positive or negative, then look for opening parenthesis
                # then look for a set of letters/numbers w/i the parenthesis, use operands[1] to match
                match = self.parse_offset(operands[1])
                # IF we didn't find a match, the instruction format is invalid
                if not match:
                    self.record_alert("error", f"Load instruction format is invalid")
                    raise ValueError

                imm_str = match.group(1) # Returns the immediate
                rs1_str = match.group(2) # Returns the first source register

            else:
                if len(operands) != 3:
                    self.record_alert("error", f"Immediate instruction format is invalid: {opcode}{', '.join(operands)}")
                    raise ValueError

                rd_str = operands[0]
                rs1_str = operands[1]
                imm_str = operands[2]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            line_number = exc_tb.tb_lineno
            print(f"Error on line: {line_number}, Type: {exc_type.__name__}, Message: {e}")

        registers = self.validate_registers(rd_str=rd_str, rs1_str=rs1_str)

        rd = registers[0]
        rs1 = registers[1]

        imm = self.decode_immediate(opcode, imm_str=imm_str)

        # if it's a shift, then can only shift by 31 at the most
        # todo: Roll this into decode immediate 
        if self.opcodes[opcode].get("subtype", '') == "shift":
            if not (0 <= imm < 32):
                self.record_alert("warning")
                raise ValueError(f"Shift amount out of range (0-31): {imm}")

            # SRAI uses a different func7
            f7 = self.func7[opcode]
            imm = (f7 << 5) | (imm & 0x1F)
        else:
            imm = imm & 0xFFF

        # Build instruction
        instruction = (imm << 20) | (rs1 << 15) | (self.func3[opcode] << 12) | (rd << 7) | self.opcodes[opcode]["opcode"]
        return instruction

    def encode_s_type(self, opcode, operands):
        """Encodes S-type instructions to binary"""

        if len(operands) != 2:
            self.record_alert("error", f"Save instruction requires format of 'rs2 offset(rs1)', number of operands: {len(operands)}")
            raise ValueError
        
        rs2_str = operands[0]
        match = self.parse_offset(operands[1])

        if not match:
            self.record_alert("error", f"Could not parse offset in save instruction\tOperand: {operands[1]}")
            raise ValueError

        imm_str = match.group(1)
        rs1_str = match.group(2)

        registers = self.validate_registers(rs1_str=rs1_str, rs2_str=rs2_str)

        rs1 = registers[0]
        rs2 = registers[1]

        imm = self.decode_immediate(opcode, imm_str=imm_str)

        imm_11_5 = (imm >> 5) & 0x7F # Grab upper 7 bits
        imm_4_0 = imm & 0x1F

        instruction = ((imm_11_5) << 25) | (rs2 << 20) | (rs1 << 15) | (self.func3[opcode] << 12) | (imm_4_0 << 7) | self.opcodes[opcode]["opcode"]
        return instruction

    def encode_b_type(self, opcode, operands, current_pc):
        """Encodes B-type instructions to binary"""

        # B type instruction form: beq rs1, rs2, offset. len(operands) == 3, should
        if len(operands) != 3:
            self.record_alert("error", f"Branch type instruction requires three operands, number of operands: {len(operands)}")
            raise ValueError
        
        rs1_str = operands[0]
        rs2_str = operands[1]
        label = operands[2]

        registers = self.validate_registers(rs1_str=rs1_str, rs2_str=rs2_str)

        rs1 = registers[0]
        rs2 = registers[1]


        imm = self.decode_immediate(opcode, label=label, current_pc=current_pc)
        
        print(imm)

        imm_12 = (imm >> 12) & 0x1
        imm_11 = (imm >> 11) & 0x1
        imm_10_5 = (imm >> 5) & 0x3F
        imm_4_1 = (imm >> 1) & 0xF

        instruction = (imm_12 << 31) | (imm_10_5 << 25)  | (rs2 << 20) | (rs1 << 15) | (self.func3[opcode] << 12) | (imm_4_1 << 8) | (imm_11 << 7) | self.opcodes[opcode]["opcode"]
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
            self.record_alert("error", f"J-type instruction requires one or two operands: {opcode} {', '.join(operands)}")
            raise ValueError

        registers = self.validate_registers(rd_str=rd_str)

        rd = registers[0]

        imm = self.decode_immediate(opcode, label=label, current_pc=current_pc)
        
        imm_20 = (imm >> 20) & 0x1
        imm_10_1 = (imm >> 1) & 0x3FF
        imm_11 = (imm >> 11) & 0x1
        imm_19_12 = (imm >> 12) & 0x7F

        instruction = (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12) | (rd << 7) | self.opcodes[opcode]["opcode"]
        return instruction

    def encode_u_type(self, opcode, operands):
        """Encodes U-type instructions to binary"""

        if len(operands) != 2:
            self.record_alert("error", f"Invalid operand count in U-type instruction, opcode: {opcode}, operands: {', '.join(operands)}")
            raise ValueError
        
        rd_str = operands[0]
        imm_str = operands[1]

        registers = self.validate_registers(rd_str=rd_str)
        rd = registers[0]

        imm = self.decode_immediate(opcode, imm_str=imm_str)

        instruction = (imm << 12) | (rd << 7) | self.opcodes[opcode]["opcode"]
        return instruction

    def assemble_instruction(self, line, current_pc):
        """Assembles one instruction to machine code"""
        opcode, operands = self.parse_instruction(line)
        
        type = self.get_type(opcode) 

        self.parse_count +=1
   
        print(f"Parse count: {self.parse_count}")
        print(f"{line}\n")
        try:
            match type:
                case "R":
                    return self.encode_r_type(opcode, operands)   
                case "I":
                    return self.encode_i_type(opcode, operands)
                case "S":
                    return self.encode_s_type(opcode, operands)
                case "B":
                    return self.encode_b_type(opcode, operands, current_pc)
                case "J":
                    return self.encode_j_type(opcode, operands, current_pc)
                case "U":
                    return self.encode_u_type(opcode, operands)
                case None:
                    self.record_alert("error", f"Instruction '{opcode}' is not supported")
                    raise ValueError
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            line_number = exc_tb.tb_lineno
            print(f"Error on line: {line_number}, Type: {exc_type.__name__}, Message: {e}\n")
            return self.AssemblerResults
        
    def assemble(self, input, output):
        """Runs the entire assembly procedure"""
        
        self.reset_assembler()

        lines = input.readlines()
        cleaned_lines = self.preprocessor(lines)

        # If program is too large, throw error
        if len(cleaned_lines) > self.MAX_INSTRUCTIONS:
            # todo: change to correct err handling
            self.record_alert("error", f"Number of instructions in input is larger than memory size! Max number of instructions is {self.MAX_INSTRUCIONS}")
            return self.AssemblerResults # Success defaults to fail
        
        # Second pass is actually assembling the instructions
        self.pc = 0
        index = 0
        for line in cleaned_lines:
            try:
                self.current_line_index = index
                instruction = self.assemble_instruction(line, self.pc)
                self.memory.append(instruction)
                self.pc += 4
                index += 1
            except Exception as e: # Errors and warnings are recorded in the results
                exc_type, exc_obj, exc_tb = sys.exc_info()
                line_number = exc_tb.tb_lineno
                print(f"Error on line: {line_number}, Type: {exc_type.__name__}, Message: {e}")
                return self.AssemblerResults

        # .mem file needs to fill the entire memory
        while len(self.memory) < self.MAX_INSTRUCTIONS: # Fill remaining memory with zeros 
            self.memory.append(self.NOP)

        # Check for unused labels
        if self.should_warn('unused_label'):
            unused_labels = [key for key in self.labels.keys() if key not in self.unused_labels]
            for label in unused_labels:
                self.record_alert('unused_label', f"Label '{label}' is defined but never used")

        # Write each assembled instruction in to the output .mem file as an 8 character hex sequence
        for instr in self.memory:
            output.write(f"{instr:08x}\n")
            
        self.AssemblerResults.success = True
        
        return self.AssemblerResults

