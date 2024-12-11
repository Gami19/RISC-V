	#
	# Squash Game on RISC-V
	#
	
vrambase= _vram_base
ledbase = _peripheral
WIDTH	= 80
HEIGHT  = 45
DELAY   = 900    # 100

ball	=  0	# ball count
bx	=  4	# ball x
by	=  8	# ball y
vx	= 12	# ball vector x
vy	= 16	# ball vector y
nx	= 20	# ball next x
ny	= 24	# ball next y
py	= 28	# paddle position
pl	= 32	# paddle length
npy	= 36	# paddle next position
hit	= 40	# paddle hit
count	= 44	# paddle hit count
delay	= 48	# delay counter

data_size = delay + 4
	
	.text
	.global	main
	.align	2
	
main:	addi	sp, sp, -4
	sw	ra, 0(sp)	# push return address

	# ボールの初期位置を設定
	call random_position  # ランダムな位置を取得
	sw a0, bx(gp)  # ランダムなx座標を保存
	sw a1, by(gp)  # ランダムなy座標を保存

	# ボールの移動
	lw t0, bx(gp)
	addi t0, t0, -1
	sw t0, nx(gp)

	# 衝突チェック
	lw t0, nx(gp)
	bne t0, t1, SKIP3

	# ここでボールの位置をリセットする処理を追加
	# もしボールが画面外に出た場合、ボールの位置を初期化する
	li t0, 4  # 初期x座標
	sw t0, bx(gp)
	li t0, 8  # 初期y座標
	sw t0, by(gp)

LOOP0:	la	gp, data	# gp = data pointer
	li	t0, 3		# ball = 3
	sw	t0, ball(gp)

	# ランダムなボールの初期位置を設定
	call random_position  # ランダムな位置を取得
	sw a0, bx(gp)  # ランダムなx座標を保存
	sw a1, by(gp)  # ランダムなy座標を保存

	li	t0, 1		# vy = vx = 1
	sw	t0, vx(gp)
	sw	t0, vy(gp)
	li	t0, 42		# py = 10
	sw	t0, py(gp)
	li	t0, 3		# pl = 3
	sw	t0, pl(gp)	
	li	t0, 0		# count = 0
	sw	t0, count(gp)
	la	t1, ledbase	# test code
	sw	t0, 0(t1)
	li	t0, DELAY	# delay = DELAY
	sw	t0, delay(gp)

	#
	# make field
	#
	li	s1, 0		# for( i=0; i < WIDTH ; i++ )/* all clear */
LOOP1:	li	t0, WIDTH
	bge	s1, t0, BREAK1
	li	s2, 0		# for( j=0; j < HEIGHT; j++ ) 
LOOP2:	li	t0, HEIGHT
	bge	s2, t0, BREAK2
	move	a1, s1
	move	a2, s2
	li	a3, ' '
	call	v_putc
	addi	s2, s2, 1
	j	LOOP2
BREAK2:	addi	s1, s1, 1
	j	LOOP1

BREAK1:	
	li	a1, 0
	move	a2, a1
	la	a3, str_1	# v_puts( 0, 0, "RISC-V Processor Video System                  " ) ;
	call	v_puts
	
	addi	a2, a2, 1
	la	a3, str_2	# v_puts( 1, 2, "Squash Game" );
	call	v_puts
	
	li	a1, 58
	la	a3, str_3	# v_puts( 1, 58, "Balls:" );
	call	v_puts
	
	li	a1, 68
	la	a3, str_4	# v_puts( 1, 68, "Hit count:" );
	call	v_puts

	li	s1, 0
LOOP3:	li	t0, WIDTH
	bge	s1, t0, BREAK3	# for( i=0; i < WIDTH ; i++ )
	move	a1, s1
	li	a2, 2
	li	a3, '-'
	call	v_putc		# v_putc( i,       2, '-' );/* Top wall */
	li	a2, HEIGHT-1
	call	v_putc		# v_putc( i,HEIGHT-1, '-' );/* Bottom wall */
	addi	s1, s1, 1
	j	LOOP3

BREAK3:
	li	s1, 2
LOOP4:	li	t0, HEIGHT
	bge	s1, t0, BREAK4	# for( i=2; i < HEIGHT ; i++ )
	li	a1, 0
	li	a3, '|'
	move	a2, s1
	call 	v_putc		# v_putc( 0, i, '|' );/* Left side wall */
	addi	s1, s1, 1
	j	LOOP4

