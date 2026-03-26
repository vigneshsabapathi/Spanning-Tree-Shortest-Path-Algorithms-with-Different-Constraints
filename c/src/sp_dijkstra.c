#include <stdio.h>
#include <stdlib.h>
#include "shortest_path.h"
#include "min_heap.h"

SPResult sp_dijkstra(const Graph *g, int source)
{
    int V = g->num_vertices;

    SPResult result;
    result.source        = source;
    result.target        = -1;
    result.num_vertices  = V;
    result.target_reached = true;
    result.time_us       = 0;

    result.dist = (int *)malloc(V * sizeof(int));
    result.prev = (int *)malloc(V * sizeof(int));
    bool *visited = (bool *)malloc(V * sizeof(bool));

    for (int i = 0; i < V; i++) {
        result.dist[i] = INF;
        result.prev[i] = -1;
        visited[i]     = false;
    }
    result.dist[source] = 0;

    MinHeap *heap = heap_create(V);

    for (int v = 0; v < V; v++) {
        if (!g->vertex_blocked[v]) {
            heap_insert(heap, result.dist[v], v);
        }
    }

    while (!heap_is_empty(heap)) {
        int u = heap_extract_min(heap).value;

        if (result.dist[u] == INF) {
            break;
        }

        visited[u] = true;

        for (AdjNode *adj = g->adj[u].head; adj != NULL; adj = adj->next) {
            int v = adj->dest;

            if (visited[v])          continue;
            if (g->vertex_blocked[v]) continue;
            if (adj->edge_blocked)   continue;

            int weight = adj->weight;
            if (result.dist[u] > INF - weight) continue;

            int new_dist = result.dist[u] + weight;

            if (new_dist < result.dist[v]) {
                result.dist[v] = new_dist;
                result.prev[v] = u;
                if (heap_contains(heap, v)) {
                    heap_decrease_key(heap, v, new_dist);
                }
            }
        }
    }

    heap_destroy(heap);
    free(visited);

    return result;
}

void sp_result_free(SPResult *r)
{
    if (r == NULL) return;
    free(r->dist);
    free(r->prev);
    r->dist = NULL;
    r->prev = NULL;
}

int *sp_reconstruct_path(const SPResult *r, int target, int *path_len)
{
    if (r->dist[target] == INF) {
        *path_len = 0;
        return NULL;
    }

    int len = 0;
    for (int v = target; v != -1; v = r->prev[v]) {
        len++;
    }

    int *path = (int *)malloc(len * sizeof(int));
    int  idx  = len - 1;
    for (int v = target; v != -1; v = r->prev[v]) {
        path[idx--] = v;
    }

    *path_len = len;
    return path;
}

void sp_result_print(const SPResult *r, int target)
{
    printf("Source: %d\n", r->source);
    printf("Target: %d\n", target);

    if (r->dist[target] == INF) {
        printf("Distance: unreachable\n");
        printf("Path: none\n");
        return;
    }

    printf("Distance: %d\n", r->dist[target]);

    int  path_len = 0;
    int *path     = sp_reconstruct_path(r, target, &path_len);

    printf("Path: ");
    for (int i = 0; i < path_len; i++) {
        if (i > 0) printf(" -> ");
        printf("%d", path[i]);
    }
    printf("\n");

    free(path);
}
