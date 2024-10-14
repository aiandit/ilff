prefix = /usr
INSTDIR = $(DESTDIR)$(prefix)

LIBNAME = ilff

sources = ilff.c

objects = $(patsubst %.c, %.o, $(sources))

DLIB_PREF = lib
DLIB_SUFF = .so
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


all: build-lib

build-lib: $(LIB) $(DLIB)

$(DLIB): $(objects)
	$(CC) $(CFLAGS) $(LDFLAGS) -shared -o $@ $^

$(LIB): $(objects)
	$(AR) r $@ $^

ilff.o: ilff.h

install: $(LIB) $(DLIB)
	install -d $(INSTDIR)/lib
	install -d $(INSTDIR)/include
	install -m 644 ilff.h $(INSTDIR)/include
	install -m 644 $(LIB) $(INSTDIR)/lib
	install -m 755 $(DLIB) $(INSTDIR)/lib

uninstall:
	rm -rf $(INSTDIR)/include/ilff.h
	rm -rf $(INSTDIR)/lib/ilff.a
	rm -rf $(INSTDIR)/lib/ilff$(DLIB_SUFF)

clean:
	rm -rf ilff.a ilff$(DLIB_SUFF) *.o
