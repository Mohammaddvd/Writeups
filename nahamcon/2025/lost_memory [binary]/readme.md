## Strategy
- libc.so.6 the libc version 2.32 (no safe_linking)
- ld-linux-x86-64.so.2  (linker)
- lost_memory (main bin)

```
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

Since safe_linking is not present, we can leverage the fd-poison technique to manipulate the tcache’s linked list.
Additionally, because PIE is disabled, we have predictable addresses, allowing us to corrupt the global ptr list for arbitrary read and write.

Using this arbitrary read primitive, we can leak the address of the actual printf function. With some calculations, we determine the address of system. Finally, we overwrite the free@got entry with the address of system, and trigger execution.