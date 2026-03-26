#include "graph_gen.h"
#include <stdlib.h>
#include <time.h>

static int edge_exists(const Graph *g, int u, int v)
{
    AdjNode *node = g->adj[u].head;
    while (node) {
        if (node->dest == v)
            return 1;
        node = node->next;
    }
    return 0;
}

Graph *gen_random_graph(int num_vertices, double density, int max_weight,
                        unsigned int seed)
{
    srand(seed);

    Graph *g = graph_create(num_vertices);

    for (int i = 0; i < num_vertices; i++) {
        for (int j = i + 1; j < num_vertices; j++) {
            double r = rand() / (double)RAND_MAX;
            if (r < density) {
                int w = (rand() % max_weight) + 1;
                graph_add_edge(g, i, j, w);
            }
        }
    }

    return g;
}

/* Guarantees connectivity via a random spanning tree (Fisher-Yates shuffle),
 * then adds extra edges to approach the target density. */
Graph *gen_connected_graph(int num_vertices, double density, int max_weight,
                           unsigned int seed)
{
    srand(seed);

    Graph *g = graph_create(num_vertices);

    int *shuffled = malloc(num_vertices * sizeof(int));
    if (!shuffled) {
        graph_destroy(g);
        return NULL;
    }
    for (int i = 0; i < num_vertices; i++)
        shuffled[i] = i;
    for (int i = num_vertices - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = shuffled[i];
        shuffled[i] = shuffled[j];
        shuffled[j] = tmp;
    }

    for (int i = 0; i < num_vertices - 1; i++) {
        int w = (rand() % max_weight) + 1;
        graph_add_edge(g, shuffled[i], shuffled[i + 1], w);
    }
    free(shuffled);

    long long max_edges    = (long long)num_vertices * (num_vertices - 1) / 2;
    int       target_edges = (int)(density * (double)max_edges);
    int       attempts     = target_edges * 10 + num_vertices * num_vertices;

    while (g->num_edges < target_edges && attempts-- > 0) {
        int i = rand() % num_vertices;
        int j = rand() % num_vertices;
        if (i == j)
            continue;
        if (i > j) { int tmp = i; i = j; j = tmp; }  /* canonical order */
        if (edge_exists(g, i, j))
            continue;
        int w = (rand() % max_weight) + 1;
        graph_add_edge(g, i, j, w);
    }

    return g;
}

/* Each cell (r,c) maps to vertex r*cols+c; edges connect right and down neighbours. */
Graph *gen_grid_graph(int rows, int cols, int max_weight, unsigned int seed)
{
    srand(seed);

    int num_vertices = rows * cols;
    Graph *g = graph_create(num_vertices);

    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            int v = r * cols + c;
            if (c + 1 < cols)
                graph_add_edge(g, v, v + 1, (rand() % max_weight) + 1);
            if (r + 1 < rows)
                graph_add_edge(g, v, v + cols, (rand() % max_weight) + 1);
        }
    }

    return g;
}

/* Builds a grid graph then randomly blocks interior vertices and applies
 * penalty factors (2-5) to ~20% of edges. */
Graph *gen_obstacle_graph(int rows, int cols, double obstacle_fraction,
                          int max_weight, unsigned int seed)
{
    Graph *g = gen_grid_graph(rows, cols, max_weight, seed);

    int V = g->num_vertices;

    int num_to_block = (int)(obstacle_fraction * V);
    int blocked      = 0;
    int attempts     = num_to_block * 20 + V;

    while (blocked < num_to_block && attempts-- > 0) {
        int v = rand() % V;
        if (v == 0 || v == V - 1)
            continue;
        if (g->vertex_blocked[v])
            continue;
        graph_block_vertex(g, v);
        blocked++;
    }

    double penalty_fraction = 0.20;
    int    num_edges        = g->num_edges;

    for (int e = 0; e < num_edges; e++) {
        double r = rand() / (double)RAND_MAX;
        if (r < penalty_fraction) {
            int penalty = (rand() % 4) + 2;   /* 2..5 */
            int src  = g->edge_list[e].src;
            int dest = g->edge_list[e].dest;
            graph_set_edge_penalty(g, src, dest, penalty);
        }
    }

    return g;
}
