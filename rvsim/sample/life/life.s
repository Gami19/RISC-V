	.text
	.global main
	.align  2

xsize    = 64
ysize    = 40
	
	## 
	## Life Game 64x40 for LCD Monitor on RISC-V
	## 
	
main:	la	t0, peripheral
	li	s10, 1
	sw	s10, 0(t0)
	sw	s10, 4(t0)
	sw	s10, 8(t0)
	addi	s10, s10, 1
	lw	s11, 12(t0)
	sw	s11, 0(t0)
	sw	s11, 4(t0)
	sw	s11, 8(t0)

	jal	clear		# clear VRAM area

	##
	## Display DATA area
	##
LOOP4:	la	t0, peripheral
	sw	s10, 0(t0)
	sw	s10, 4(t0)
	sw	s10, 8(t0)
	addi	s10, s10, 1
	
	jal	disp		# copy DATA to VRAM
#	jal	wait		# wait

	
	##
	## for( x=0 # x<64 # x++ )   a1 = x
	## 
	add	a1, zero, zero
FOR1:	addi	t0, zero, xsize
	bge	a1, t0, FOREND1

	##
	## for( y=0 # y<40 # y++ )   a2 = y
	## 
	add	a2, zero, zero
FOR2:	addi    t0, zero, ysize
	bge	a2, t0, FOREND2

BODY:	add	a3, zero, zero 	# number of plants, a3 = 0
	
	addi	a1, a1, -1	# NoP += what1(x-1,y-1)
	addi	a2, a2, -1
	jal	what1
	add	a3, a3, a0

SKIP1:	addi	a2, a2, 1	# NoP += what1(x-1,y  )
	jal	what1
	add	a3, a3, a0

SKIP2:	addi	a2, a2, 1	# NoP += what1(x-1,y+1)
	jal	what1
	add	a3, a3, a0

SKIP3:	addi	a1, a1, 1	# NoP += what1(x  ,y+1)
	jal	what1
	add	a3, a3, a0

SKIP4:	addi	a2, a2, -2	# NoP += what1(x  ,y-1)
	jal	what1
	add	a3, a3, a0

SKIP5:	addi	a1, a1, 1	# NoP += what1(x+1,y-1)
	jal	what1
	add	a3, a3, a0

SKIP6:	addi	a2, a2, 1	# NoP += what1(x+1,y  )
	jal	what1
	add	a3, a3, a0

SKIP7:	addi	a2, a2, 1	# NoP += what1(x+1,y+1)
	jal	what1
	add	a3, a3, a0

SKIP8:	addi	a1, a1, -1	# if( what1(x,y) ) {
	addi	a2, a2, -1
	jal	what1
	beq	a0, zero, CENTER0	

CENTER1:addi	t0, a3, -2	#	if( NoOf == 2 || NoOf == 3 ) 
	beq	t0, zero, SET	#		set1(x,y)
	addi	t0, a3, -3	#	else
	beq	t0, zero, SET	#		set0(x,y)
	j	DEL

CENTER0:addi	t0, a3, -3	# } else {
	beq	t0, zero, SET	#	if( NoOf == 3 )	set1(x,y)

DEL:	jal	SET0
	j	SKIP10

SET:	jal	SET1		# }

SKIP10:	addi	a2, a2, 1	# y++
	j	FOR2		# } // forend y
	
FOREND2:addi	a1, a1, 1	# x++
	j	FOR1		# } // forend x

FOREND1:
	j	LOOP4
	
	##
	## What1(a1,a2) return a0
	##
what1:	addi	sp, sp, -4
	sw	ra, 0 (sp)
	jal	check		 # area check
	beq	a0, zero, return # if out of range then return
	mv	t0, a2		 # t0 = Y
	slli	t1, t0, 4	 # t1 = Y << 4
	mv	t2, t1		 # t2 = Y << 4
	slli	t2, t2, 2	 # t2 = Y << 6
	add	t0, t1, t2	 # t0 = (Y<<6)+(Y<<4)
	add	t0, t0, a1	 # t0 = Y*80+X
	la	t1, vrambase
	add	t1, t1, t0	 # t1 = vrambase+Y*80+X
	lb	a0, 0(t1)
	srli	a0, a0, 6	 # a0 >>= 6, " "=0, "@"=1
return:	lw	ra, 0(sp)
	addi	sp, sp, 4
	jr	ra

	##
	## check boundary
	## 
