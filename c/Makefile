CC      = gcc
CFLAGS  = -Wall -Wextra -Wpedantic -std=c11 -Iinclude
DBGFLAGS= -g -O0 -DDEBUG
RELFLAGS= -O2 -DNDEBUG

SRCDIR  = src
INCDIR  = include
TESTDIR = tests
OBJDIR  = obj
BINDIR  = bin

SRCS    = $(SRCDIR)/graph.c $(SRCDIR)/union_find.c $(SRCDIR)/min_heap.c \
          $(SRCDIR)/mst_kruskal.c $(SRCDIR)/mst_prim.c \
          $(SRCDIR)/sp_dijkstra.c $(SRCDIR)/sp_dijkstra_obstacle.c \
          $(SRCDIR)/graph_gen.c $(SRCDIR)/benchmark.c

OBJS    = $(SRCS:$(SRCDIR)/%.c=$(OBJDIR)/%.o)
MAIN_OBJ = $(OBJDIR)/main.o
TARGET   = $(BINDIR)/algo

TEST_SRCS = $(wildcard $(TESTDIR)/test_*.c)
TEST_BINS = $(TEST_SRCS:$(TESTDIR)/%.c=$(BINDIR)/%)

.PHONY: all debug release clean test check dirs

all: release

release: CFLAGS += $(RELFLAGS)
release: dirs $(TARGET)

debug: CFLAGS += $(DBGFLAGS)
debug: dirs $(TARGET)

dirs:
	@mkdir -p $(OBJDIR) $(BINDIR)

$(TARGET): $(OBJS) $(MAIN_OBJ)
	$(CC) $(CFLAGS) $^ -o $@

$(OBJDIR)/%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

$(BINDIR)/test_%: $(TESTDIR)/test_%.c $(OBJS)
	$(CC) $(CFLAGS) $^ -o $@

test: debug $(TEST_BINS)
	@echo "=== Running all tests ==="
	@for t in $(TEST_BINS); do echo "--- $$t ---"; $$t || exit 1; done
	@echo "=== All tests passed ==="

check: test

clean:
	rm -rf $(OBJDIR) $(BINDIR)
