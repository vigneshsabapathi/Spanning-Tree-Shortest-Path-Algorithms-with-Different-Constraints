#include "graph_gen.h"
#include <stdlib.h>
#include <time.h>

/* -----------------------------------------------------------------------
 * Helper: check whether an undirected edge (u, v) already exists by
 * scanning the adjacency list of u.
 * --------------------------------------------------------------------- */
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

/* -----------------------------------------------------------------------
 * 1. gen_random_graph
 *    Iterates every undirected pair (i,j), i<j, and adds each edge with
 *    probability == density.
 * --------------------------------------------------------------------- */
Graph *gen_random_graph(int num_vertices, double density, int max_weight,
                        unsigned int seed)
{
    srand(seed);

    Graph *g = graph_create(num_vertices);
    if (!g)
        return NULL;

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

/* -----------------------------------------------------------------------
 * 2. gen_connected_graph
 *    Guarantees connectivity via a random spanning tree (Fisher-Yates
 *    shuffle), then fills in extra edges to approach the target density.
 * --------------------------------------------------------------------- */
Graph *gen_connected_graph(int num_vertices, double density, int max_weight,
                           unsigned int seed)
{
    srand(seed);

    Graph *g = graph_create(num_vertices);
    if (!g)
        return NULL;

    /* Build a shuffled vertex array (Fisher-Yates). */
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

    /* Connect consecutive vertices in the shuffled order → spanning tree. */
    for (int i = 0; i < num_vertices - 1; i++) {
        int w = (rand() % max_weight) + 1;
        graph_add_edge(g, shuffled[i], shuffled[i + 1], w);
    }
    free(shuffled);

    /* Determine how many more edges are needed to hit target density. */
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

/* -----------------------------------------------------------------------
 * 3. gen_grid_graph
 *    Each cell (r,c) is vertex r*cols+c.  Edges connect right and down
 *    neighbours.
 * --------------------------------------------------------------------- */
Graph *gen_grid_graph(int rows, int cols, int max_weight, unsigned int seed)
{
    srand(seed);

    int num_vertices = rows * cols;
    Graph *g = graph_create(num_vertices);
    if (!g)
        return NULL;

    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            int v = r * cols + c;

            /* Right neighbour */
            if (c + 1 < cols) {
                int w = (rand() % max_weight) + 1;
                graph_add_edge(g, v, v + 1, w);
            }

            /* Down neighbour */
            if (r + 1 < rows) {
                int w = (rand() % max_weight) + 1;
                graph_add_edge(g, v, v + cols, w);
            }
        }
    }

    return g;
}

/* -----------------------------------------------------------------------
 * 4. gen_obstacle_graph
 *    Builds a grid graph then:
 *      - Randomly blocks a fraction of interior vertices.
 *      - Randomly applies a penalty factor (2-5) to a fraction of edges.
 * --------------------------------------------------------------------- */
Graph *gen_obstacle_graph(int rows, int cols, double obstacle_fraction,
                          int max_weight, unsigned int seed)
{
    /* gen_grid_graph already calls srand(seed), so the RNG is seeded. */
    Graph *g = gen_grid_graph(rows, cols, max_weight, seed);
    if (!g)
        return NULL;

    int V = g->num_vertices;

    /* Block random interior vertices (never block vertex 0 or V-1). */
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

    /* Apply a penalty factor (2-5) to roughly 20 % of edges. */
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
