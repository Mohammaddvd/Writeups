Welcome to the new write-up on heap exploitation.
This is my first technique in the "House" series that I’ve learned, and I think the others are similar to this one.
Here we are with "House of BotCake".

Once again, I’m using the how2heap source to demonstrate how this technique works, along with some notes.

The explanation is simple:
```
This file demonstrates a powerful tcache poisoning attack by tricking malloc into
returning a pointer to an arbitrary location (in this demo, the stack).
This attack only relies on double free.
```

So let’s dive into the code. First, we have a stack buffer, which we’re eventually going to point to (defined on line `20`).

Then we fill the tcache with seven chunks. We use a chunk size of 0x100 (REMEMBER: this size must be large enough to avoid storing chunks in the fastbin!).

In lines `23–26`, we fill the tcache. After that, we define two heap chunks: first `prev`, then chunk `a`. We’ll later free chunk a twice.

On line `29`, we allocate 0x10 bytes (which actually returns 0x20) to prevent consolidation with the top chunk when we free chunk `a`.

Remember the `prev` chunk defined before `a`. In line `35`, we free `a`, then `prev`. At this point, the "malloc_consolidate" function is called, so `prev` and `a` are merged. Now the only chunk in the unsorted bin is the address of `prev`!

In line `39`, we allocate a chunk with size 0x100 (`0x110` with the header) to get the last chunk from the tcache (since tcache follows LIFO). Next, in line `41`, the double free occurs, which places chunk `a` into the tcache. So now `a` is present both in the tcache and in the unsorted bin (since it was merged with prev).

In line `45`, we allocate a chunk to retrieve the prev chunk from the unsorted bin. Since this chunk contains the `a` chunk, we can now edit the data of the former `a`. In line `47`, we edit the header of the former `a` chunk—this technique is similar to what we saw before in the “fastbin-to-stack” write-up, used to bypass the safe unlinking checks.

In line `49`, we allocate the last stored `a` chunk. Now the tcache is corrupted, and the final chunk remaining in the tcache is our stack buffer. This means that in the next malloc (line `52`), libc will return a pointer to the stack buffer.

I copy-pasted this code from the how2heap repo and removed the printf/puts functions. In line `50`, the a_size variable was originally used for printing the size of chunk a, but we’re not using it anymore. However, when we try to remove or comment it out, the program crashes. Why?

Here’s the error:
```
malloc(): unaligned tcache chunk detected
zsh: abort      ./app
```

If you check the libc code, you’ll find this error message in the tcache_get_n function. The error happens when there's a problem with alignment. Let's check it in GDB using the latest version of the code:
```
Tcachebins[idx=11728124035470, size=0xaaaaaaac1900, count=1] ←  Chunk(addr=0xffffffffed20, size=0xaaaaaaac1900, flags=PREV_INUSE | IS_MMAPPED | NON_MAIN_ARENA)  ←  [Corrupted chunk at 0xffffffffed20]
```

The address field is: 0xffffffffed20

Now let’s check the updated version:

```
Tcachebins[idx=11728124035470, size=0xaaaaaaac1900, count=1] ←  Chunk(addr=0xffffffffed28, size=0xaaaaaaac1900, flags=PREV_INUSE | IS_MMAPPED | NON_MAIN_ARENA)  ←  [Corrupted chunk at 0xffffffffed28]
```

Now the address is: 0xffffffffed28

This 8 is our problem. It’s a rule (or maybe a security mechanism) that heap chunks must start at a properly aligned boundary.

So in line `50`, when we create a new stack variable, we ensure proper alignment to safely unlink to our stack buffer.
The value of that variable doesn’t matter—only the alignment does.

