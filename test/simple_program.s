# More complex program with multiple features
start:
    lui t0, 0x1000      # Load base address
    addi t1, zero, 100  # Counter limit
    addi t2, zero, 0    # Sum accumulator

sum_loop:
    add t2, t2, t1      # Add counter to sum
    addi t1, t1, -1     # Decrement counter
    bne t1, zero, sum_loop  # Continue if not zero
    
    # Store result
    sw t2, 0(t0)        # Store sum at base address
    
    # Jump to end
    jal end_program

end_program:
    addi a0, t2, 0      # Move result to a0