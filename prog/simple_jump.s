# Function call simulation
main:
    addi t0, zero, 10
    jal function     # Call function
    addi t0, t0, 1   # This runs after return

function:
    addi t1, zero, 20
    jalr zero, ra, 0 # Return to caller