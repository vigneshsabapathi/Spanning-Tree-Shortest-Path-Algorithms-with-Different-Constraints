#ifndef GRAPH_GEN_H
#define GRAPH_GEN_H

#include "graph.h"

Graph *gen_random_graph(int num_vertices, double density, int max_weight, unsigned int seed);
Graph *gen_connected_graph(int num_vertices, double density, int max_weight, unsigned int seed);
Graph *gen_grid_graph(int rows, int cols, int max_weight, unsigned int seed);
Graph *gen_obstacle_graph(int rows, int cols, double obstacle_fraction, int max_weight, unsigned int seed);

#endif /* GRAPH_GEN_H */
