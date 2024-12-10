class rvsim :

  tracef = 1		# 0: no trace, 1: All trace, 2: only peripheral store

  PC   = 0		# Program Counter
  SW   = 0		# Input Slide SW and Push SW
  NPC  = 0		# Next PC
  REG  = [0 for i in range(32)]	# Register
  IMEM = [0 for i in range(32768)]		# Instruction Memory Base
  DMEM = [0 for i in range(32768)]		# Data Memory Base
  VRAM = [0x20202020 for i in range(1024)]	# Video Memory Base
  PERF = [0 for i in range(4)]                  # Periheral Base

  # opecode
  OP_LOAD   = 0x03 # 7'b000_0011
  OP_STORE  = 0x23 # 7'b010_0011
  OP_FENCEX = 0x0f # 7'b000_1111
  OP_AUIPC  = 0x17 # 7'b001_0111
  OP_LUI    = 0x37 # 7'b011_0111
  OP_BR     = 0x63 # 7'b110_0011
  OP_JALR   = 0x67 # 7'b110_0111
  OP_JAL    = 0x6f # 7'b110_1111
  OP_FUNC1  = 0x13 # 7'b001_0011
  OP_FUNC2  = 0x33 # 7'b011_0011
  OP_FUNC3  = 0x73 # 7'b111_0011
    
  # Instruction Format Type ( 0: illegal instruction )
  FT_R	= 1
  FT_I	= 2
  FT_S	= 3
  FT_U	= 4
  FT_J	= 5
  FT_B	= 6
    
  #
  # Resource
  #
  VRAM_BASE = 0x7ff00000
  SW_ADDR   = 0x7ff1000c	# Slide SW and Push SW
  
  regn = [ "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2", \
           "s0",   "s1", "a0", "a1", "a2", "a3", "a4", "a5", \
           "a6",   "a7", "s2", "s3", "s4", "s5", "s6", "s7", \
           "s8",   "s9", "s10","s11","t3", "t4", "t5", "t6"
  ]
  
  def get_word( self, line ):
    hex_str = line[6:8]+line[4:6]+line[2:4]+line[0:2]
    data = int(hex_str,16)
