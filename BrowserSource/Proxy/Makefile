CC := clang++

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

DEFINES :=
CFLAGS := -Wall -Wextra -std=c++20 $(DEFINES) -I$(MAKEFILE_DIR)/fmt/include
LDFLAGS := -L$(MAKEFILE_DIR)/fmt/build -lfmt -static

SRCS := $(wildcard *.cpp)

HDRS := $(wildcard *.h)

OBJS := $(SRCS:.cpp=.o)

EXE := server

.PHONY: all
all: $(EXE)

$(EXE): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

# Hack: any header change causes a full recompilation of everything.
%.o: %.cpp $(HDRS)
	$(CC) $(CFLAGS) -c -o $@ $<

.PHONY: clean
clean:
	@rm -f $(OBJS) $(EXE)

.PHONY: debug
debug:
	@echo "CC: $(CC)"
	@echo "MAKEFILE_DIR: $(MAKEFILE_DIR)"
	@echo "STT_TOP: $(STT_TOP)"
	@echo "OBJS: $(OBJS)"

