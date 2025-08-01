# Test logical operations
addi t0, zero, 0x0F  # t0 = 15 (0x0F)
addi t1, zero, 0x33  # t1 = 51 (0x33)
and t2, t0, t1       # t2 = t0 & t1
or t3, t0, t1        # t3 = t0 | t1
xor t4, t0, t1       # t4 = t0 ^ t1