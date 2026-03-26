#include "graph.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Graph *graph_create(int num_vertices)
{
    if (num_vertices <= 0 || num_vertices > MAX_VERTICES) {
        fprintf(stderr, "graph_create: invalid num_vertices %d\n", num_vertices);
        exit(1);
    }

    Graph *g = (Graph *)malloc(sizeof(Graph));
    if (!g) {
        fprintf(stderr, "graph_create: failed to allocate Graph\n");
        exit(1);
    }

    g->num_vertices  = num_vertices;
    g->num_edges     = 0;
    g->edge_capacity = 16;

    g->adj = (AdjList *)calloc(num_vertices, sizeof(AdjList));
    if (!g->adj) {
        fprintf(stderr, "graph_create: failed to allocate adj array\n");
        exit(1);
    }

    g->edge_list = (Edge *)malloc(g->edge_capacity * sizeof(Edge));
    if (!g->edge_list) {
        fprintf(stderr, "graph_create: failed to allocate edge_list\n");
        exit(1);
    }

    g->vertex_blocked = (bool *)calloc(num_vertices, sizeof(bool));
    if (!g->vertex_blocked) {
        fprintf(stderr, "graph_create: failed to allocate vertex_blocked\n");
        exit(1);
    }

    g->edge_penalty = (int *)malloc(g->edge_capacity * sizeof(int));
    if (!g->edge_penalty) {
        fprintf(stderr, "graph_create: failed to allocate edge_penalty\n");
        exit(1);
    }

    return g;
}

void graph_destroy(Graph *g)
{
    if (!g) return;

    for (int v = 0; v < g->num_vertices; v++) {
        AdjNode *cur = g->adj[v].head;
        while (cur) {
            AdjNode *next = cur->next;
            free(cur);
            cur = next;
        }
    }

    free(g->adj);
    free(g->edge_list);
    free(g->vertex_blocked);
    free(g->edge_penalty);
    free(g);
}

/* Double edge_list and edge_penalty capacity. */
static void grow_edge_storage(Graph *g)
{
    int new_cap = g->edge_capacity * 2;

    Edge *new_list = (Edge *)realloc(g->edge_list, new_cap * sizeof(Edge));
    if (!new_list) {
        fprintf(stderr, "graph_add_edge: failed to grow edge_list\n");
        exit(1);
    }
    g->edge_list = new_list;

    int *new_penalty = (int *)realloc(g->edge_penalty, new_cap * sizeof(int));
    if (!new_penalty) {
        fprintf(stderr, "graph_add_edge: failed to grow edge_penalty\n");
        exit(1);
    }
    g->edge_penalty = new_penalty;

    g->edge_capacity = new_cap;
}

static AdjNode *make_adj_node(int dest, int weight, int edge_id)
{
    AdjNode *node = (AdjNode *)malloc(sizeof(AdjNode));
    if (!node) {
        fprintf(stderr, "graph_add_edge: failed to allocate AdjNode\n");
        exit(1);
    }
    node->dest         = dest;
    node->weight       = weight;
    node->edge_id      = edge_id;
    node->edge_blocked = false;
    node->next         = NULL;
    return node;
}

void graph_add_edge(Graph *g, int src, int dest, int weight)
{
    if (!g) return;
    if (src < 0 || src >= g->num_vertices) {
        fprintf(stderr, "graph_add_edge: src %d out of range\n", src);
        exit(1);
    }
    if (dest < 0 || dest >= g->num_vertices) {
        fprintf(stderr, "graph_add_edge: dest %d out of range\n", dest);
        exit(1);
    }

    if (g->num_edges >= g->edge_capacity)
        grow_edge_storage(g);

    int edge_id = g->num_edges;

    g->edge_list[edge_id].src     = src;
    g->edge_list[edge_id].dest    = dest;
    g->edge_list[edge_id].weight  = weight;
    g->edge_list[edge_id].edge_id = edge_id;
    g->edge_list[edge_id].blocked = false;
    g->edge_penalty[edge_id]      = 1;

    AdjNode *fwd = make_adj_node(dest, weight, edge_id);
    fwd->next         = g->adj[src].head;
    g->adj[src].head  = fwd;

    AdjNode *rev = make_adj_node(src, weight, edge_id);
    rev->next         = g->adj[dest].head;
    g->adj[dest].head = rev;

    g->num_edges++;
}

