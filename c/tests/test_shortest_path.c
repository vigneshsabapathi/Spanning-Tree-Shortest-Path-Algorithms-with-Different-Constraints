#include <stdio.h>
#include <stdlib.h>
#include "graph.h"
#include "shortest_path.h"

#define ASSERT(cond, msg) do { if (!(cond)) { fprintf(stderr, "FAIL [%s:%d]: %s\n", __FILE__, __LINE__, msg); exit(1); } } while(0)
#define PASS(msg) printf("PASS: %s\n", msg)

int main(void) {
    /*
     * 5-vertex undirected graph:
     *   0-1(10), 0-2(3), 1-3(2), 2-1(4), 2-3(8), 2-4(2), 3-4(5)
     */
    Graph *g = graph_create(5);
    ASSERT(g != NULL, "graph_create returned NULL");

    graph_add_edge(g, 0, 1, 10);
    graph_add_edge(g, 0, 2, 3);
    graph_add_edge(g, 1, 3, 2);
    graph_add_edge(g, 2, 1, 4);
    graph_add_edge(g, 2, 3, 8);
    graph_add_edge(g, 2, 4, 2);
    graph_add_edge(g, 3, 4, 5);
    PASS("built 5-vertex graph");

    SPResult r = sp_dijkstra(g, 0);
    ASSERT(r.dist[0] == 0,  "dist[0] should be 0");
    ASSERT(r.dist[2] == 3,  "dist[2] should be 3 (0->2)");
    ASSERT(r.dist[1] == 7,  "dist[1] should be 7 (0->2->1, cost 3+4)");
    ASSERT(r.dist[3] == 9,  "dist[3] should be 9 (0->2->1->3, cost 3+4+2)");
    ASSERT(r.dist[4] == 5,  "dist[4] should be 5 (0->2->4, cost 3+2)");
    PASS("dijkstra from 0: dist[] values correct");

    int path_len = 0;
    int *path = sp_reconstruct_path(&r, 3, &path_len);
    ASSERT(path != NULL,      "reconstructed path should not be NULL");
    ASSERT(path_len == 4,     "path to vertex 3 should have length 4");
    ASSERT(path[0] == 0,      "path[0] should be 0");
    ASSERT(path[1] == 2,      "path[1] should be 2");
    ASSERT(path[2] == 1,      "path[2] should be 1");
    ASSERT(path[3] == 3,      "path[3] should be 3");
    free(path);
    PASS("reconstruct path to 3: [0,2,1,3], path_len==4");

    sp_result_free(&r);

    graph_block_vertex(g, 2);
    SPResult r2 = sp_dijkstra(g, 0);
    ASSERT(r2.dist[1] == 10, "with vertex 2 blocked, dist[1] should be 10 (direct 0->1)");
    ASSERT(r2.dist[3] == 12, "with vertex 2 blocked, dist[3] should be 12 (0->1->3, cost 10+2)");
    PASS("dijkstra with vertex 2 blocked: dist[1]==10, dist[3]==12");

    sp_result_free(&r2);
    graph_unblock_vertex(g, 2);

    /* penalty=10 makes 0->2->1 cost 3*10+4*10=70, so direct 0->1(10) wins */
    graph_set_edge_penalty(g, 0, 2, 10);
    SPResult r3 = sp_dijkstra_obstacle(g, 0);
    ASSERT(r3.dist[1] == 10, "obstacle dijkstra: dist[1] should be 10 (direct 0->1 preferred over penalized 0->2->1)");
    PASS("sp_dijkstra_obstacle with penalty on 0-2: dist[1]==10");

    sp_result_free(&r3);

    graph_destroy(g);
    PASS("graph_destroy completed");

    return 0;
}
