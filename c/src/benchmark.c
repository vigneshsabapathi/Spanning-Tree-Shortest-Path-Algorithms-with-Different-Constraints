#define _POSIX_C_SOURCE 199309L
#include "benchmark.h"
#include "mst.h"
#include "shortest_path.h"
#include "graph_gen.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/* ---------------------------------------------------------------------------
 * Helper
 * ------------------------------------------------------------------------- */

static long get_time_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long)ts.tv_sec * 1000000L + (long)(ts.tv_nsec / 1000L);
}

/* ---------------------------------------------------------------------------
 * Individual benchmark functions
 * ------------------------------------------------------------------------- */

BenchmarkResult bench_kruskal(Graph *g)
{
    long start = get_time_us();
    MSTResult r = mst_kruskal(g);
    long end = get_time_us();

    BenchmarkResult br;
    br.time_us      = end - start;
    br.total_weight = r.total_weight;
    br.success      = r.is_connected;

    mst_result_free(&r);
    return br;
}

BenchmarkResult bench_prim(Graph *g, int start)
{
    long t0 = get_time_us();
    MSTResult r = mst_prim(g, start);
    long t1 = get_time_us();

    BenchmarkResult br;
    br.time_us      = t1 - t0;
    br.total_weight = r.total_weight;
    br.success      = r.is_connected;

    mst_result_free(&r);
    return br;
}

BenchmarkResult bench_dijkstra(Graph *g, int src, int dest)
{
    long t0 = get_time_us();
    SPResult r = sp_dijkstra(g, src);
    long t1 = get_time_us();

    BenchmarkResult br;
    br.time_us      = t1 - t0;
    br.total_weight = (r.dist[dest] != INF) ? r.dist[dest] : -1;
    br.success      = (r.dist[dest] != INF);

    sp_result_free(&r);
    return br;
}

BenchmarkResult bench_dijkstra_obstacle(Graph *g, int src, int dest)
{
    long t0 = get_time_us();
    SPResult r = sp_dijkstra_obstacle(g, src);
    long t1 = get_time_us();

    BenchmarkResult br;
    br.time_us      = t1 - t0;
    br.total_weight = (r.dist[dest] != INF) ? r.dist[dest] : -1;
    br.success      = (r.dist[dest] != INF);

    sp_result_free(&r);
    return br;
}

/* ---------------------------------------------------------------------------
 * MST comparison suite
 * ------------------------------------------------------------------------- */

void benchmark_mst_comparison(void)
{
    typedef struct { int V; double density; } MSTConfig;

    static const MSTConfig configs[] = {
        { 50,   0.10 },
        { 50,   0.80 },
        { 1000, 0.05 },
        { 500,  0.50 },
    };
    static const int NUM_CONFIGS = (int)(sizeof configs / sizeof configs[0]);
    static const int RUNS = 5;

    for (int c = 0; c < NUM_CONFIGS; c++) {
        int    V       = configs[c].V;
        double density = configs[c].density;

        Graph *g = gen_connected_graph(V, density, 1000, (unsigned int)(42 + c));

        long  kruskal_time_sum   = 0;
        long  prim_time_sum      = 0;
        int   kruskal_weight     = 0;
        int   prim_weight        = 0;

        for (int i = 0; i < RUNS; i++) {
            BenchmarkResult kr = bench_kruskal(g);
            BenchmarkResult pr = bench_prim(g, 0);

            kruskal_time_sum += kr.time_us;
            prim_time_sum    += pr.time_us;

            /* capture weight from last run (deterministic) */
            kruskal_weight = kr.total_weight;
            prim_weight    = pr.total_weight;
        }

        long kruskal_avg = kruskal_time_sum / RUNS;
        long prim_avg    = prim_time_sum    / RUNS;

        printf("\n=== MST Benchmark: V=%d, density=%.2f ===\n", V, density);
        printf("%-11s| %12s | %15s\n", "Algorithm", "Total Weight", "Avg Time (us)");
        printf("-----------|--------------|---------------\n");
        printf("%-11s| %12d  | %15ld\n", "Kruskal", kruskal_weight, kruskal_avg);
        printf("%-11s| %12d  | %15ld\n", "Prim",    prim_weight,    prim_avg);

        if (kruskal_weight == prim_weight) {
            printf("[OK] Both algorithms produced the same total weight: %d\n",
                   kruskal_weight);
        } else {
            printf("[WARN] Weight mismatch: Kruskal=%d  Prim=%d\n",
                   kruskal_weight, prim_weight);
        }

        graph_destroy(g);
    }
}

/* ---------------------------------------------------------------------------
 * Shortest-path comparison suite
 * ------------------------------------------------------------------------- */

void benchmark_sp_comparison(void)
{
    typedef struct { int V; double density; } SPConfig;

    static const SPConfig configs[] = {
        { 100,  0.10 },
        { 500,  0.20 },
        { 1000, 0.05 },
    };
    static const int NUM_CONFIGS = (int)(sizeof configs / sizeof configs[0]);

    for (int c = 0; c < NUM_CONFIGS; c++) {
        int    V       = configs[c].V;
        double density = configs[c].density;

        Graph *g = gen_connected_graph(V, density, 1000, (unsigned int)(99 + c));

        int src  = 0;
        int dest = V - 1;

        /* Set penalties on ~20 % of edges before running the obstacle variant.
         * We iterate over the edge_list directly and tag every 5th edge. */
        int num_edges = g->num_edges;
        int step      = (num_edges >= 5) ? (num_edges / (num_edges / 5)) : 1;
        /* simpler: tag every edge whose index % 5 == 0 */
        for (int e = 0; e < num_edges; e += 5) {
            Edge *edge = &g->edge_list[e];
            /* penalty between 3 and 5 */
            int penalty = 3 + (e % 3);   /* cycles 3,4,5,3,4,5,... */
            graph_set_edge_penalty(g, edge->src, edge->dest, penalty);
        }
        (void)step; /* suppress unused-variable warning */

        BenchmarkResult dr  = bench_dijkstra(g, src, dest);
        BenchmarkResult dro = bench_dijkstra_obstacle(g, src, dest);

        printf("\n=== SP Benchmark: V=%d, density=%.2f, src=%d, dest=%d ===\n",
               V, density, src, dest);
        printf("%-20s| %10s | %12s | %15s\n",
               "Algorithm", "Distance", "Path Exists", "Time (us)");
        printf("--------------------|------------|--------------|---------------\n");
        printf("%-20s| %10d | %12s | %15ld\n",
               "Dijkstra",
               dr.total_weight,
               dr.success ? "yes" : "no",
               dr.time_us);
        printf("%-20s| %10d | %12s | %15ld\n",
               "Dijkstra+Obstacle",
               dro.total_weight,
               dro.success ? "yes" : "no",
               dro.time_us);

        graph_destroy(g);
    }
}
