#ifndef BENCHMARK_H
#define BENCHMARK_H

#include "graph.h"

typedef struct {
    long time_us;
    int  total_weight;
    bool success;
} BenchmarkResult;

BenchmarkResult bench_kruskal(Graph *g);
BenchmarkResult bench_prim(Graph *g, int start);
BenchmarkResult bench_dijkstra(Graph *g, int src, int dest);
BenchmarkResult bench_dijkstra_obstacle(Graph *g, int src, int dest);

void benchmark_mst_comparison(void);
void benchmark_sp_comparison(void);

#endif /* BENCHMARK_H */
