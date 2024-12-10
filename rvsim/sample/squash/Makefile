CROSS_COMPILE=/staff/kuga/Share/riscv/bin/riscv32-unknown-elf-
#CROSS_COMPILE=/opt/riscv/bin/riscv32-unknown-elf-
CC     = $(CROSS_COMPILE)gcc
AS     = $(CROSS_COMPILE)as
LD     = $(CROSS_COMPILE)ld
OBJCOPY= $(CROSS_COMPILE)objcopy
OBJDUMP= $(CROSS_COMPILE)objdump

CFLAGS  = -g -march=rv32im -ffreestanding 
ASFLAGS = -g --gstabs+ -march=rv32im
LDFLAGS = -nostartfiles --no-relax -Bstatic -T ../link.ld -nostdlib

OBJS = startup.o squash.o

all: squash.mif squash.verilog squash.lst

squash.mif: squash.verilog
	./../vlogdump2mif.py squash.verilog -s

squash.verilog: squash.elf
	$(OBJCOPY) -O verilog  $< $@

squash.lst: squash.elf
	$(OBJDUMP) -D $< > $@

squash.elf: $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

clean:
	rm -rf *.verilog *.mif *.elf *.o *.lst *~
