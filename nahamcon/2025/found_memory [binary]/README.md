This challenge features a binary with full modern protections:
```
'/home/md7/LAB/naham/found_memory_patched'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    RUNPATH:    b'.'
    FORTIFY:    Enabled
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```
Despite this, we exploit a Use-After-Free (UAF) vulnerability to leak heap and libc addresses, and ultimately gain code execution.
```
menu:

1) Alloc
2) Free
3) View
4) Edit
5) Exit
```

We have UAF read and write. Even though PIE is enabled and we have full RELRO (which didn’t exist in the last challenge), we can still break everything and exploit this binary.

The libc version here is 2.31, which doesn’t have safe-linking, so we can easily leak heap addresses. But that's not enough — we need a libc leak. How?

By triggering malloc_consolidate()!


Why do we care? Well, UAFs and the like are very nice to have, but a Read-After-Free on a fastbin chunk can only ever leak you a heap address, as the singly-linked lists only use the fd pointer which points to another chunk (on the heap) or is NULL. We want to get a libc leak as well!

If we free enough adjacent fastbin chunks at once and trigger a call to malloc_consolidate(), they will consolidate to create a chunk that goes to the unsorted bin. The unsorted bin is doubly-linked, and acts accordingly - if it is the only element in the list, both fd and bk will point to a location in malloc_state,  which is contained within libc.


everything is ready for cooking!

--------

In the exploit code, 2 chunks are allocated and freed. Since we have UAF-read, we can leak the heap address.

That’s the first step. Now we need to leak a libc address. According to the explanation above, we have to overwrite a chunk header’s size so that when the chunk is freed, malloc_consolidate() will be triggered.

With a simple fd-poison, we can control a chunk’s header. After setting the size to 0x441 (we need to make sure there's a chunk at this offset, so we allocate 17 more chunks), we free the chunk. The address of the unsorted bin in libc will be written there.

Now we have everything — but what should we overwrite, since the GOT is not writable? We can overwrite __free_hook in libc.

Some calculations to get the address of system(), then overwrite __free_hook using fd-poison again.

Finally, a free() call executes our command.


refs:
https://ir0nstone.gitbook.io/notes/binexp/heap/malloc_consolidate