#   if data & 0x80000000:
#     data = data - 0x80000000
    return data

  def load_file( self, file, core ):
    with open(file, "r") as fp:
      data = fp.readlines()
      if data:
        for i, line in enumerate(data):
          word = self.get_word(line)
          core[i] = word
      else:
        i = 0                   # rerurn 0 if no word, 
    return i                    # return number of word
  
  def init_imem( self, file):
    status = self.load_file( file, self.IMEM )
    return status
  
  def init_dmem( self, file ):
    status = self.load_file( file, self.DMEM )
    return status

  def reset( self ):
    # Program Counter
    self.PC = 0
    
    # Clear Register
    for i in range(32):
      self.REG[i] = 0
    
    for i in range(1024):
      self.VRAM[i] = 0x20202020 # Fill Space Char.

    return 0

  
  def dmemr( self, mode, daddr ):
    mspace = ( daddr & 0xfff00000 ) >> 20
    addr = daddr & 0x000fffff
    
    if mspace == 0x000 : # Text segment
      memptr = self.IMEM
    elif mspace == 0x001 : # Data segment
      memptr = self.DMEM
    elif mspace == 0x7ff : # VRAM segment
      if( addr >= 0 and addr <= 0xffff ):
        memptr = self.VRAM
      elif( addr >= 0x10000 and addr <= 0x1000f ):
        addr &= 0xf
        memptr = self.PERF
      else:
        memptr = self.DMEM
    else:
      memptr = self.DMEM
    
    mem_val = memptr[addr>>2]
    if( daddr == self.SW_ADDR ):
      mem_val = self.SW
    
    if mode == 0 :# lb
      if  addr & 0x3 == 0:
        byte = mem_val      & 0xff
      elif  addr & 0x3 == 1:
        byte = (mem_val>> 8) & 0xff
      elif  addr & 0x3 == 2:
        byte = (mem_val>>16) & 0xff
      elif  addr & 0x3 == 3:
        byte = (mem_val>>24) & 0xff
      return_val = ((byte & 0x7f) - 128) if byte & 0x80 else byte
    elif mode == 1 : # lh
      if  addr & 0x2 == 0:
        short = mem_val      & 0xffff
      elif addr & 0x2 == 2:
        short = (mem_val>>16) & 0xffff
      return_val = ((short & 0x7fff) - 32768) if short & 0x8000 else short
    elif mode == 2 : # lw
      return_val = ((mem_val & 0x7fffffff) - 2147483648) if mem_val & 0x80000000 else mem_val
    elif mode == 4 : # lbu
      if  addr & 0x3 == 0:
        return_val = ( mem_val      & 0xff)
      if  addr & 0x3 == 1:
        return_val = ((mem_val>> 8) & 0xff)
      elif  addr & 0x3 == 2:
        return_val = ((mem_val>>16) & 0xff)
      elif  addr & 0x3 == 3:
        return_val = ((mem_val>>24) & 0xff)
    elif mode == 5 : # lhu
      if  addr & 0x2 == 0:
        return_val = ( mem_val      & 0xffff) 
      elif addr & 0x2 == 2:
        return_val = ((mem_val>>16) & 0xffff) 
    elif mode == 6 : # lwu
      return_val = mem_val
    
    return return_val
  
  def dmemw( self, mode, daddr, ddata ):
    mspace = ( daddr & 0xfff00000 ) >> 20
    addr = daddr & 0x000fffff
    
    if mspace == 0x000: # Text segment
      memptr = self.IMEM
    elif mspace == 0x001: # Data segment
      memptr = self.DMEM
    elif mspace ==  0x7ff: # VRAM segment
      if( addr >= 0 and addr <= 0xffff ):
        memptr = self.VRAM
      elif( addr >= 0x10000 and addr <= 0x1000f ):
        addr &= 0xf
        memptr = self.PERF
    else:
      memptr = self.DMEM

    mem_val = memptr[addr>>2]
    
    if  mode ==  0 : # sb
      if  addr & 0x3 == 0:
        memptr[addr>>2]  = (mem_val & 0xffffff00) |  (ddata & 0xff)      
      elif addr & 0x3 ==  1:
        memptr[addr>>2]  = (mem_val & 0xffff00ff) | ((ddata & 0xff)<< 8) 
      elif addr & 0x3 ==  2:
        memptr[addr>>2]  = (mem_val & 0xff00ffff) | ((ddata & 0xff)<<16) 
      elif addr & 0x3 ==  3:
        memptr[addr>>2]  = (mem_val & 0x00ffffff) | ((ddata & 0xff)<<24) 
    elif mode ==  1 : # sh
      if   addr & 0x2 ==  0: memptr[addr>>2]  = (mem_val & 0xffff0000) |  (ddata & 0xffff)     
      elif addr & 0x2 ==  2: memptr[addr>>2]  = (mem_val & 0x0000ffff) | ((ddata & 0xffff)<<16)
    elif mode ==  2 : # sw
      memptr[addr>>2] = ddata

      
  def imm( self, fmt, inst ):
    snum = ((inst & 0x7fffffff) - 2147483648) if inst & 0x80000000 else inst
    if  fmt ==  self.FT_S :
      #imm_val = ((int)(inst & 0x80000000)>>19) | ( IR_F7 << 5 ) | IR_RD 
      #imm_val = ((snum & 0xfe000000)>>20) | self.IR_RD(inst) 
      imm_val = ((snum >> 20) & 0xffffffe0) | self.IR_RD(inst) 
      imm_val = ((imm_val & 0x7fffffff) - 2147483648) if imm_val & 0x80000000 else imm_val
    elif fmt == self.FT_U :
      imm_val = inst & 0xfffff000
    elif fmt == self.FT_J :
      snum = (snum >> 11) & 0xfff00000 \
	   | (inst & 0x000ff000)       \
	   | (inst & 0x00100000) >>  9 \
           | (inst & 0x7fe00000) >> 20
      imm_val = ((snum & 0x7fffffff) - 2147483648) if snum & 0x80000000 else snum
    elif fmt == self.FT_B :
      snum = (snum >> 19) & 0xfffff000 \
	   | (inst & 0x00000080) <<  4 \
           | (inst & 0x7e000000) >> 20 \
 	   | (inst & 0x00000f00) >>  7
      imm_val = ((snum & 0x7fffffff) - 2147483648) if snum & 0x80000000 else snum
    else: # FT_I
      imm_val = snum >> 20
