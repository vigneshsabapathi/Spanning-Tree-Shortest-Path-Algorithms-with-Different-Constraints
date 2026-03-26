#ifndef MST_H
#define MST_H

#include "graph.h"

typedef struct {
    Edge *edges;
    int   num_edges;
    int   total_weight;
    bool  is_connected;
    long  time_us;
} MSTResult;

MSTResult mst_kruskal(const Graph *g);
MSTResult mst_prim(const Graph *g, int start_vertex);
void      mst_result_free(MSTResult *r);
void      mst_result_print(const MSTResult *r, const char *label);
bool      mst_results_equal(const MSTResult *a, const MSTResult *b);

#endif /* MST_H */
