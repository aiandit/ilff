#pragma once

#include <stdint.h>

typedef void ILFFFile;

ILFFFile *ilffOpen(char const *name, char const *mode);
int ilffClose(ILFFFile *);

int ilffWrite(ILFFFile *, char const *data, int64_t len);
int ilffWriteLine(ILFFFile *, char const *data, int64_t len);

int ilffGetLine(ILFFFile *, int64_t lnnum, char *data, int64_t *nChars);
int ilffGetLines(ILFFFile* ilff_, int64_t const lnnum, int64_t const N, char** data, int64_t* lengths, int64_t* nLines);
int ilffGetRange(ILFFFile *, int64_t const lnnum, int64_t const N, char *data, int64_t *maxLen);

int64_t ilffNLines(ILFFFile *);

int ilffReindex(ILFFFile*);
int ilffFlush(ILFFFile*);
