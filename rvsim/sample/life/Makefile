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
OBJS	= startup.o life.o

all: life.mif life.verilog life.lst

life.mif: life.verilog
	./../vlogdump2mif.py life.verilog -s

life.verilog: life.elf
	$(OBJCOPY) -O verilog  $< $@

life.lst: life.elf
	$(OBJDUMP) -D $< > $@

life.elf: $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

clean:
	$(RM) -rf *.verilog *.mif *.elf *.o *.lst
