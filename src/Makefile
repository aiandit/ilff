HOSTTYPE ?= $(shell uname -m)

prefix = /usr
INSTDIR = $(DESTDIR)$(prefix)
LIBDIR = $(INSTDIR)/lib/$(HOSTTYPE)-linux-gnu
INCDIR = $(INSTDIR)/include

LIBNAME = ilff

sources = ilff.c

objects = $(patsubst %.c, %.o, $(sources))

VERSION = $(shell ./getversion.sh)

DLIB_PREF = lib
DLIB_SUFF = .so.$(VERSION)
ifeq ($(OS),Windows_NT)
DLIB_PREF =
DLIB_SUFF = .dll
endif

LIB = $(DLIB_PREF)$(LIBNAME).a
DLIB = $(DLIB_PREF)$(LIBNAME)$(DLIB_SUFF)

ifeq ($(CFLAGS),)
CFLAGS = -O3
endif
CFLAGS += -Wall -Wextra -fPIC

ifneq ($(OS),Windows_NT)
LDFLAGS += -Wl,-soname,libilff.so.0
endif

all: build-lib

build-lib: $(LIB) $(DLIB)

$(DLIB): $(objects)
	$(CC) $(CFLAGS) $(LDFLAGS) -shared -o $@ $^
ifneq ($(OS),Windows_NT)
	ln -sfT $(DLIB)      libilff.so.0
	ln -sfT libilff.so.0 libilff.so
endif

$(LIB): $(objects)
	$(AR) r $@ $^

ilff.o: ilff.h

install: $(LIB) $(DLIB)
	install -d $(LIBDIR)
	install -d $(INCDIR)
	install -m 644 ilff.h $(INCDIR)
	install -m 644 $(LIB) $(LIBDIR)
	install -m 755 $(DLIB) $(LIBDIR)
ifneq ($(OS),Windows_NT)
	install -m 755 libilff.so libilff.so.0 $(LIBDIR)
endif

uninstall:
	rm -rf $(INSTDIR)/include/ilff.h
	rm -rf $(LIBDIR)/ilff.a
	rm -rf $(LIBDIR)/ilff$(DLIB_SUFF)
ifneq ($(OS),Windows_NT)
	rm -rf $(LIBDIR)/libilff.so $(LIBDIR)/libilff.so.0
endif

clean:
	rm -rf libilff.* *.o
