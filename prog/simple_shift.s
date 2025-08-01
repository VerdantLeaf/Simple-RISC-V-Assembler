# Test shift instructions
addi t0, zero, 8     # t0 = 8
slli t1, t0, 2       # t1 = t0 << 2 (32)
srli t2, t1, 1       # t2 = t1 >> 1 (16)
addi t3, zero, -8    # t3 = -8
srai t4, t3, 1       # t4 = t3 >> 1 (arithmetic, -4)