# Test LUI and AUIPC
lui t0, 0x12345      # Load upper immediate
auipc t1, 0x1000     # Add upper immediate to PC
addi t0, t0, 0x678   # Complete the full 32-bit value