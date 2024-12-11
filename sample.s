	#
	# Simple Ball Avoidance Game
	#

	.text
	.global	main
	.align	2


main:	addi	sp, sp, -4
	sw	ra, 0(sp)	# push return address

	li	t0, 10		# player position (初期位置)
	li	t1, 0		# obstacle position (初期位置)
	li	t2, 0		# score

LOOP:	
	# 画面をクリア
	li	a1, 0
	li	a2, 0
	li	a3, ' '
	call	v_putc		# 画面をクリア

	# プレイヤーを表示
	li	a1, 10		# x position
	move	a2, t0		# y position
	li	a3, 'O'		# プレイヤーのシンボル
	call	v_putc		# プレイヤーを表示

	# 障害物を表示
	li	a1, 10		# x position
	move	a2, t1		# y position
	li	a3, 'X'		# 障害物のシンボル
	call	v_putc		# 障害物を表示

	# スコアを表示
	li	a1, 0		# x position
	li	a2, 0		# y position
	addi	t2, t2, 1	# スコアを増やす
	addi	t3, t2, '0'	# スコアをASCIIに変換
	call	v_putc		# スコアを表示

	# ボタンのチェック
	call	getsw
	srli	a0, a0, 16	# 上ボタン
	li	t4, 2
	bne	a0, t4, CHECK_DOWN

	# プレイヤーを上に移動
	addi	t0, t0, -1
	j CHECK_OBSTACLE

CHECK_DOWN:
	li	t4, 4
	bne	a0, t4, CHECK_OBSTACLE

	# プレイヤーを下に移動
	addi	t0, t0, 1

CHECK_OBSTACLE:
	# 障害物を下に移動
	addi	t1, t1, 1

	# 障害物が画面の下に到達したらリセット
	li	t5, 20		# 画面の高さ
	bge	t1, t5, RESET_OBSTACLE

	j LOOP

RESET_OBSTACLE:
	li	t1, 0		# 障害物の位置をリセット
	j LOOP

	# スタックを復元して戻る
	lw	ra, 0(sp)
	addi	sp, sp, 4
	ret

	#
	# v_putc(x,y,ch) // x: a1, y: a2, ch: a3
	#
v_putc:	li	t0, 80	# t0 = XSIZE
	mul	t0, a2, t0	# t0 = y * XSIZE
	add	t0, t0, a1	# t0 = y * XSIZE + x
	la	t1, vrambase
	add	t1, t1, t0	# t1 = VRAMbase + y * XSIZE + x
	sb	a3, 0( t1 )	# *( DATA + y * XSIZE + x ) = ch
	ret

	#
	# a0 = getsw() // return switch status on a0 reg
	#
getsw:	la	t0, ledbase
	lw	a0, 12(t0)
	ret