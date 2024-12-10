	.text
	.globl	main
	.align	2
	
main:	addi	sp, sp, -4
        sw	ra, 0 (sp)
	addi	a0, zero, 4	# n = 4
	jal	fact		# call fact
        lw	ra, 0 (sp)
	addi	sp, sp,  4
	jr	ra		# ret

fact:	addi	sp, sp, -8
        sw	ra, 4(sp)
        sw	a0, 0(sp)
	slti	t0, a0, 1
        beq	t0, zero, L1
        addi	a1, zero, 1
        addi	sp, sp, 8
        jr	ra		# ret

L1:	addi	a0, a0, -1
        jal	fact		# call fact
        lw	a0, 0(sp)
        lw	ra, 4(sp)
        addi	sp, sp, 8
        mul	a1, a1, a0
        jr	ra		# ret
