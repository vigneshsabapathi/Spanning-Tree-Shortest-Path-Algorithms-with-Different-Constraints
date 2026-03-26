#include <stdio.h>
#include <stdlib.h>
#include "min_heap.h"

/* ---------- static helpers ---------- */

static void swap(MinHeap *h, int i, int j) {
    HeapNode tmp = h->data[i];
    h->data[i]   = h->data[j];
    h->data[j]   = tmp;

    h->pos[h->data[i].value] = i;
    h->pos[h->data[j].value] = j;
}

static void sift_up(MinHeap *h, int i) {
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (h->data[i].key < h->data[parent].key) {
            swap(h, i, parent);
            i = parent;
        } else {
            break;
        }
    }
}

static void sift_down(MinHeap *h, int i) {
    while (1) {
        int left     = 2 * i + 1;
        int right    = 2 * i + 2;
        int smallest = i;

        if (left < h->size && h->data[left].key < h->data[smallest].key)
            smallest = left;

        if (right < h->size && h->data[right].key < h->data[smallest].key)
            smallest = right;

        if (smallest != i) {
            swap(h, i, smallest);
            i = smallest;
        } else {
            break;
        }
    }
}

/* ---------- public API ---------- */

MinHeap *heap_create(int capacity) {
    MinHeap *h = malloc(sizeof(MinHeap));
    if (!h) { fprintf(stderr, "heap_create: malloc failed\n"); exit(1); }

    h->data = malloc(sizeof(HeapNode) * capacity);
    if (!h->data) { fprintf(stderr, "heap_create: malloc failed\n"); exit(1); }

    h->pos = malloc(sizeof(int) * capacity);
    if (!h->pos) { fprintf(stderr, "heap_create: malloc failed\n"); exit(1); }

    for (int i = 0; i < capacity; i++)
        h->pos[i] = -1;

    h->size     = 0;
    h->capacity = capacity;
    return h;
}

void heap_destroy(MinHeap *h) {
    if (!h) return;
    free(h->data);
    free(h->pos);
    free(h);
}

void heap_insert(MinHeap *h, int key, int value) {
    int idx          = h->size;
    h->data[idx].key   = key;
    h->data[idx].value = value;
    h->pos[value]      = idx;
    h->size++;
    sift_up(h, idx);
}

HeapNode heap_extract_min(MinHeap *h) {
    HeapNode min = h->data[0];

    int last = h->size - 1;
    swap(h, 0, last);
    h->size--;

    /* mark extracted value as not present */
    h->pos[min.value] = -1;

    if (h->size > 0)
        sift_down(h, 0);

    return min;
}

void heap_decrease_key(MinHeap *h, int value, int new_key) {
    int idx          = h->pos[value];
    h->data[idx].key = new_key;
    sift_up(h, idx);
}

bool heap_is_empty(MinHeap *h) {
    return h->size == 0;
}

bool heap_contains(MinHeap *h, int value) {
    return value >= 0 && value < h->capacity && h->pos[value] != -1;
}
