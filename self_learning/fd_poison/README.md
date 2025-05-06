# Heap Exploitation with FD Poisoning (libc 2.32)

Today we're tackling a heap exploitation challenge using the **fd-poisoning** technique. The goal is to **poison the `fd` field**—the pointer to the next chunk in a tcache bin—in order to gain control over the address returned by a future `malloc()` call.

> ⚠️ This is a writeup of the exploitation process, so it's assumed that you're already familiar with the **tcache** structure in glibc.

---

## 🛠️ Exploit Setup (lines 1–58):

The first part of the exploit defines helper functions for interacting with the menu of the vulnerable binary. These include functions to add, delete, view, and edit "kids".
I also skip the reversing the binary part, do it by your self :)

**Program menu:**
```
Virtual Kid Management
=====================================
1. Create a kid   // (malloc with fixed size)
2. View a kid     // (can leak data due to UAF)
3. Free a kid     // (free with UAF opportunity)
4. Change a kid   // (edit an allocated chunk)
5. Exit
6. Options
```

The target binary is compiled with **libc version 2.32**, which brings some things to consider:

- The **tcache** now includes a `count` variable to track the number of chunks in each bin.
- **Safe-linking** is enabled, meaning the `fd` pointer is XOR-ed with a heap address for security.

The challenge could have been harder if **ASLR** were fully effective, but leaking heap chunk addresses allows us to bypass it.

---

## 🧱 Exploitation Process:

We first allocate **three chunks** on the heap. The third chunk is added only to prevent the second chunk (once freed) from merging with the top chunk.

In **lines 65–66**, we free the first two chunks.


By **line 76**, we leak the addresses of the first two chunks using a UAF vulnerability and compute the address of the second chunk.

We then **poison the `fd` pointer** of the second chunk so that the next time `malloc()` is called, it returns an **arbitrary address** of our choice. Our target address is **32 bytes past the first chunk**, which is where a **function pointer** resides. We plan to overwrite this function pointer with the address of the `win()` function.

In **line 77**, we compute the desired fake `fd` value.  
In **line 78**, we use the "edit" functionality to overwrite the second chunk’s `fd` field with our fake address.

Then, we call `malloc()` twice. On the **second call**, `malloc()` should return the **fake address** we injected—**not** the original first chunk's address.

In **line 82**, we write the address of the `win()` function to that location. This works because the first 8 bytes of the target structure are treated as the `age` field (but actually represent the function pointer).

Finally, by selecting **menu option 2**, we trigger the execution of the overwritten function pointer inside the previously freed chunk—now pointing to `win()`. This results in **shell execution**.
![Capture](https://github.com/user-attachments/assets/29ce7a5f-56b7-483c-907b-c617aacbaecc)

### Ref & challenge:
https://github.com/SecurityInnovation/glibc_heap_exploitation_training/tree/master/modules/fd_poison/challenge1
