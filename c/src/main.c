/*
 * main.c — CLI driver for the algo project.
 *
 * Modes:
 *   demo   - Hand-crafted 9-vertex textbook graph demo
 *   bench  - Full MST + shortest-path benchmark suite
 *   mst    - MST on a generated graph (-v vertices -d density)
 *   path   - Shortest path on a generated graph (-v -d -s -t)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "graph.h"
#include "mst.h"
#include "shortest_path.h"
#include "graph_gen.h"
#include "benchmark.h"

static void print_usage(void)
{
    printf("Usage: ./algo [mode] [options]\n");
    printf("Modes:\n");
    printf("  demo   - Run demo on a hand-crafted graph\n");
    printf("  bench  - Run full benchmark suite\n");
    printf("  mst    - Run MST on generated graph (-v vertices -d density)\n");
    printf("  path   - Run shortest path (-v vertices -d density -s src -t target)\n");
}

static void print_path(const int *path, int len)
{
    if (path == NULL || len == 0) {
        printf("  (no path)\n");
        return;
    }
    printf("  Path: ");
    for (int i = 0; i < len; i++) {
        if (i > 0) printf(" -> ");
        printf("%d", path[i]);
    }
    printf("\n");
}

/*
 * Classic 9-vertex Kruskal/Prim textbook graph.
 *
 * Vertices: 0-8
 * Edges (undirected):
 *   0-1(4)  0-7(8)  1-2(8)  1-7(11) 2-3(7)  2-5(4)
 *   2-8(2)  3-4(9)  3-5(14) 4-5(10) 5-6(2)  6-7(1)
 *   6-8(6)  7-8(7)
 * Expected MST weight: 37
 */
static void run_demo(void)
{
    printf("=======================================================\n");
    printf("  DEMO — Classic 9-vertex textbook graph\n");
    printf("=======================================================\n\n");

    Graph *g = graph_create(9);

    graph_add_edge(g, 0, 1,  4);
    graph_add_edge(g, 0, 7,  8);
    graph_add_edge(g, 1, 2,  8);
    graph_add_edge(g, 1, 7, 11);
    graph_add_edge(g, 2, 3,  7);
    graph_add_edge(g, 2, 5,  4);
    graph_add_edge(g, 2, 8,  2);
    graph_add_edge(g, 3, 4,  9);
    graph_add_edge(g, 3, 5, 14);
    graph_add_edge(g, 4, 5, 10);
    graph_add_edge(g, 5, 6,  2);
    graph_add_edge(g, 6, 7,  1);
    graph_add_edge(g, 6, 8,  6);
    graph_add_edge(g, 7, 8,  7);

    printf("--- Graph ---\n");
    graph_print(g);
    printf("\n");

    printf("--- Kruskal MST ---\n");
    MSTResult kruskal = mst_kruskal(g);
    mst_result_print(&kruskal, "Kruskal");
    printf("  Expected MST weight: 37\n\n");

    printf("--- Prim MST (start = 0) ---\n");
    MSTResult prim = mst_prim(g, 0);
    mst_result_print(&prim, "Prim");
    printf("\n");

    if (mst_results_equal(&kruskal, &prim)) {
        printf("Kruskal and Prim produced the SAME MST weight. [OK]\n\n");
    } else {
        printf("Kruskal and Prim MST weights DIFFER.\n\n");
    }

    mst_result_free(&kruskal);
    mst_result_free(&prim);

    printf("--- Dijkstra from vertex 0 ---\n");
    SPResult sp = sp_dijkstra(g, 0);
    sp_result_print(&sp, 4);

    int path_len = 0;
    int *path = sp_reconstruct_path(&sp, 4, &path_len);
    printf("  Shortest path to vertex 4:\n");
    print_path(path, path_len);
    free(path);
    printf("\n");

    sp_result_free(&sp);

    printf("--- Dijkstra from vertex 0 (vertex 2 blocked) ---\n");
    graph_block_vertex(g, 2);

    SPResult sp_blocked = sp_dijkstra(g, 0);
    sp_result_print(&sp_blocked, 4);

    int path_blocked_len = 0;
    int *path_blocked = sp_reconstruct_path(&sp_blocked, 4, &path_blocked_len);
    printf("  Alternate path to vertex 4 (vertex 2 blocked):\n");
    print_path(path_blocked, path_blocked_len);
    free(path_blocked);
    printf("\n");

    sp_result_free(&sp_blocked);
    graph_unblock_vertex(g, 2);

    printf("--- Obstacle-aware Dijkstra from vertex 0 (with penalties) ---\n");

    graph_set_edge_penalty(g, 0, 7, 50);   /* make the 0-7 shortcut expensive */
    graph_set_edge_penalty(g, 1, 7, 30);

    SPResult sp_obs = sp_dijkstra_obstacle(g, 0);
    sp_result_print(&sp_obs, 4);

    int path_obs_len = 0;
    int *path_obs = sp_reconstruct_path(&sp_obs, 4, &path_obs_len);
    printf("  Path to vertex 4 (with penalties):\n");
    print_path(path_obs, path_obs_len);
    free(path_obs);
    printf("\n");

    sp_result_free(&sp_obs);

    graph_destroy(g);

    printf("=======================================================\n");
    printf("  DEMO complete.\n");
    printf("=======================================================\n\n");
}