check:	blt	a1, zero, check_o # if out of left side then check_o
	addi	t0, zero, xsize
	bge	a1, t0, check_o	  # if out of right side then check_o
	blt	a2, zero, check_o # if out of upper side then check_o
	addi	t0, zero, ysize
	bge	a2, t0, check_o	  # if out of bottom side then check_o
	addi	a0, zero, 1       # if inside then a0=1
	jr	ra
check_o:add	a0, zero, zero	  # if outside then return a0=0
	jr	ra
	
	##
	## SET1(x,y) sets "@" into DATA[x,y]
	##
SET1:	slli	t0, a2, 6	# t0 = 64*Y
	add	t0, t0, a1	# t0 = Y*xsize+X
	la	t1, DATA
	add	t1, t1, t0	# t1 = DATA+Y*xsize+X
	addi	t0, zero, '@'
	sb	t0, 0( t1 )	# *(DATA+Y*xsize+X) = '@'
	jr	ra

	##
	## SET0(x,y) sets " " into DATA[x,y]
	##
SET0:	slli	t0, a2, 6	# t0 = 64*Y
	add	t0, t0, a1	# t0 = Y*xsize+X
	la	t1, DATA
	add	t1, t1, t0	# t1 = DATA+Y*xsize+X
	addi	t0, zero, ' '
	sb	t0, 0( t1 )	# *(DATA+Y*xsize+X) = ' '
	jr	ra

	##
	## Display :  Copy DATA -> VRAM area
	## 
disp:	la	t0, DATA
	la	t1, vrambase
	addi	t2, zero, ysize
disp1:	addi	t3, zero, xsize

disp2:	lb	t4, 0( t0 )
	sb	t4, 0( t1 )
	addi	t0, t0, 1
	addi	t1, t1, 1
	addi	t3, t3, -1
	bne	t3, zero, disp2
	addi	t1, t1, 80 - xsize
	addi	t2, t2, -1
	bne	t2, zero, disp1
	jr	ra
	
	##
	## Clear :  clear VRAM area
	## 
clear:	la	t1, vrambase
	addi	t2, zero, ysize
clear1:	addi	t3, zero, xsize

clear2:	addi	t4, zero, ' '
	sb	t4, 0( t1 )
	addi	t1, t1, 1
	addi	t3, t3, -1
	bne	t3, zero, clear2
	addi	t1, t1, 80 - xsize
	addi	t2, t2, -1
	bne	t2, zero, clear1
	jr	ra
	
	## 
	## wait
	## 
wait:	la	t0, 50
wait2:	la	t1, 1024
wait1:	addi	t1, t1, -1
	bne	t1, zero, wait1
	addi	t0, t0, -1
	bne	t0, zero, wait2
	jr	ra

	.data
	.align	2
DATA:           #0----+----1----+----2----+----3----+----4----+----5----+----6---
	.ascii	"                                                                " #00
	.ascii	"                                                                " #01
	.ascii	"                         @                                      " #02
	.ascii	"                       @ @                                      " #03
	.ascii	"             @@      @@            @@                           " #04
	.ascii	"            @   @    @@            @@                           " #05
	.ascii	" @@        @     @   @@                                         " #06
	.ascii	" @@        @   @ @@    @ @                                      " #07
	.ascii	"           @     @       @                                      " #08
	.ascii	"            @   @                                               " #09
	.ascii	"             @@                              @    @             " #10
	.ascii	"                                           @@ @@@@ @@           " #11
	.ascii	"                                             @    @             " #12
	.ascii	"                                                                " #13
	.ascii	"                                                                " #14
	.ascii	"                                                                " #15
	.ascii	"                                                                " #16
	.ascii	"                                                                " #17
	.ascii	"                                                                " #18
	.ascii	"                                                                " #19
	.ascii	"      @                                                         " #20
	.ascii	"      @                                                         " #21
	.ascii	"      @                                                         " #22
	.ascii	"                                                                " #23
	.ascii	"                                                                " #24
	.ascii	"                                                                " #25
	.ascii	"                                                                " #26
	.ascii	"                                                                " #27
	.ascii	"                                                                " #28
	.ascii	"                                                                " #29
	.ascii	"                                                                " #30
	.ascii	"                                                                " #31
	.ascii	"                                                                " #32
	.ascii	"                                                                " #33
	.ascii	"                                                                " #34
	.ascii	"                                                                " #35
	.ascii	"                                                                " #36
	.ascii	"                                                                " #37
	.ascii	"                                                                " #38
	.ascii	"                                                                " #39

	.align	2

vrambase   = _vram_base
peripheral = _peripheral	