#    print( "{:08x} {:08x} {:08x}".format(snum, imm_val, inst))
    return imm_val


  
  def step( self ):
    return_str = ''
      
    inst = self.IMEM[self.PC>>2]
    self.NPC = self.PC + 4
    
    if  self.IR_OP(inst) ==  self.OP_LUI :
      self.REG[self.IR_RD(inst)] = self.imm( self.FT_U, inst )
      if( self.tracef == 1 ):
        return_str = "{:08x} {:08x} lui\t{:s}, {:d}".format(self.PC, inst, self.regn[self.IR_RD(inst)], self.imm(self.FT_U, inst))
      
    elif self.IR_OP(inst) ==  self.OP_AUIPC : 
      self.REG[self.IR_RD(inst)] = self.PC + self.imm( self.FT_U, inst )
      if( self.tracef == 1 ):
        return_str =  "{:08x} {:08x} auipc\t{:s}, 0x{:08x}\t{:08x}".format(self.PC, inst, self.regn[self.IR_RD(inst)], self.imm(self.FT_U, inst), self.REGR(self.IR_RD(inst)) )
      
    elif self.IR_OP(inst) ==  self.OP_JAL   :
      self.NPC = self.PC + self.imm( self.FT_J, inst )
      self.REG[self.IR_RD(inst)] = self.PC + 4
      if( self.tracef == 1 ):
        return_str =  "{:08x} {:08x} jal\t{:s}, 0x{:x}".format(self.PC, inst, self.regn[self.IR_RD(inst)], self.imm(self.FT_J, inst)&0xffffffff)
      
    elif self.IR_OP(inst) ==  self.OP_JALR  : 
      self.NPC = self.REGR(self.IR_RS1(inst)) + self.imm( self.FT_I, inst )
      self.REG[self.IR_RD(inst)] = self.PC + 4
      if( self.tracef == 1 ):
        return_str =  "{:08x} {:08x} jalr\t{:s}, {:d}({:s})\t{:08x} {:08x} {:08x}".format( \
		 self.PC, inst, self.regn[self.IR_RD(inst)], self.imm(self.FT_I, inst), self.regn[self.IR_RS1(inst)], \
		 self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.NPC )
      
    elif self.IR_OP(inst) ==  self.OP_BR: 
      inst_str = ""
      if  self.IR_F3(inst) ==  0 :  # beq
        inst_str = "beq"
        if( self.REGR(self.IR_RS1(inst)) == self.REGR(self.IR_RS2(inst)) ):
          self.NPC = (int)(self.PC) + (int)(self.imm( self.FT_B, inst ))
      elif self.IR_F3(inst) ==  1 : # bne
        inst_str = "bne"
        if( self.REGR(self.IR_RS1(inst)) != self.REGR(self.IR_RS2(inst)) ):
          self.NPC = (int)(self.PC) + (int)(self.imm( self.FT_B, inst ))
      elif self.IR_F3(inst) ==  4 :   # blt
        inst_str = "blt"
        if( (int)(self.REGR(self.IR_RS1(inst))) < (int)(self.REGR(self.IR_RS2(inst))) ):
          self.NPC = self.PC + self.imm( self.FT_B, inst )
      elif self.IR_F3(inst) ==  5 :   # bge
        inst_str = "bge"
        if( (int)(self.REGR(self.IR_RS1(inst))) >= (int)(self.REGR(self.IR_RS2(inst))) ):
          self.NPC = self.PC + self.imm( self.FT_B, inst )
      elif self.IR_F3(inst) ==  6 :  # bltu
        inst_str = "bltu"
        if( self.REGR(self.IR_RS1(inst)) < self.REGR(self.IR_RS2(inst)) ):
          self.NPC = self.PC + self.imm( self.FT_B, inst )
      elif self.IR_F3(inst) ==  7 : # bgeu
        inst_str = "bgeu"
        if( self.REGR(self.IR_RS1(inst)) >= self.REGR(self.IR_RS2(inst)) ):
          self.NPC = self.PC + self.imm( self.FT_B, inst )
      else:
        return_str =  "** Undefined instruction {:08x} in OP_BR".format( inst )
        self.PC = self.NPC
        return return_str
      if self.tracef == 1:
        return_str =  "{:08x} {:08x} {:s}\t{:s}, {:s}, {:d}\t{:08x} {:08x}".format( \
                   self.PC, inst, inst_str, self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)], self.imm(self.FT_B, inst), \
		   self.REGR(self.IR_RS1(inst))&0xffffffff, self.REGR(self.IR_RS2(inst))&0xffffffff )
    
    elif self.IR_OP(inst) ==  self.OP_LOAD  :
      daddr = self.REGR(self.IR_RS1(inst)) + self.imm( self.FT_I, inst )
      self.REG[self.IR_RD(inst)] = self.dmemr( self.IR_F3(inst), daddr )
      if self.tracef == 1 :
        if   self.IR_F3(inst) ==  0 : # lb
          inst_str =  "lb"
        elif self.IR_F3(inst) ==  1 : # lh
          inst_str =  "lh"
        elif self.IR_F3(inst) ==  2 : # lw
          inst_str =  "lw"
        elif self.IR_F3(inst) ==  4 : # lbu
          inst_str =  "lbu"
        elif self.IR_F3(inst) ==  5 : # lhu
          inst_str =  "lhu"
        elif self.IR_F3(inst) ==  6 : # lwu
          inst_str =  "lwu"
        else:
          return_str = "** Undefined instruction {:08x} in OP_LOAD".format( inst )
          self.PC = self.NPC
          return return_str
        return_str = "{:08x} {:08x} {:s}\t{:s}, {:d}({:s})\t{:08x} {:08x} {:08x}".format( \
                   self.PC, inst, inst_str, self.regn[self.IR_RD(inst)], self.imm(self.FT_I, inst), self.regn[self.IR_RS1(inst)], \
                   self.REGR(self.IR_RS1(inst))&0xffffffff, self.REGR(self.IR_RD(inst))&0xffffffff, daddr&0xffffffff )
        
        
    elif self.IR_OP(inst) ==  self.OP_STORE :
      daddr = self.REGR(self.IR_RS1(inst)) + self.imm( self.FT_S, inst )
      self.dmemw( self.IR_F3(inst), daddr, self.REGR(self.IR_RS2(inst)) )
      if  self.IR_F3(inst) ==  0 : # sb
        if( self.tracef == 1 or self.tracef == 2 and daddr >= self.VRAM_BASE ):
          return_str =  "{:08x} {:08x} sb\t{:s}, {:d}({:s})\t{:08x} {:08x} {:08x}".format( \
		   self.PC, inst, self.regn[self.IR_RS2(inst)], self.imm(self.FT_S, inst), self.regn[self.IR_RS1(inst)], self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))&0xffffffff, daddr&0xffffffff )
      elif self.IR_F3(inst) ==  1 : # sh
        if( self.tracef == 1 or self.tracef == 2 and daddr >= self.VRAM_BASE ):
          return_str =  "{:08x} {:08x} sh\t{:s}, {:d}({:s})\t{:08x} {:08x} {:08x}".format(\
		   self.PC, inst, self.regn[self.IR_RS2(inst)], self.imm(self.FT_S, inst), self.regn[self.IR_RS1(inst)], self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))&0xffffffff, daddr&0xffffffff )
      elif self.IR_F3(inst) ==  2 : # sw
        if( self.tracef == 1 or self.tracef == 2 and daddr >= self.VRAM_BASE ):
          return_str =  "{:08x} {:08x} sw\t{:s}, {:d}({:s})\t{:08x} {:08x} {:08x}".format( \
		   self.PC, inst, self.regn[self.IR_RS2(inst)], self.imm(self.FT_S, inst), self.regn[self.IR_RS1(inst)], self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))&0xffffffff, daddr&0xffffffff )
      else:
        return_str =  "** Undefined instruction {:08x} in OP_STORE".format( inst )
      
    elif self.IR_OP(inst) ==  self.OP_FUNC1 : # Self.Immediate
      if  self.IR_F3(inst) ==  0 : # addi
        self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst))) + self.imm( self.FT_I, inst )
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} addi\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format( \
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst),
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)&0xffffffff )
      elif self.IR_F3(inst) ==  1 :       # slli
        if self.IR_F7(inst) ==0 :
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) << ( self.imm( self.FT_I, inst ) & 0x1f )
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} slli\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format( \
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst), \
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
      elif self.IR_F3(inst) ==  2 :  # slti
        self.REG[self.IR_RD(inst)] = 1 if ( (int)(self.REGR(self.IR_RS1(inst))) < self.imm( self.FT_I, inst ) ) else 0
        if( self.tracef == 1) :
          return_str =  "{:08x} {:08x} slti\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format( \
	       self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst), \
		 self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
      elif self.IR_F3(inst) ==  3 :  # sltiu
        self.REG[self.IR_RD(inst)] = 1 if ( self.REGR(self.IR_RS1(inst)) < self.imm( self.FT_I, inst ) ) else 0
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} sltii\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst),
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
      elif self.IR_F3(inst) ==  4 :  # xori
        self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) ^ self.imm( self.FT_I, inst )
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} xori\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst),
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
      elif self.IR_F3(inst) ==  5 : 
        if self.IR_F7(inst) == 0 : # srli
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) >> ( self.imm( self.FT_I, inst ) & 0x1f )
          if self.tracef == 1 :
            return_str =  "{:08x} {:08x} srli\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst),
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
        elif self.IR_F7(inst) == 0x20 :	# srai
          self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst)) ) >> ( self.imm( self.FT_I, inst ) & 0x1f )
          if self.tracef == 1 :
            return_str =  "{:08x} {:08x} srai\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst),
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
      elif self.IR_F3(inst) ==  6 : # ori
        self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) | self.imm( self.FT_I, inst )
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} ori\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst),
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
      elif self.IR_F3(inst) ==  7 : # andi
        self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) & self.imm( self.FT_I, inst )
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} andi\t{:s}, {:s}, {:d}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.imm(self.FT_I, inst),
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.imm(self.FT_I,inst)  )
      
    elif self.IR_OP(inst) ==  self.OP_FUNC2 : # R type
      if  self.IR_F3(inst) ==  0 : 
        if self.IR_F7(inst) == 0 : # add
          self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst))) + (int)(self.REGR(self.IR_RS2(inst)))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} add\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 0x20 : # sub
          self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst))) - (int)(self.REGR(self.IR_RS2(inst)))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} sub\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 1 : # mul
          self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst))) * (int)(self.REGR(self.IR_RS2(inst)))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} mul\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst)==  1 : 
        if self.IR_F7(inst) == 0 :  # sll
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) << ( self.REGR(self.IR_RS2(inst)) & 0x1f )
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} sll\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 1 :     # mulh
          self.REG[self.IR_RD(inst)] = ( ( (long)(self.REGR(self.IR_RS1(inst))) * (long)(self.REGR(self.IR_RS2(inst))) ) & 0xffffffff00000000 ) >> 32
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} mulh\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  2 : 
        if self.IR_F7(inst) == 0 :  # slt
          self.REG[self.IR_RD(inst)] = 1 if (int)(self.REGR(self.IR_RS1(inst))) < (int)(self.REGR(self.IR_RS2(inst))) else 0
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} and\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 1 :   # mulhsu
          self.REG[self.IR_RD(inst)] = ( ( (long)(self.REGR(self.IR_RS1(inst))) * (ulong)(self.REGR(self.IR_RS2(inst))) ) & 0xffffffff00000000 ) >> 32
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} mulhsu\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst)==  3 :
        if self.IR_F7(inst) == 0 : # sltu
            self.REG[self.IR_RD(inst)] = 1 if self.REGR(self.IR_RS1(inst)) < self.REGR(self.IR_RS2(inst)) else 0
            if( self.tracef == 1 ):
              return_str =  "{:08x} {:08x} sltu\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 1 :    # mulhu
          self.REG[self.IR_RD(inst)] = ( ( (ulong)(self.REGR(self.IR_RS1(inst))) * (ulong)(self.REGR(self.IR_RS2(inst))) ) & 0xffffffff00000000 ) >> 32
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} mulhu\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  4 :
        if self.IR_F7(inst) == 0 : # xor
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) ^ self.REGR(self.IR_RS2(inst))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} xor\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 1 : # div
          self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst))) / (int)(self.REGR(self.IR_RS2(inst)))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} div\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst)==  5 :
        if self.IR_F7(inst) == 0 : # srl
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) >> ( self.REGR(self.IR_RS2(inst)) &  0x1f )
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} srl\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 0x20 : # sra
          self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst))) >> ( self.REGR(self.IR_RS2(inst)) &  0x1f )
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} sra\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  6 :
        if self.IR_F7(inst) == 0 : # or
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) | self.REGR(self.IR_RS2(inst))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} or\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 1 : # rem
          self.REG[self.IR_RD(inst)] = (int)(self.REGR(self.IR_RS1(inst))) % (int)(self.REGR(self.IR_RS2(inst)))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} rem\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) == 7 : 
        if self.IR_F7(inst) == 0 : # and
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) & self.REGR(self.IR_RS2(inst))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} and\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F7(inst) == 1 :      # remu
          self.REG[self.IR_RD(inst)] = self.REGR(self.IR_RS1(inst)) % self.REGR(self.IR_RS2(inst))
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} remu\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      
    elif self.IR_OP(inst) ==  self.OP_FENCEX : # fence
      if  self.IR_F3(inst) ==  0 : 
        if( self.tracef == 1 ):
          return_str =  "** Unimplement \"fence\" instruction {:08x} in base extension.".format( inst )
      elif self.IR_F3(inst) ==  1 : # fence.i
        if( self.tracef == 1 ):
          return_str =  "** Unimplement \"fence.i\" instruction {:08x} in \"Zifencei\" extension.".format( inst )
      else:
        return_str =  "** Undefined instruction. {:08x} in OP_FENCEX".format( inst )
      
    elif self.IR_OP(inst) ==  self.OP_FUNC3 : # ecall, ebreak, CSRxxx
      if self.IR_F3(inst) ==  0 : 
        if self.IR_F12(inst) == 0 : # ecall
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} ecall\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		     self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		     self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
        elif self.IR_F12(inst) == 1 : # ebreak
          if( self.tracef == 1 ):
            return_str =  "{:08x} {:08x} ebreak".format(self.PC, inst)
      elif self.IR_F3(inst) ==  1 : #csrrw
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} csrrw\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  2 : # csrrs
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} csrrs\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  3 : # csrrc
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} csrrc\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  5 : # csrrwi
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} csrrwi\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  6 : # scrrsi
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} scrrsi\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      elif self.IR_F3(inst) ==  7 : # csrrci
        if( self.tracef == 1 ):
          return_str =  "{:08x} {:08x} csrrci\t{:s}, {:s}, {:s}\t{:08x} {:08x} {:08x}".format(
		   self.PC, inst, self.regn[self.IR_RD(inst)], self.regn[self.IR_RS1(inst)], self.regn[self.IR_RS2(inst)],
		   self.REGR(self.IR_RD(inst)), self.REGR(self.IR_RS1(inst)), self.REGR(self.IR_RS2(inst))  )
      else:
        return_str =  "** Undefined instruction. {:08x} in OP_FUNC3".format( inst )
        self.PC = self.NPC
        return return_str
    else:
      return_str =  "** Undefined instruction. {:08x}".format( inst )
    
    self.PC = self.NPC
    return return_str
  

  
  def set_trace( self, mode ):
    self.tracef = mode
    return self.tracef
  
  def set_sw( self, data ):
    self.SW = data
    return self.SW
  
  def read_sw( self ):
    return self.SW

  def read_pc( self ):
    return self.PC
    
  def read_reg( self ):
    reg = [0 for i in range(32)]
    for i in range( 32 ):
      reg[i] = self.REG[i] if i != 0 else 0
    return reg
  
  def read_imem( self, addr ):
    return self.IMEM[addr>>2]

  def read_dmem( self, addr ):
    return self.DMEM[addr>>2]
  
  def read_vram( self,  addr ):
    return self.VRAM[addr>>2]

  def read_perf( self, addr ):
    return self.PERF[addr>>2]

  def REGR(self, X):
    return self.REG[X] if X != 0 else 0

  #
  # Opecode field
  #
  def IR_OP(self, inst):
    return (   inst         & 0x7f  ) # IR[ 6: 0]

  def IR_RD(self, inst):
    return ( ( inst >>  7 ) & 0x1f  ) # IR[11: 7]

  def IR_F3(self, inst):
    return ( ( inst >> 12 ) & 0x07  ) # IR[14:12]

  def IR_RS1(self, inst):
    return ( ( inst >> 15 ) & 0x1f  ) # IR[19:15]

  def IR_RS2(self, inst):
    return ( ( inst >> 20 ) & 0x1f  ) # IR[24:20]

  def IR_F7(self, inst):
    return ( ( inst >> 25 ) & 0x7f  ) # IR[31:25]

  def IR_F12(self, inst):
    return ( ( inst >> 20 ) & 0xfff ) # IR[31:20]
