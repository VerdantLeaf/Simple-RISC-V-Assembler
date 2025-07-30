# Load and store operations
addi sp, zero, 1000  # Set stack pointer
addi t0, zero, 42    # Load immediate value
sw t0, 0(sp)         # Store to memory
lw t1, 0(sp)         # Load from memory
sb t0, 4(sp)         # Store byte
lb t2, 4(sp)         # Load byte