BREAK4:	li	a1, 28
	li	a2, 20
	la	a3, str_5	# v_puts( 28, 20, "Push center button to start!" );
	call	v_puts

LOOP5:	call	getsw
	srli	a0, a0, 20	# if( sw == 0x100000 ) break; /* center = start */
	li	t0, 1
	beq	a0, t0, BREAK5
	j	LOOP5

BREAK5:	li	a1, 28
	li	a2, 20
	la	a3, str_6	# "                            "
	call	v_puts

LOOP:	# make paddle
	li	s1, 0		#for( i=0; i < pl; i++ )
LOOP6:	lw	t0, pl(gp)
	bge	s1, t0, BREAK6
	li	a1, 10
	lw	a2, py(gp)
	add	a2, a2, s1
	li	a3, 'O'
	call	v_putc		# v_putc( 78, py+i, 'O')
	addi	s1, s1, 1
	j	LOOP6

BREAK6:	
	lw	a1, bx(gp)
	lw	a2, by(gp)
	li	a3, '@'
	call	v_putc		# v_putc( bx, by, '@' );           /* make ball */

	li	a1, 64
	li	a2, 1
	lw	a3, ball(gp)
	addi	a3, a3, '0'
	call	v_putc		# v_putc( 64,  1, '0'+ball );      /* display ball count */

	li	a1, 78
	li	a2, 1
	lw	a3, count(gp)
	la	t1, ledbase
	sw	a3, 0(t1)
	li	t0, 10
	div	a3, a3, t0
	addi	a3, a3, '0'
	call	v_putc		# v_putc( 78,  1, '0'+(count/10)); /* display paddle hit count */
	addi	a1, a1, 1
	lw	a3, count(gp)
	li	t0, 10
	rem	a3, a3, t0
	addi	a3, a3, '0'
	call	v_putc		# v_putc( 79, 1, '0'+(count%10)); /* display paddle hit count */

	# wait
	lw	a1, delay(gp)
	call	wait		# wait( delay );

	# ball move
	lw	t0, bx(gp)
	addi	t0, t0, -1
	sw	t0, nx(gp)

	# collision check
	lw	t0, nx(gp)
	bne	t0, t1, SKIP3

	#li	t0, 1		# nx = 1
	#sw	t0, nx(gp)
	#lw	t0, by(gp)	# ny = by
	#sw	t0, ny(gp)
	#lw	t0, vx(gp)	# vx = -vx
	#sub	t0, zero, t0
	#sw	t0, vx(gp)

SKIP3:	# paddle check
	lw	t0, nx(gp)	# if( nx == 10 ) 
	li	t1, 10
	li	s1, 0		# for( i=0 , hit=0 ; i < pl ; i++ ) 
	sw	s1, hit(gp)
	beq	t0, t1,	LOOP7
	j	SKIP4

	# パドルのヒット判定
	lw t0, hit(gp)  # ヒットフラグを取得
	beq t0, zero, SKIP8
	# ヒットした場合の処理を追加
	# ヒットカウントを増やす処理を追加
	lw t0, count(gp)
	addi t0, t0, 1
	sw t0, count(gp)
	
LOOP7:	lw	s2, pl(gp)
	bge	s1, s2, SKIP4
	lw	s2, by(gp)
	lw	s3, py(gp)
	add	s3, s3, s1	# if( by == py+i ) 
	beq	s2, s3,	BREAK8
	

BREAK7:	add	s1, s1, 1
	j	LOOP7		# 
