#ifndef SHORTEST_PATH_H
#define SHORTEST_PATH_H

#include "graph.h"

typedef struct {
    int  *dist;
    int  *prev;
    int   source;
    int   target;
    int   num_vertices;
    bool  target_reached;
    long  time_us;
} SPResult;

SPResult sp_dijkstra(const Graph *g, int source);
SPResult sp_dijkstra_obstacle(const Graph *g, int source);
void     sp_result_free(SPResult *r);
void     sp_result_print(const SPResult *r, int target);
int     *sp_reconstruct_path(const SPResult *r, int target, int *path_len);

#endif /* SHORTEST_PATH_H */
