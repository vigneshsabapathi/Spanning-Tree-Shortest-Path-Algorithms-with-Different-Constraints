#include "mst.h"
#include "union_find.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---------- static comparator for qsort ---------- */

static int edge_cmp_weight(const void *a, const void *b)
{
    const Edge *ea = (const Edge *)a;
    const Edge *eb = (const Edge *)b;
    return ea->weight - eb->weight;
}

/* ---------- Kruskal's MST ---------- */

MSTResult mst_kruskal(const Graph *g)
{
    MSTResult result;
    result.edges        = NULL;
    result.num_edges    = 0;
    result.total_weight = 0;
    result.is_connected = false;
    result.time_us      = 0;

    if (!g || g->num_vertices <= 0)
        return result;

    /* Copy edge list so we don't mutate the original graph */
    int edge_count = g->num_edges;
    Edge *work = (Edge *)malloc((size_t)edge_count * sizeof(Edge));
    if (!work)
        return result;
    memcpy(work, g->edge_list, (size_t)edge_count * sizeof(Edge));

    /* Sort by weight */
    qsort(work, (size_t)edge_count, sizeof(Edge), edge_cmp_weight);

    /* Union-Find over all vertices */
    UnionFind *uf = uf_create(g->num_vertices);
    if (!uf) {
        free(work);
        return result;
    }

    /* Pre-allocate result edge array (MST has at most V-1 edges) */
    int max_mst_edges = g->num_vertices - 1;
    if (max_mst_edges < 0)
        max_mst_edges = 0;

    result.edges = (Edge *)malloc((size_t)max_mst_edges * sizeof(Edge));
    if (!result.edges) {
        uf_destroy(uf);
        free(work);
        return result;
    }

    /* Main Kruskal loop */
    for (int i = 0; i < edge_count && result.num_edges < max_mst_edges; i++) {
        Edge *e = &work[i];

        /* Skip blocked edges or vertices */
        if (e->blocked)
            continue;
        if (g->vertex_blocked && (g->vertex_blocked[e->src] || g->vertex_blocked[e->dest]))
            continue;

        int root_src  = uf_find(uf, e->src);
        int root_dest = uf_find(uf, e->dest);

        if (root_src != root_dest) {
            uf_union(uf, e->src, e->dest);
            result.edges[result.num_edges++] = *e;
            result.total_weight += e->weight;
        }
    }

    result.is_connected = (result.num_edges == max_mst_edges);

    uf_destroy(uf);
    free(work);

    return result;
}

/* ---------- Shared utility functions ---------- */

void mst_result_free(MSTResult *r)
{
    if (!r)
        return;
    free(r->edges);
    r->edges = NULL;
}

void mst_result_print(const MSTResult *r, const char *label)
{
    if (!r)
        return;

    printf("=== %s ===\n", label ? label : "MST");
    printf("  Total weight : %d\n", r->total_weight);
    printf("  Num edges    : %d\n", r->num_edges);
    printf("  Connected    : %s\n", r->is_connected ? "yes" : "no");

    for (int i = 0; i < r->num_edges; i++) {
        const Edge *e = &r->edges[i];
        printf("  edge[%d]: %d -- %d  weight=%d\n",
               i, e->src, e->dest, e->weight);
    }
}

bool mst_results_equal(const MSTResult *a, const MSTResult *b)
{
    if (!a || !b)
        return a == b;
    return (a->total_weight == b->total_weight) &&
           (a->num_edges    == b->num_edges);
}
