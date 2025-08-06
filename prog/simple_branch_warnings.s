# Test different branch conditions
addi t0, zero, 333334
addi t1, zero, 5

beq t0, t1, equal    # Should not branch
bne t0, t1, not_equal # Should branch

equal:
    addi t2, zero, 458792
    jal done

not_equal:
    addi t2, zero, 43436907

done:
    add t3, t2, zero
    