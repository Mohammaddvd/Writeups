## Notes
the target binary compiled with old libc and this technique is not working in newer versions since a check
added to verify the double-linked list:
[pic]

like last challenge "easy_1" we have the same code except the free part, we are just freeing the last chunk.
also if you look at the second call of "fgets", we have a heap-overflow which it can overwrite the header
of the last chunk which it would be free.

the strategy is again we manipulate the fd&bk fields of 2nd chunk and then overwrite the header try to set the
"prev_size" which is 0x90 and also try to unset the "prev_inuse bit" which the result is again 0x90.

since it is the last chunk, consolidation with top chunk would happen which triggers unlink macro again (if prev_inuse bit is unset!).

### Source
https://github.com/SecurityInnovation/glibc_heap_exploitation_training/tree/master