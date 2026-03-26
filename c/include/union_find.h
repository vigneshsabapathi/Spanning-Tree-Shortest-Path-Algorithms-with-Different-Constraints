#ifndef UNION_FIND_H
#define UNION_FIND_H

#include <stdbool.h>

typedef struct {
    int  size;
    int *parent;
    int *rank;
} UnionFind;

UnionFind *uf_create(int size);
void       uf_destroy(UnionFind *uf);
int        uf_find(UnionFind *uf, int x);
bool       uf_union(UnionFind *uf, int x, int y);
bool       uf_connected(UnionFind *uf, int x, int y);
void       uf_reset(UnionFind *uf);

#endif /* UNION_FIND_H */
