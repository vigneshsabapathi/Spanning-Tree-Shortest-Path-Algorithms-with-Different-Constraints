#include <stdlib.h>
#include <stdio.h>
#include "union_find.h"

UnionFind *uf_create(int size) {
    UnionFind *uf = malloc(sizeof(UnionFind));
    if (!uf) {
        fprintf(stderr, "uf_create: failed to allocate UnionFind\n");
        exit(1);
    }

    uf->size = size;

    uf->parent = malloc(size * sizeof(int));
    if (!uf->parent) {
        fprintf(stderr, "uf_create: failed to allocate parent array\n");
        exit(1);
    }

    uf->rank = malloc(size * sizeof(int));
    if (!uf->rank) {
        fprintf(stderr, "uf_create: failed to allocate rank array\n");
        exit(1);
    }

    for (int i = 0; i < size; i++) {
        uf->parent[i] = i;
        uf->rank[i]   = 0;
    }

    return uf;
}

void uf_destroy(UnionFind *uf) {
    if (!uf) return;
    free(uf->parent);
    free(uf->rank);
    free(uf);
}

int uf_find(UnionFind *uf, int x) {
    /* Walk up to find root */
    int root = x;
    while (uf->parent[root] != root) {
        root = uf->parent[root];
    }

    /* Path compression: point every node along the path directly to root */
    while (uf->parent[x] != root) {
        int next = uf->parent[x];
        uf->parent[x] = root;
        x = next;
    }

    return root;
}

bool uf_union(UnionFind *uf, int x, int y) {
    int rx = uf_find(uf, x);
    int ry = uf_find(uf, y);

    if (rx == ry) return false;

    /* Union by rank: attach shorter tree under taller tree's root */
    if (uf->rank[rx] < uf->rank[ry]) {
        uf->parent[rx] = ry;
    } else if (uf->rank[rx] > uf->rank[ry]) {
        uf->parent[ry] = rx;
    } else {
        /* Equal rank: pick rx as new root and increment its rank */
        uf->parent[ry] = rx;
        uf->rank[rx]++;
    }

    return true;
}

bool uf_connected(UnionFind *uf, int x, int y) {
    return uf_find(uf, x) == uf_find(uf, y);
}

void uf_reset(UnionFind *uf) {
    for (int i = 0; i < uf->size; i++) {
        uf->parent[i] = i;
        uf->rank[i]   = 0;
    }
}
