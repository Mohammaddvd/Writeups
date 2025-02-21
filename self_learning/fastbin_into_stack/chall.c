#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <errno.h>
#include <signal.h>

#define PORT 8081
#define MAX_USERS 30
#define NOP __asm__("nop")

int sockfd, cfd;
struct sockaddr_in address;
int lenaddr = sizeof(address);

// void banner()
// {

//     // "1 - signup"
//     // "2 - give up"
//     // "3 - submit flag"
//     // "4 - leak"

//     return NULL;

// }

void handle_sigabrt(int sig) {
    close(cfd);
    close(sockfd);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{
    if (signal(SIGABRT, handle_sigabrt) == SIG_ERR) {
        perror("Unable to catch SIGABRT");
        exit(EXIT_FAILURE);
    }
    int *users[MAX_USERS];
    char *flag = "CTF{Pwnsters!}";
    char tmpflag[32];
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    int uc = 0;
    char choose[8];
    int option = 0;
    int which = 0;
    char *leakfmt = "%p %p";
    char leakout[40];
    int len;

    if(bind(sockfd, &address, sizeof(address)) == -1)
    {
        perror("bind");
        exit(1);
    }
    if(listen(sockfd, 5))
    {
        perror("listen");
        exit(1);
    }

    while(uc < MAX_USERS)
    {
        cfd = accept(sockfd, &address, &lenaddr);
        if(cfd == -1)
        {
            perror("accept");
            exit(1);
        }
        
        read(cfd, choose, sizeof(int));
        option = atoi(choose);

	switch(option)
	{
		case 1:
            if(uc < 8){
                users[uc] = (char *) malloc(20);
                read(cfd, users[uc], 0x100); //overflow bug
                uc++;
            }else{
                users[uc] = (char *) calloc(1, 20);
                read(cfd, users[uc], 0x1000); //overflow bug
                uc++;
            }
			break;
		case 2:
			memset(choose, 0, 8);
			read(cfd, choose, sizeof(int));
			which = atoi(choose);
			free(users[which]);     // double-free / use-after-free
			break;
		case 3:
            len = read(cfd, tmpflag+8, 24);
            memset(tmpflag+8+len-1, 0, 3);
            if( strcmp(tmpflag+8, flag) == 0 )
            {
                printf("we have a winner!\n");
                exit(0);
            }
			break;
		case 4:
            // Leaking these values
            // char tmpflag[32];
            // users[which];
            read(cfd, choose, sizeof(int));
			which = atoi(choose);
            sprintf(leakout, leakfmt, tmpflag, users[which]);
            write(cfd, leakout, 40);
			break;
        case 5:
            uc = 100;
            close(sockfd);
		default:
			break;
	}
        NOP;
        NOP;
        close(cfd);
    }

    return 0;

}