SKIP4:
	#  paddle hit
	lw	t0, hit(gp)	# if( hit ) 
	beq	t0, zero, SKIP8
	#lw	t0, bx(gp)	# nx = bx
	#sw	t0, nx(gp)
	#lw	t0, by(gp)	# ny = by
	#sw	t0, ny(gp)
	#lw	t0, vx(gp)	# vx = -vx
	#sub	t0, zero, t0
	#sw	t0, vx(gp)
	#lw	t0, count(gp)	# count++
	#addi	t0, t0, 1
	#sw	t0, count(gp)

	li	a1, 78
	li	a2, 1
	lw	a3, count(gp)
	la	t1, ledbase
	sw	a3, 0(t1)
	li	t0, 10
	div	a3, a3, t0
	addi	a3, a3, '0'
	call	v_putc		# v_putc( 78, 1, '0'+(count/10)); /* display paddle hit count */
	addi	a1, a1, 1
	lw	a3, count(gp)
	li	t0, 10
	rem	a3, a3, t0
	addi	a3, a3, '0'
	call	v_putc		# v_putc( 79, 1, '0'+(count%10)); /* display paddle hit count */
	
	lw	t0, count(gp)	# if( count >= 5 && delay == DELAY ) delay = DELAY/3;
	li	t1, 5
	blt	t0, t1, SKIP8
	lw	t0, delay(gp)
	li	t1, DELAY
	bne	t0, t1, SKIP8
	li	t0, 3
	div	t1, t1, t0
	sw	t1, delay(gp)
SKIP8:	# 
	# paddle miss hit
	lw	t0, nx(gp)	# if( nx == 0 ) 
	li	t1, 0
	bne	t0, t1, SKIP9
		
	lw	t0, ball(gp)	# ball--
	addi	t0, t0, -1
	sw	t0, ball(gp)

	li	a1, 64
	li	a2, 1
	lw	a3, ball(gp)
	addi	a3, a3, '0'
	call	v_putc		# v_putc( 64, 1, '0'+ball )	# ball count

	# delete ball
	lw	a1, bx(gp)	# v_putc( bx, by, ' ' )
	lw	a2, by(gp)
	li	a3, ' '
	call 	v_putc
	
	

	#li	t0, 2		# nx = 2
	#sw	t0, nx(gp)
	#li	t0, 4		# ny = 4
	#sw	t0, ny(gp)
	#li	t0, 1	
	#sw	t0, vx(gp)	# vx = 1
	#sw	t0, vy(gp)	# vy = 1

	lw	t0, ball(gp)	# if( ball == 0 ) break8
	beq	t0, zero, BREAK8

SKIP9:	# paddle move
	call 	getsw
	srli	a0, a0, 16
	li	t0, 2
	bne	a0, t0, SKIP10		# if( sw == 0x20000 ) npy = py - 1; else/* up   SW */
	lw	t0, py(gp)
	addi	t0, t0, -1
	sw	t0, npy(gp)
	j	SKIP11
SKIP10:	li	t0, 4
	bne	a0, t0, SKIP12		# if( sw == 0x40000 ) npy = py + 1; else/* down SW  */
	lw	t0, py(gp)
	addi	t0, t0,  1
	sw	t0, npy(gp)
	j	SKIP11
SKIP12:	lw	t0, py(gp)
	sw	t0, npy(gp)

SKIP11:	li	t1, 2
	bne	t0, t1, SKIP13		# if( npy == 2  ) npy =  3;     else/* top wall */
	li	t2, 3
	sw	t2, npy(gp)
SKIP13:	lw	t1, pl(gp)
	li	t2, HEIGHT
	sub	t1, t2, t1
	bne	t0, t1, SKIP14		# if( npy == HEIGHT-pl ) npy = HEIGHT-1-pl;      /* bottom wall */
	addi	t1, t1, -1
	sw	t1, npy(gp)
SKIP14:	
	li	s1, 0
LOOP15:	lw	s2, pl(gp)
	bge	s1, s2, SKIP15		# for( i=0 ; i < pl ; i++ )
	/* delete paddle */
	li	a1, 10
	lw	a2, py(gp)
	add	a2, a2, s1
	li	a3, ' '
	call	v_putc			#   v_putc( 10, py+i, ' ' );
	addi	s1, s1, 1
	j	LOOP15			# 
SKIP15:	
	lw	t0, npy(gp)
	sw	t0, py(gp)	# py = npy


	lw	a1, bx(gp)
	lw	a2, by(gp)
	li	a3, ' '
	call	v_putc		# v_putc( bx, by, ' ' ) delete ball

	lw	t0, nx(gp)
	sw	t0, bx(gp)	# bx = nx

	j	LOOP		# 

BREAK8:	# Game over
	# delete ball
	lw	a1, bx(gp)
	lw	a2, by(gp)
	li	a3, ' '
	call	v_putc		# v_putc( bx, by, ' ' )

	li	a1, 28
	li	a2, 20
	la	a3, str_game_over  # ゲームオーバーメッセージ
	call	v_puts