void graph_block_vertex(Graph *g, int v)
{
    if (!g) return;
    if (v < 0 || v >= g->num_vertices) {
        fprintf(stderr, "graph_block_vertex: vertex %d out of range\n", v);
        exit(1);
    }
    g->vertex_blocked[v] = true;
}

void graph_unblock_vertex(Graph *g, int v)
{
    if (!g) return;
    if (v < 0 || v >= g->num_vertices) {
        fprintf(stderr, "graph_unblock_vertex: vertex %d out of range\n", v);
        exit(1);
    }
    g->vertex_blocked[v] = false;
}

void graph_block_edge(Graph *g, int src, int dest)
{
    if (!g) return;
    if (src < 0 || src >= g->num_vertices) {
        fprintf(stderr, "graph_block_edge: src %d out of range\n", src);
        exit(1);
    }
    if (dest < 0 || dest >= g->num_vertices) {
        fprintf(stderr, "graph_block_edge: dest %d out of range\n", dest);
        exit(1);
    }

    int edge_id = -1;
    for (int i = 0; i < g->num_edges; i++) {
        Edge *e = &g->edge_list[i];
        if ((e->src == src && e->dest == dest) ||
            (e->src == dest && e->dest == src)) {
            e->blocked = true;
            edge_id    = e->edge_id;
            break;
        }
    }

    if (edge_id == -1) {
        fprintf(stderr, "graph_block_edge: edge (%d,%d) not found\n", src, dest);
        return;
    }

    for (AdjNode *cur = g->adj[src].head; cur; cur = cur->next) {
        if (cur->dest == dest && cur->edge_id == edge_id) {
            cur->edge_blocked = true;
            break;
        }
    }

    for (AdjNode *cur = g->adj[dest].head; cur; cur = cur->next) {
        if (cur->dest == src && cur->edge_id == edge_id) {
            cur->edge_blocked = true;
            break;
        }
    }
}

void graph_set_edge_penalty(Graph *g, int src, int dest, int penalty)
{
    if (!g) return;
    if (src < 0 || src >= g->num_vertices) {
        fprintf(stderr, "graph_set_edge_penalty: src %d out of range\n", src);
        exit(1);
    }
    if (dest < 0 || dest >= g->num_vertices) {
        fprintf(stderr, "graph_set_edge_penalty: dest %d out of range\n", dest);
        exit(1);
    }

    int edge_id = -1;
    for (int i = 0; i < g->num_edges; i++) {
        Edge *e = &g->edge_list[i];
        if ((e->src == src && e->dest == dest) ||
            (e->src == dest && e->dest == src)) {
            edge_id = e->edge_id;
            break;
        }
    }

    if (edge_id == -1) {
        fprintf(stderr, "graph_set_edge_penalty: edge (%d,%d) not found\n", src, dest);
        return;
    }

    g->edge_penalty[edge_id] = penalty;

    for (AdjNode *cur = g->adj[src].head; cur; cur = cur->next) {
        if (cur->dest == dest && cur->edge_id == edge_id) {
            cur->weight = penalty;
            break;
        }
    }

    for (AdjNode *cur = g->adj[dest].head; cur; cur = cur->next) {
        if (cur->dest == src && cur->edge_id == edge_id) {
            cur->weight = penalty;
            break;
        }
    }
}

void graph_print(const Graph *g)
{
    if (!g) return;

    for (int v = 0; v < g->num_vertices; v++) {
        printf("[%d]%s: ", v, g->vertex_blocked[v] ? "(blocked)" : "");
        for (AdjNode *cur = g->adj[v].head; cur; cur = cur->next) {
            printf("%d(w=%d,eid=%d%s) -> ",
                   cur->dest,
                   cur->weight,
                   cur->edge_id,
                   cur->edge_blocked ? ",blocked" : "");
        }
        printf("NULL\n");
    }
}

int graph_edge_count(const Graph *g)
{
    if (!g) return 0;
    return g->num_edges;
}
