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
OBJS	= startup.o fact.o

all: fact.mif fact.verilog fact.lst

fact.mif: fact.verilog
	./../vlogdump2mif.py fact.verilog -s

fact.verilog: fact.elf
	$(OBJCOPY) -O verilog  $< $@

fact.lst: fact.elf
	$(OBJDUMP) -D $< > $@

fact.elf: $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

clean:
	$(RM) -rf *.verilog *.mif *.elf *.o *.lst *~
