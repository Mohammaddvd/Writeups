# fastbin-duplicate-into-stack
This marks my third week of learning about heap exploitation, and today’s trick is
truly fascinating. Unlike last time, I created my own challenge and will  walk you
through the solution.

Today's  trick  is  called  Fastbin  Duplicate Into Stack, which involves tricking
calloc into returning a nearly  arbitrary  pointer  by  manipulating  the  fastbin
freelist.

I used the how2heap repository as a reference to demonstrate the trick (see sample.c).

## Step-by-Step Explanation
### Filling the Tcache
To begin, we need to fill the tcache. As you might know, tcache can store a maximum of 7 chunks. In lines 13–18, we allocate and free chunks to fill the tcache.

### Target Buffer Setup
In line 21, we define stack_var as our target buffer. Our goal is to have our final calloc() call return a pointer to this variable on the stack rather than a chunk on the heap.

### Heap Chunk Allocation
Lines 23–25 allocate three new chunks in the heap.

### Triggering Double-Free
Lines 27–31 show how we trigger a double-free by freeing the same chunk twice (the chunk referred to by a).

### Popping Chunks from the Fastbin
In line 33, we call calloc() to pop the previously freed a chunk from the fastbin. Similarly, in line 35, we do the same with chunk b.

### Preparing the Target Buffer
We now need to prepare our target buffer to resemble a valid heap chunk by setting its size correctly without setting the prev_in_use bit.

### Calculating the Correct FD Pointer
In line 44, we set the fd pointer. This step is crucial and requires knowing the target buffer's stack address. We need to pass a safe-linking check using the following formula: (ref https://research.checkpoint.com/2020/safe-linking-eliminating-a-20-year-old-malloc-exploit-primitive/)
```
*d = (addr >> 12) ^ ptr;
```
### Corrupting the Fastbin
In line 48, we pop the last a chunk from the bin. At this point, the fastbin is corrupted. Then, in line 50, when we call calloc(), it returns a pointer to the stack.

---
## challange time
Now it’s your turn. You have the source code (chall.c) and a compiled binary (chall). Try solving it yourself without reading further.

The application communicates via a TCP connection and provides a simple menu:

```
1 - signup  [allocate a chunk]
2 - give up [free a chunk]
3 - submit flag [writing some data into the stack]
4 - leak    [leak addresses]
```

All the necessary elements for crafting the exploit are in place. Check out `exploit.py` for hints.

### Exploit Breakdown

- Lines 69–73: Fill the tcache.

- Lines 77–82: Perform the double-free.

- Lines 85–94: Leak stack and heap addresses.

- Final step: Send the crafted payload.

If everything goes well, you’ll get a shell. Good luck!