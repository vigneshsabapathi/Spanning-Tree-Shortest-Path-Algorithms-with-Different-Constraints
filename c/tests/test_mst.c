#include <stdio.h>
#include <stdlib.h>
#include "graph.h"
#include "mst.h"

#define ASSERT(cond, msg) do { if (!(cond)) { fprintf(stderr, "FAIL [%s:%d]: %s\n", __FILE__, __LINE__, msg); exit(1); } } while(0)
#define PASS(msg) printf("PASS: %s\n", msg)

int main(void) {
    /* Classic 9-vertex graph */
    Graph *g = graph_create(9);
    ASSERT(g != NULL, "graph_create returned NULL");

    graph_add_edge(g, 0, 1, 4);
    graph_add_edge(g, 0, 7, 8);
    graph_add_edge(g, 1, 2, 8);
    graph_add_edge(g, 1, 7, 11);
    graph_add_edge(g, 2, 3, 7);
    graph_add_edge(g, 2, 5, 4);
    graph_add_edge(g, 2, 8, 2);
    graph_add_edge(g, 3, 4, 9);
    graph_add_edge(g, 3, 5, 14);
    graph_add_edge(g, 4, 5, 10);
    graph_add_edge(g, 5, 6, 2);
    graph_add_edge(g, 6, 7, 1);
    graph_add_edge(g, 6, 8, 6);
    graph_add_edge(g, 7, 8, 7);
    PASS("built classic 9-vertex graph (14 edges)");

    /* Run mst_kruskal */
    MSTResult kr = mst_kruskal(g);
    ASSERT(kr.total_weight == 37, "kruskal total_weight should be 37");
    ASSERT(kr.num_edges == 8,     "kruskal num_edges should be 8 (9 vertices - 1)");
    PASS("mst_kruskal: total_weight==37, num_edges==8");

    /* Run mst_prim from start=0 */
    MSTResult pr = mst_prim(g, 0);
    ASSERT(pr.total_weight == 37, "prim total_weight should be 37");
    ASSERT(pr.num_edges == 8,     "prim num_edges should be 8");
    PASS("mst_prim(start=0): total_weight==37, num_edges==8");

    /* mst_results_equal should return true */
    ASSERT(mst_results_equal(&kr, &pr) == true, "kruskal and prim results should be equal");
    PASS("mst_results_equal returns true");

    mst_result_free(&kr);
    mst_result_free(&pr);
    graph_destroy(g);
    PASS("freed MST results and destroyed 9-vertex graph");

    /* Test disconnected graph: 4 vertices, edges 0-1(1) and 2-3(1) only */
    Graph *dg = graph_create(4);
    ASSERT(dg != NULL, "graph_create (disconnected) returned NULL");
    graph_add_edge(dg, 0, 1, 1);
    graph_add_edge(dg, 2, 3, 1);

    MSTResult dkr = mst_kruskal(dg);
    ASSERT(dkr.is_connected == false, "kruskal on disconnected graph: is_connected should be false");
    PASS("kruskal on disconnected graph: is_connected==false");

    mst_result_free(&dkr);
    graph_destroy(dg);
    PASS("freed disconnected MST result and destroyed graph");

    return 0;
}
