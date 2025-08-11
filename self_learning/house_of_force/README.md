# House of Force

overwriting topchunk size to achieve arb memory by malloc()

fixed in glibc 2.29

tips:
```
requested size:
	evil_size = target_addr - topchunk_hdr - 0x10 - 0x10

	#first- 0x10: For the metadata tacked onto the request 
	#second - 0x10: To account for the metadata prior to the __malloc_hook

```
<img width="501" height="369" alt="force" src="https://github.com/user-attachments/assets/1f0e9f1a-de5b-42e2-b7b4-7f9167f2ce86" />