LOOP_GAME_OVER:	# 再スタートのための入力待ち
	call	getsw
	srli	a0, a0, 20
	li	t0, 1
	beq	a0, t0, BREAK_GAME_OVER  # 中央ボタンが押されたら再スタート
	j	LOOP_GAME_OVER

BREAK_GAME_OVER:
	# ゲームの初期化処理をここに追加
	li	t0, 3		# ボールの数を初期化
	sw	t0, ball(gp)	# ボールの数を保存
	li	t0, 4		# ボールの初期 x 座標
	sw	t0, bx(gp)	# ボールの x 座標を保存
	li	t0, 8		# ボールの初期 y 座標
	sw	t0, by(gp)	# ボールの y 座標を保存
	li	t0, 1		# ボールの速度を初期化
	sw	t0, vx(gp)
	sw	t0, vy(gp)
	li	t0, 10		# パドルの初期位置
	sw	t0, py(gp)
	li	t0, 3		# パドルの長さ
	sw	t0, pl(gp)
	li	t0, 0		# ヒットカウントを初期化
	sw	t0, count(gp)
	li	t0, DELAY	# 遅延を初期化
	sw	t0, delay(gp)

	j	LOOP0		# ゲームループに戻る
	
	lw	ra, 0(sp)
	addi	sp, sp, 4
	ret

	#
	# v_puts( a1, a2, a3 ) (x,y,*str)
	#
v_puts:	addi	sp, sp, -16
	sw	ra, 0(sp)
	sw	a1, 4(sp)
	sw	a3, 8(sp)
v_puts1:sw	a3,12(sp)
	lb	a3, 0(a3)	# while( *str != '\0' ) 
	beq	a3, zero, v_puts2
	call	v_putc		# v_putc( x++, y, *str++ )
	add	a1, a1, 1
	lw	a3,12(sp)
	add	a3, a3, 1
	j	v_puts1
v_puts2:lw	a3, 8(sp)
	lw	a1, 4(sp)
	lw	ra, 0(sp)
	addi	sp, sp, 16
	ret
	
	#
	# v_putc(x,y,ch) // x: a1, y: a2, ch: a3
	#
v_putc:	li	t0, WIDTH	# t0 = XSIZE
	mul	t0, a2, t0	# t0 = y * XSIZE
	add	t0, t0, a1	# t0 = y * XSIZE + y
	la	t1, vrambase
	add	t1, t1, t0	# t1 = VRAMbase + y * XSIZE + x
	sb	a3, 0( t1 )	# *( DATA + y * XSIZE + X ) = ch
	ret

	#
	# a0 = getsw() // return switch status on a0 reg
	#
getsw:	la	t0, ledbase
	lw	a0, 12(t0)
	ret

	## 
	## wait(a1)
	## 
wait:	move	t0, a1
wait2:	li	t1, 5           # 1024
wait1:	addi	t1, t1, -1
	la	t2, ledbase	# check code
	sw	t0, 4( t2 )
	bne	t1, zero, wait1
	addi	t0, t0, -1
	bne	t0, zero, wait2
	ret
	
	.data
	.align	2
data:	.space	data_size

str_1:	.string	"RISC-V Processor Video System                  "
str_2:	.string	"Squash Game"
str_3:	.string	"Balls:"
str_4:	.string	"Hit count:"
str_5:	.string "Push center button to start!"
str_6:	.string "                            "
str_game_over:	.string "Game Over! Press center button to restart."


random_seed: .word 123456  # 初期シード値
next_next_x: .word 0
next_next_next_x: .word 0

# ランダムなボールの位置を生成する関数
random_position:
	# LCGのパラメータ
	li t0, 1664525  # a
	li t1, 1013904223  # c
	li t2, 4294967296  # m (2^32)
	
	# 乱数の初期値を設定
	lw t3, random_seed  # 前の乱数を読み込む
	mul t4, t3, t0      # X_n * a
	add t4, t4, t1      # (X_n * a + c)
	rem t3, t4, t2      # (X_n * a + c) mod m
	sw t3, random_seed   # 新しい乱数を保存

	# 乱数をx座標とy座標に変換
	rem a0, t3, WIDTH   # 0からWIDTH-1の範囲
	rem a1, t3, HEIGHT  # 0からHEIGHT-1の範囲

	ret
