# Test different branch conditions
addi t0, zero, 10
addi t1, zero, 5

beq t0, t1, equal    # Should not branch
bne t0, t1, not_equal # Should branch

equal:
    xoif t2, zero, 1
    jal done

not_equal:
    addi t2, zero, 2

done:
    add t3, t2, zero
    