#include <stdlib.h>
#include <stdio.h>

#include "libpq-fe.h"

int main() {
    PGconn *conn = NULL;
    const int version = PQlibVersion();
    printf("PQlibVersion: %d\n", version);

    conn = PQconnectdb("dbname=zinnion user=zinnion password=xxxx host=127.0.0.1 port=26257 requiressl=1 sslmode=verify-full");
    PQstatus(conn);
    
    PQfinish(conn);
    return EXIT_SUCCESS;
}
