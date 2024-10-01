#pragma once

#include <stdint.h>

typedef void ILFFFile;

enum EILFFFlags {
  eILFFFlagNone,
  eILFFFlagCheck,
  eILFFFlagSymlinks,
};

ILFFFile *ilffOpen(char const *name, char const *mode, int flags);
int ilffClose(ILFFFile *);

int ilffWrite(ILFFFile *, char const *data, int64_t len);
int ilffWriteLine(ILFFFile *, char const *data, int64_t len);

int ilffGetLine(ILFFFile *, int64_t lnnum, char *data, int64_t *nChars);
int ilffGetLines(ILFFFile* ilff_, int64_t const lnnum, int64_t const N, char** data, int64_t* lengths);
int ilffGetRange(ILFFFile *, int64_t const lnnum, int64_t const N, char *data, int64_t *maxLen);

int ilffGetIndex(ILFFFile *, int64_t lnnum, int64_t const N, int64_t* index);

int64_t ilffNLines(ILFFFile *);

int ilffCheck(ILFFFile*);
int ilffCheckPrint(ILFFFile *ilff_, int res);

int ilffReindex(ILFFFile*);
int ilffDumpindex(ILFFFile*);
int ilffFlush(ILFFFile*);
int ilffTruncate(ILFFFile*);

int ilffRemove(char const *name);
