Here we are with another write-up on heap exploitation!
It’s been two weeks since my last write-up, which was about the Use-After-Free (UAF) technique.
This week, we’re diving into the "Unsafe-Unlink" technique.

The main goal of the unsafe unlink technique is to achieve arbitrary memory write. This is done by exploiting how the free() function consolidates free chunks in the heap, particularly through the unlinking process of the doubly-linked list used in memory management.

This time, I didn’t write a vulnerable app or use a real-world binary to demonstrate today’s trick. Instead, I took a simple demonstration script from the awesome repo "how2heap":
https://github.com/shellphish/how2heap/blob/master/glibc_2.35/unsafe_unlink.c

with some tweaks of my own.

Let’s start tracing the program:
Lines 17 & 18:
We create two large chunks big enough to avoid being stored in the tcache or fastbin.
We allocate 0x420 bytes for each chunk.

Lines 20-22:
Next, we create a fake chunk inside chunk0 (our first chunk) and set up some pointers known as fd (forward pointer) and bk (backward pointer).
These are used in the doubly-linked list structure that manages free chunks.

Lines 24-26:
Here, we modify the header of the second chunk (chunk1).
We change the prev_size field to 0x420 and unset the prev_inuse bit.
(If you’re unfamiliar with these terms, I recommend Googling them or asking our friend ChatGPT!)

Line 28:
This is the key moment that divides the program’s state before and after the exploit.
When we free() chunk1, the pointer for chunk0 (which is stored on the stack) gets overwritten to point back to the stack itself.
The reason of overwrite is bcz of the unlink process when we want to free a chunk:

fd = P->fd
bk = P->bk
P->fd = bk
P->bk = fd

for better understanding, check the libc source code, malloc.c file:
_int_free() -> _int_free_merge_chunk() -> unlink_chunk()

Hmm… this means that from this point on, any write operation targeting chunk0 will actually write to the stack.
(Technically, when we access chunk0, the system retrieves the pointer from the stack. Since we’ve tampered with that pointer, we’re effectively writing to the stack instead of the original heap chunk.)

So, in line 30, when we think we’re writing to chunk0, we’re actually overwriting a stack address—specifically 24 bytes before the stored chunk0 pointer.

This results in a segmentation fault!


In a real-world scenario:
Instead of manually editing chunk metadata like we did here, we’d exploit vulnerabilities (like buffer overflows) to corrupt the chunks dynamically.