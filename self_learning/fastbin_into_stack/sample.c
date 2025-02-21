#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

#define NOP __asm__("nop")

int main()
{
	// Fill up tcache
	void *ptrs[7];

	for (int i=0; i<7; i++) {
		ptrs[i] = malloc(8);
	}
	for (int i=0; i<7; i++) {
		free(ptrs[i]);
	}


	unsigned long stack_var[40] ;//__attribute__ ((aligned (0x10)));	// Target stack buffer

	int *a = calloc(1,8);
	int *b = calloc(1,8);
	int *c = calloc(1,8);

	free(a);

	free(b);

	free(a);	// Double free

	unsigned long *d = calloc(1,8); // first a

	calloc(1,8); // b

	stack_var[1] = 0x20;

	unsigned long ptr = (unsigned long)stack_var;
	unsigned long addr = (unsigned long) d;

	/*VULNERABILITY*/
	NOP;
	*d = (addr >> 12) ^ ptr;	//setting fd pointer
	NOP;
	/*VULNERABILITY*/

	calloc(1,8); // second a

	int *p = calloc(1,8); // this chunk will allocate on stack
	
	read(0, p, 0x300); // write buf into heap, wait, heap?!?!

	//assert((unsigned long)p == (unsigned long)stack_var + 0x10);
}
