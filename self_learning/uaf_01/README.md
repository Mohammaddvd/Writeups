# Heap exploitation
## Use-After-Free
This write-up documents my process of starting a structured routine for
learning and practicing heap challenges. so lets start it by  a  simple
use-after-free vulnerability (i  had wrote  this  program  which it has
the vuln). Our approach is much simpler than you might expect, we  have
a menu which  we  have to choose 4 options:

```
![we have a global struct called `usr` which has  two  string  pointer]
![this struct store in heap]

1- change username       // [using fgets to store data in usr->username]
2- change password       // [using fgets to store data in usr->username]
3- delete user           // [just free the `usr`]
4- leave a message       // [allocate new chunk in heap  with  our data]
```

if you check the binary you would see that after free ing the`usr` chunk
, the binary is not going to set the variable to NULL, it cause  UAF  or
Use-After-Free!

When we can free a chunk and then allocate a new one, while we can access
the previous variable we can do OOB Write, lets write our final RIP  into
the GOT.

Since we dont have NX (also ASLR :) we can load our shellcode into env of
our shell and get the address of it as our RIP, now choose  an  entry  of
GOT, for exampple `printf` which the binary call it during its execution.


`usr` heap-chunk in situations:

|      usr        |                                   |       usr         |
|username|password| => after free and leave a message |GOT@printf|password|



Now at this state when we want to change  username , we are writing it in
the printf stub.


   GOT:
0x804c004: | Real printf |  => after changing username => | shellcode ADDR |


Finally we would call the shellcode!

![photo_2025-01-23_09-25-02](https://github.com/user-attachments/assets/e69ee563-b1c3-4a18-ab42-9b774bf66cce)