static void run_mst(int vertices, double density)
{
    printf("=======================================================\n");
    printf("  MST — vertices=%d  density=%.2f\n", vertices, density);
    printf("=======================================================\n\n");

    Graph *g = gen_connected_graph(vertices, density, MAX_WEIGHT, 42);
    if (g == NULL) {
        fprintf(stderr, "Error: failed to generate graph.\n");
        return;
    }

    printf("Graph: %d vertices, %d edges\n\n", g->num_vertices, g->num_edges);

    printf("--- Kruskal MST ---\n");
    MSTResult kruskal = mst_kruskal(g);
    mst_result_print(&kruskal, "Kruskal");
    printf("\n");

    printf("--- Prim MST (start = 0) ---\n");
    MSTResult prim = mst_prim(g, 0);
    mst_result_print(&prim, "Prim");
    printf("\n");

    if (mst_results_equal(&kruskal, &prim)) {
        printf("Both algorithms produced the SAME MST weight. [OK]\n\n");
    } else {
        printf("MST weights differ between algorithms.\n\n");
    }

    mst_result_free(&kruskal);
    mst_result_free(&prim);
    graph_destroy(g);

    printf("=======================================================\n");
    printf("  MST complete.\n");
    printf("=======================================================\n\n");
}

static void run_path(int vertices, double density, int src, int target)
{
    printf("=======================================================\n");
    printf("  SHORTEST PATH — vertices=%d  density=%.2f  src=%d  target=%d\n",
           vertices, density, src, target);
    printf("=======================================================\n\n");

    Graph *g = gen_connected_graph(vertices, density, MAX_WEIGHT, 42);
    if (g == NULL) {
        fprintf(stderr, "Error: failed to generate graph.\n");
        return;
    }

    if (src < 0 || src >= g->num_vertices) {
        fprintf(stderr, "Error: src vertex %d out of range [0, %d).\n",
                src, g->num_vertices);
        graph_destroy(g);
        return;
    }
    if (target < 0 || target >= g->num_vertices) {
        fprintf(stderr, "Error: target vertex %d out of range [0, %d).\n",
                target, g->num_vertices);
        graph_destroy(g);
        return;
    }

    printf("Graph: %d vertices, %d edges\n\n", g->num_vertices, g->num_edges);

    /* Apply deterministic penalties to edges whose src is a multiple of 7. */
    for (int i = 0; i < g->num_edges; i++) {
        if (g->edge_list[i].src % 7 == 0) {
            graph_set_edge_penalty(g,
                                   g->edge_list[i].src,
                                   g->edge_list[i].dest,
                                   g->edge_list[i].weight / 2 + 1);
        }
    }

    printf("--- Dijkstra (standard) from %d ---\n", src);
    SPResult sp = sp_dijkstra(g, src);
    sp_result_print(&sp, target);

    int path_len = 0;
    int *path = sp_reconstruct_path(&sp, target, &path_len);
    printf("  Path (%d -> %d):\n", src, target);
    print_path(path, path_len);
    free(path);
    printf("\n");

    sp_result_free(&sp);

    printf("--- Dijkstra (obstacle-aware) from %d ---\n", src);
    SPResult sp_obs = sp_dijkstra_obstacle(g, src);
    sp_result_print(&sp_obs, target);

    int path_obs_len = 0;
    int *path_obs = sp_reconstruct_path(&sp_obs, target, &path_obs_len);
    printf("  Path (%d -> %d) with penalties:\n", src, target);
    print_path(path_obs, path_obs_len);
    free(path_obs);
    printf("\n");

    sp_result_free(&sp_obs);
    graph_destroy(g);

    printf("=======================================================\n");
    printf("  SHORTEST PATH complete.\n");
    printf("=======================================================\n\n");
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        print_usage();
        return 1;
    }

    const char *mode = argv[1];

    int    vertices = 100;
    double density  = 0.3;
    int    src      = 0;
    int    target   = -1;          /* resolved to vertices-1 after parsing */

    for (int i = 2; i < argc - 1; i++) {
        if (strcmp(argv[i], "-v") == 0) {
            vertices = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-d") == 0) {
            density = atof(argv[++i]);
        } else if (strcmp(argv[i], "-s") == 0) {
            src = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-t") == 0) {
            target = atoi(argv[++i]);
        }
    }

    if (target < 0)
        target = vertices - 1;

    if (strcmp(mode, "demo") == 0) {
        run_demo();
    } else if (strcmp(mode, "bench") == 0) {
        printf("=======================================================\n");
        printf("  BENCHMARK SUITE\n");
        printf("=======================================================\n\n");
        benchmark_mst_comparison();
        benchmark_sp_comparison();
        printf("=======================================================\n");
        printf("  BENCHMARK complete.\n");
        printf("=======================================================\n\n");
    } else if (strcmp(mode, "mst") == 0) {
        run_mst(vertices, density);
    } else if (strcmp(mode, "path") == 0) {
        run_path(vertices, density, src, target);
    } else {
        fprintf(stderr, "Unknown mode: %s\n\n", mode);
        print_usage();
        return 1;
    }

    return 0;
}
