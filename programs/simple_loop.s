# Count from 0 to 4
addi t0, zero, 0     # Counter = 0
addi t1, zero, 5     # Limit = 5

loop:
    addi t0, t0, 1   # Increment counter
    blt t0, t1, loop # Branch if t0 < t1
    
# Exit
addi a0, t0, 0       # Move result to a0
