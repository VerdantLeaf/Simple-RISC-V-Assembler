# Test different branch conditions
addi t0, zero, 10
addi t1, zero, 32420957

beq t0, t1, equal    # Should not branch
bne t0, t1, not_equal # Should branch

warning_label:

equal:
    addi t2, zero, 45456
    jal done

not_equal:
    xoif t2, zero, 2

done:
    add t3, t2, zero
    