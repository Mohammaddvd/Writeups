## Notes
the target binary compiled with old libc and this technique is not working in newer versions since a check
added to verify the double-linked list:
[pic]

we have three chunks, the program tries to free the 2nd and 3rd chunks, we can write on 1st and 2nd chunks.
strategy is the first chunk is a place to hold our shellcode, we manipulate the fd&bk fields of second chunk,
when the third chunk free, the "unlink" macro would trigger and place the address of first chunk into GOT of
"puts" function and boom.
(in shellcode we load instructions to jump to the winner function)

### Source
https://github.com/SecurityInnovation/glibc_heap_exploitation_training/tree/master