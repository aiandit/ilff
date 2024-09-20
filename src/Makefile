prefix = /usr
INSTDIR = $(DESTDIR)$(prefix)

LIBNAME = ilff

sources = ilff.c

objects = $(patsubst %.c, %.o, $(sources))

LIB = $(LIBNAME).a
DLIB = $(LIBNAME).so

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
	rm -rf $(INSTDIR)/lib/ilff.so
