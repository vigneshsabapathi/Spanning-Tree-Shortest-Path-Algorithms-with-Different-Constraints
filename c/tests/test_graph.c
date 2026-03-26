#include <stdio.h>
#include <stdlib.h>
#include "graph.h"

#define ASSERT(cond, msg) do { if (!(cond)) { fprintf(stderr, "FAIL [%s:%d]: %s\n", __FILE__, __LINE__, msg); exit(1); } } while(0)
#define PASS(msg) printf("PASS: %s\n", msg)

int main(void) {
    Graph *g = graph_create(5);
    ASSERT(g != NULL,            "graph_create returned NULL");
    ASSERT(g->num_vertices == 5, "num_vertices should be 5");
    PASS("graph_create with 5 vertices");

    graph_add_edge(g, 0, 1, 10);
    graph_add_edge(g, 0, 2, 3);
    graph_add_edge(g, 1, 3, 5);
    graph_add_edge(g, 2, 3, 8);
    graph_add_edge(g, 3, 4, 2);
    PASS("added 5 edges");

    ASSERT(graph_edge_count(g) == 5, "edge_count should be 5");
    PASS("edge_count == 5");

    ASSERT(g->num_vertices == 5, "num_vertices should remain 5");
    PASS("num_vertices == 5");

    graph_block_vertex(g, 2);
    ASSERT(g->vertex_blocked[2] == true, "vertex_blocked[2] should be true after block_vertex");
    PASS("block_vertex(2): vertex_blocked[2]==true");

    graph_unblock_vertex(g, 2);
    ASSERT(g->vertex_blocked[2] == false, "vertex_blocked[2] should be false after unblock_vertex");
    PASS("unblock_vertex(2): vertex_blocked[2]==false");

    graph_block_edge(g, 0, 1);
    int found = 0;
    for (int i = 0; i < g->num_edges; i++) {
        Edge *e = &g->edge_list[i];
        if ((e->src == 0 && e->dest == 1) || (e->src == 1 && e->dest == 0)) {
            ASSERT(e->blocked == true, "edge 0-1 should be blocked");
            found = 1;
            break;
        }
    }
    ASSERT(found == 1, "edge 0-1 should exist in edge_list");
    PASS("block_edge(0,1): edge found and blocked==true");

    graph_destroy(g);
    PASS("graph_destroy completed");

    return 0;
}
