#include <stdio.h>
#include <stdlib.h>
#include "union_find.h"

#define ASSERT(cond, msg) do { if (!(cond)) { fprintf(stderr, "FAIL [%s:%d]: %s\n", __FILE__, __LINE__, msg); exit(1); } } while(0)
#define PASS(msg) printf("PASS: %s\n", msg)

int main(void) {
    UnionFind *uf = uf_create(5);
    ASSERT(uf != NULL, "uf_create returned NULL");
    for (int i = 0; i < 5; i++)
        ASSERT(uf_find(uf, i) == i, "initial find(i) should equal i");
    PASS("initial find(i)==i for all i");

    uf_union(uf, 0, 1);
    ASSERT(uf_connected(uf, 0, 1) == true,  "connected(0,1) should be true after union");
    ASSERT(uf_connected(uf, 0, 2) == false, "connected(0,2) should be false");
    PASS("union(0,1): connected(0,1)==true, connected(0,2)==false");

    uf_union(uf, 2, 3);
    ASSERT(uf_connected(uf, 2, 3) == true, "connected(2,3) should be true after union");
    PASS("union(2,3): connected(2,3)==true");

    uf_union(uf, 1, 3);
    ASSERT(uf_connected(uf, 0, 1) == true, "connected(0,1) should be true");
    ASSERT(uf_connected(uf, 0, 2) == true, "connected(0,2) should be true after merging components");
    ASSERT(uf_connected(uf, 0, 3) == true, "connected(0,3) should be true");
    ASSERT(uf_connected(uf, 1, 2) == true, "connected(1,2) should be true");
    ASSERT(uf_connected(uf, 1, 3) == true, "connected(1,3) should be true");
    ASSERT(uf_connected(uf, 2, 3) == true, "connected(2,3) should be true");
    ASSERT(uf_connected(uf, 0, 4) == false, "connected(0,4) should be false");
    ASSERT(uf_connected(uf, 1, 4) == false, "connected(1,4) should be false");
    ASSERT(uf_connected(uf, 2, 4) == false, "connected(2,4) should be false");
    ASSERT(uf_connected(uf, 3, 4) == false, "connected(3,4) should be false");
    PASS("union(1,3): all of 0,1,2,3 connected, none connected to 4");

    uf_reset(uf);
    for (int i = 0; i < 5; i++)
        ASSERT(uf_find(uf, i) == i, "after reset, find(i) should equal i");
    PASS("reset: find(i)==i for all i");

    uf_destroy(uf);
    PASS("uf_destroy completed");

    return 0;
}
