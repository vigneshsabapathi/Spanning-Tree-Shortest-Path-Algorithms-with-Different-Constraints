#ifndef GRAPH_H
#define GRAPH_H

#include <stdbool.h>
#include <limits.h>

#define INF INT_MAX
#define MAX_VERTICES 100000
#define MAX_WEIGHT   100000

typedef struct AdjNode {
    int   dest;
    int   weight;
    int   edge_id;
    bool  edge_blocked;
    struct AdjNode *next;
} AdjNode;

typedef struct {
    AdjNode *head;
} AdjList;

typedef struct {
    int  src;
    int  dest;
    int  weight;
    int  edge_id;
    bool blocked;
} Edge;

typedef struct {
    int       num_vertices;
    int       num_edges;
    AdjList  *adj;
    Edge     *edge_list;
    int       edge_capacity;
    bool     *vertex_blocked;
    int      *edge_penalty;
} Graph;

Graph *graph_create(int num_vertices);
void   graph_destroy(Graph *g);
void   graph_add_edge(Graph *g, int src, int dest, int weight);
void   graph_block_vertex(Graph *g, int v);
void   graph_unblock_vertex(Graph *g, int v);
void   graph_block_edge(Graph *g, int src, int dest);
void   graph_set_edge_penalty(Graph *g, int src, int dest, int penalty);
void   graph_print(const Graph *g);
int    graph_edge_count(const Graph *g);

#endif /* GRAPH_H */
