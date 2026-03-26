#include "mst.h"
#include "min_heap.h"
#include <stdio.h>
#include <stdlib.h>

MSTResult mst_prim(const Graph *g, int start_vertex) {
    int V = g->num_vertices;

    int  *dist          = malloc(V * sizeof(int));
    bool *in_mst        = malloc(V * sizeof(bool));
    int  *parent        = malloc(V * sizeof(int));
    int  *parent_weight = malloc(V * sizeof(int));

    for (int i = 0; i < V; i++) {
        dist[i]          = INF;
        in_mst[i]        = false;
        parent[i]        = -1;
        parent_weight[i] = 0;
    }

    dist[start_vertex] = 0;

    MinHeap *heap = heap_create(V);

    /* Insert all non-blocked vertices; start_vertex gets key 0, rest get INF */
    for (int v = 0; v < V; v++) {
        if (!g->vertex_blocked[v]) {
            heap_insert(heap, dist[v], v);
        }
    }

    while (!heap_is_empty(heap)) {
        HeapNode node = heap_extract_min(heap);
        int u         = node.value;

        /* All remaining vertices are unreachable */
        if (dist[u] == INF) {
            break;
        }

        in_mst[u] = true;

        /* Relax edges from u */
        for (AdjNode *adj = g->adj[u].head; adj != NULL; adj = adj->next) {
            int v      = adj->dest;
            int weight = adj->weight;

            if (in_mst[v])              continue;
            if (g->vertex_blocked[v])   continue;
            if (adj->edge_blocked)      continue;

            if (weight < dist[v]) {
                dist[v]          = weight;
                parent[v]        = u;
                parent_weight[v] = weight;
                heap_decrease_key(heap, v, weight);
            }
        }
    }

    /* Build MSTResult */
    int num_mst_edges = 0;
    for (int v = 0; v < V; v++) {
        if (parent[v] != -1 && v != start_vertex) {
            num_mst_edges++;
        }
    }

    Edge *edges = malloc(num_mst_edges * sizeof(Edge));
    int   idx   = 0;
    int   total = 0;

    for (int v = 0; v < V; v++) {
        if (parent[v] != -1 && v != start_vertex) {
            edges[idx].src     = parent[v];
            edges[idx].dest    = v;
            edges[idx].weight  = parent_weight[v];
            edges[idx].edge_id = -1;
            edges[idx].blocked = false;
            idx++;
            total += parent_weight[v];
        }
    }

    /* Count unblocked vertices to determine expected edge count */
    int unblocked = 0;
    for (int v = 0; v < V; v++) {
        if (!g->vertex_blocked[v]) {
            unblocked++;
        }
    }

    MSTResult result;
    result.edges        = edges;
    result.num_edges    = num_mst_edges;
    result.total_weight = total;
    result.is_connected = (num_mst_edges == unblocked - 1);
    result.time_us      = 0;

    free(dist);
    free(in_mst);
    free(parent);
    free(parent_weight);
    heap_destroy(heap);

    return result;
}
