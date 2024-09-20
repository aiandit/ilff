LIBNAME = ilff

sources = ilff.c

objects = $(patsubst %.c, %.o, $(sources))

LIB = $(LIBNAME).a
DLIB = $(LIBNAME).so

CFLAGS += -Wall -Wextra


all: build-lib

build-lib: $(LIB) $(DLIB)

$(DLIB): $(objects)
	$(CC) $(CFLAGS) $(LDFLAGS) -shared -o $@ $^

$(LIB): $(objects)
	$(AR) r $@ $^

ilff.o: ilff.h

PREFIX = /usr

install: $(LIB) $(DLIB)
	install -m 644 ilff.h $(PREFIX)/include
	install -m 644 $(LIB) $(PREFIX)/lib
	install -m 755 $(DLIB) $(PREFIX)/lib
