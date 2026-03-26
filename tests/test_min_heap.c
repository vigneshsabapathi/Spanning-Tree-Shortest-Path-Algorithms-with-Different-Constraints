#include <stdio.h>
#include <stdlib.h>
#include "min_heap.h"

#define ASSERT(cond, msg) do { if (!(cond)) { fprintf(stderr, "FAIL [%s:%d]: %s\n", __FILE__, __LINE__, msg); exit(1); } } while(0)
#define PASS(msg) printf("PASS: %s\n", msg)

int main(void) {
    /* Create heap with capacity 10 */
    MinHeap *h = heap_create(10);
    ASSERT(h != NULL, "heap_create returned NULL");
    PASS("heap_create capacity 10");

    /* Insert keys: 5,3,8,1,4 with values 0,1,2,3,4 */
    heap_insert(h, 5, 0);
    heap_insert(h, 3, 1);
    heap_insert(h, 8, 2);
    heap_insert(h, 1, 3);
    heap_insert(h, 4, 4);
    ASSERT(!heap_is_empty(h), "heap should not be empty after inserts");
    PASS("inserted 5 elements");

    /* Extract min: verify key==1, value==3 */
    HeapNode n1 = heap_extract_min(h);
    ASSERT(n1.key == 1,   "first extract_min key should be 1");
    ASSERT(n1.value == 3, "first extract_min value should be 3");
    PASS("extract_min: key==1, value==3");

    /* Extract min: verify key==3, value==1 */
    HeapNode n2 = heap_extract_min(h);
    ASSERT(n2.key == 3,   "second extract_min key should be 3");
    ASSERT(n2.value == 1, "second extract_min value should be 1");
    PASS("extract_min: key==3, value==1");

    /* Test contains: value 0 still in heap, value 3 was extracted */
    ASSERT(heap_contains(h, 0) == true,  "value 0 should still be in heap");
    ASSERT(heap_contains(h, 3) == false, "value 3 was extracted, should not be in heap");
    PASS("contains: value 0 present, value 3 absent");

    /* decrease_key: decrease value 2's key from 8 to 2, extract min, verify key==2, value==2 */
    heap_decrease_key(h, 2, 2);
    HeapNode n3 = heap_extract_min(h);
    ASSERT(n3.key == 2,   "after decrease_key, extract_min key should be 2");
    ASSERT(n3.value == 2, "after decrease_key, extract_min value should be 2");
    PASS("decrease_key then extract_min: key==2, value==2");

    /* Extract remaining elements, verify ascending order */
    int prev_key = n3.key; /* 2, already extracted */
    (void)prev_key;
    prev_key = 2;
    while (!heap_is_empty(h)) {
        HeapNode nx = heap_extract_min(h);
        ASSERT(nx.key >= prev_key, "remaining extractions should be in ascending key order");
        prev_key = nx.key;
    }
    PASS("remaining extractions in ascending key order");

    /* Destroy heap */
    heap_destroy(h);
    PASS("heap_destroy completed");

    return 0;
}
