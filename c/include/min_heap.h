#ifndef MIN_HEAP_H
#define MIN_HEAP_H

#include <stdbool.h>

typedef struct {
    int key;
    int value;
} HeapNode;

typedef struct {
    HeapNode *data;
    int       size;
    int       capacity;
    int      *pos;
} MinHeap;

MinHeap *heap_create(int capacity);
void     heap_destroy(MinHeap *h);
void     heap_insert(MinHeap *h, int key, int value);
HeapNode heap_extract_min(MinHeap *h);
void     heap_decrease_key(MinHeap *h, int value, int new_key);
bool     heap_is_empty(MinHeap *h);
bool     heap_contains(MinHeap *h, int value);

#endif /* MIN_HEAP_H */
