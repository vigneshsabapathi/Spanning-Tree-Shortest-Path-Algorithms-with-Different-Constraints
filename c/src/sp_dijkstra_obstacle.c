#include <stdio.h>
#include <stdlib.h>
#include "shortest_path.h"
#include "min_heap.h"

SPResult sp_dijkstra_obstacle(const Graph *g, int source)
{
    int V = g->num_vertices;

    SPResult result;
    result.source         = source;
    result.target         = -1;
    result.num_vertices   = V;
    result.target_reached = true;
    result.time_us        = 0;

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

            if (visited[v])           continue;
            if (g->vertex_blocked[v]) continue;
            if (adj->edge_blocked)    continue;

            int weight  = adj->weight;
            int penalty = g->edge_penalty[adj->edge_id];

            if (penalty != 0 && weight > INF / penalty) continue;
            int effective_weight = weight * penalty;
            if (result.dist[u] > INF - effective_weight) continue;

            int new_dist = result.dist[u] + effective_weight;

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
