#include "ilff.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <libgen.h>

#include <sys/stat.h>
#include <unistd.h>

typedef int64_t ILFF_addr_t;
#define ILFF_ADDRSZ sizeof(ILFF_addr_t)

#define ILFF_INDEX_DIR ".ilff-index"
#define ILFF_INDEX_SUFF ".idx"

#define min(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a <= _b ? _a : _b; })

typedef struct {
  FILE* mainFile;
  FILE* indexFile;

  char* mainFileName;
  char* indexFileName;

  char* mode;

  ILFF_addr_t idx, nlines;

} ILFF;

static ILFF *allocILFF() {
  ILFF* ptr = calloc(sizeof(ILFF), 1);
  return ptr;
}

static int freeILFF(ILFF *ilff) {
  if (ilff->mainFileName) {
    free(ilff->mainFileName);
    ilff->mainFileName = 0;
  }
  if (ilff->indexFileName) {
    free(ilff->indexFileName);
    ilff->indexFileName = 0;
  }
  if (ilff->mode) {
    free(ilff->mode);
    ilff->mode = 0;
  }
  free(ilff);
  return 0;
}

static int closeILFF(ILFF* ilff) {
  if (ilff->mainFile) {
    fclose(ilff->mainFile);
    ilff->mainFile = 0;
  }
  if (ilff->indexFile) {
    fclose(ilff->indexFile);
    ilff->indexFile = 0;
  }
  freeILFF(ilff);
  return 0;
}

static long fileSize(FILE* file) {
  fseek(file, 0, SEEK_END);
  return ftell(file);
}

static int readint(FILE* file, ILFF_addr_t* idx) {
  char buf[ILFF_ADDRSZ];

  int rcr = fread(buf, 1, ILFF_ADDRSZ, file);

  if (rcr != ILFF_ADDRSZ) {
    fprintf(stderr,
	    "ILFF: Error: Failed to read from index file at offset %ld: %s\n",
	    ftell(file), strerror(errno));
    *idx = 0;
  } else {
    *idx = *(ILFF_addr_t*) buf;
  }

  return rcr == ILFF_ADDRSZ ? 0 : -1;
}

static int readindex(ILFF* ilff, int lnnum, ILFF_addr_t* idx1, ILFF_addr_t* idx2) {
  int rc1 = 0, rc2 = 0;

  if (lnnum > 0) {
    int rcs = fseek(ilff->indexFile, (lnnum-1)*ILFF_ADDRSZ, SEEK_SET);
    if (rcs != 0) {
      fprintf(stderr,
	      "ILFF: Error: Failed to seek in index file to %d of %ld: %s\n",
	      lnnum, fileSize(ilff->indexFile), strerror(errno));
      return -1;
    }
    rc1 = readint(ilff->indexFile, idx1);
  } else if (lnnum < 0) {
    *idx1 = 0;
    *idx2 = 0;
    return 0;
  } else {
    *idx1 = 0;
    int rcs = fseek(ilff->indexFile, lnnum*ILFF_ADDRSZ, SEEK_SET);
    if (rcs != 0) {
      fprintf(stderr,
	      "ILFF: Error: Failed to seek in index file to %d of %ld: %s\n",
	      lnnum, fileSize(ilff->indexFile), strerror(errno));
      return -1;
    }
  }

  rc2 = readint(ilff->indexFile, idx2);
  return rc1 == 0 && rc2 == 0 ? 0 : -1;
}

static int writeindex(ILFF* ilff, ILFF_addr_t idx) {
  return fwrite((char const*) &idx, 1, ILFF_ADDRSZ, ilff->indexFile);
}

static ILFF_addr_t get_nlines(ILFF* ilff) {
  return fileSize(ilff->indexFile)/ILFF_ADDRSZ;
}

static char* getIndexFileName(char const *name, int createIndexDir) {
  char* ncopy1 = strdup(name);
  char* fdir = dirname(ncopy1);

  char* ncopy2 = strdup(name);
  char* fbase = basename(ncopy2);

  int nidxLen = strlen(fdir) + sizeof(ILFF_INDEX_DIR) + 3 + strlen(fbase) + sizeof(ILFF_INDEX_SUFF);
  char* indexFileName = malloc(nidxLen);

  size_t offs = 0;

  strcpy(indexFileName, fdir);
  offs += strlen(fdir);

  indexFileName[offs] = '/';
  offs += 1;

  strcpy(indexFileName + offs, ILFF_INDEX_DIR);
  offs += sizeof(ILFF_INDEX_DIR) - 1;

  if (createIndexDir) {
    int rcmd = mkdir(indexFileName, 0755);
    if (rcmd && errno != EEXIST) {
      fprintf(stderr,
	      "ILFF: Error: Failed to create index directory %s: %s\n",
	      indexFileName, strerror(errno));
      return 0;
    }
  }

  indexFileName[offs] = '/';
  offs += 1;

  strcpy(indexFileName + offs, fbase);
  offs += strlen(fbase);

  strcpy(indexFileName + offs, ILFF_INDEX_SUFF);

  free(ncopy1);
  free(ncopy2);

  return indexFileName;
}

static char* readlinkILFF(char const *name) {
  int bufsz = 4096;
  char* namebuf = malloc(bufsz);
  ssize_t rlsz = 0;

  for (int tries = 0; tries < 5; ++tries) {
    rlsz = readlink(name, namebuf, bufsz);
    if (rlsz == -1) {
      fprintf(stderr,
	      "ILFF: Error: Failed to read link file %s: %s\n",
	      name, strerror(errno));
      free(namebuf);
      namebuf = 0;
      return 0;
    }
    if (rlsz >= bufsz) {
      bufsz *= 2;
      namebuf = realloc(namebuf, bufsz);
    } else {
      namebuf[rlsz] = 0;
      break;
    }
  }

  if (namebuf[0] == '/') {
    return namebuf;
  }

  char* name2 = strdup(name);
  char const* dname = dirname(name2);

  ssize_t offs = 0;
  char* pathbuf = malloc(rlsz + strlen(dname) + 2);

  strcpy(pathbuf, dname);
  offs += strlen(pathbuf);

  strcpy(pathbuf + offs, "/");
  offs += 1;

  strcpy(pathbuf + offs, namebuf);

  free(namebuf);
  free(name2);

  return pathbuf;
}

static ILFF* openILFF(char const *name, char const *mode, int flags) {
  ILFF *ilff = allocILFF();

  ilff->mainFileName = strdup(name);
  ilff->mode = strdup(mode);

  if (flags & eILFFFlagSymlinks) {
    char const* namebuf = name;
    struct stat stm;

    int rcst = lstat(name, &stm);
    if (rcst == 0 && S_ISLNK(stm.st_mode)) {
      namebuf = readlinkILFF(name);
      if (namebuf == 0) {
	namebuf = name;
      }
    }
    ilff->indexFileName = getIndexFileName(namebuf, 1);
    if (namebuf != name) {
      free((char*)namebuf);
    }
  } else {
    ilff->indexFileName = getIndexFileName(name, 1);
  }

  if (ilff->indexFileName == 0) {
    closeILFF(ilff);
    return 0;
  }

  char mymode[4] = {0};
  int nmode = 0;
  mymode[nmode] = mode[0];
  ++nmode;
  if (mode[1] == '+') {
    mymode[nmode] = mode[1];
    ++nmode;
  }
  mymode[nmode] = 'b';
  ++nmode;

  ilff->mainFile = fopen(ilff->mainFileName, mymode);
  if (ilff->mainFile == 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to open file %s: %s\n",
	    ilff->mainFileName, strerror(errno));
    closeILFF(ilff);
    return 0;
  }

  if (mode[0] == 'a') {
    mymode[nmode-1] = '+';
    mymode[nmode] = 'b';
  }

  ilff->indexFile = fopen(ilff->indexFileName, mymode);
  if (ilff->indexFile == 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to open index file %s: %s\n",
	    ilff->indexFileName, strerror(errno));
    closeILFF(ilff);
    return 0;
  }

  ilff->nlines = get_nlines(ilff);

  if (ilff->nlines > 0) {
    fseek(ilff->indexFile, (ilff->nlines-1)*ILFF_ADDRSZ, SEEK_SET);
    readint(ilff->indexFile, &ilff->idx);
  }

  if (flags & eILFFFlagCheck) {
    int res = ilffCheck(ilff);
    ilffCheckPrint(ilff, res);
  }

  return ilff;
}

ILFFFile* ilffOpen(char const *name, char const *mode, int flags) {
  ILFF* ilff = openILFF(name, mode, flags);
  return ilff;
}

int ilffClose(ILFFFile *ilff_) {
  ILFF* ilff = (ILFF*) ilff_;
  return closeILFF(ilff);
}

int ilffWrite(ILFFFile *ilff_, char const *data, int64_t len) {
  return ilffWriteLine(ilff_, data, len);
}

int ilffWriteLine(ILFFFile* ilff_, char const *data, int64_t len) {
  ILFF* ilff = (ILFF*) ilff_;

  fwrite(data, 1, len, ilff->mainFile);

  if (data[len-1] != '\n') {
    fputc('\n', ilff->mainFile);
    ++len;
  }

  ilff->idx = ilff->idx + len;
  writeindex(ilff, ilff->idx);

  ++ilff->nlines;
  return 0;
}

int ilffGetLine(ILFFFile* ilff_, int64_t lnnum, char*data, int64_t* nChars) {
  ILFF* ilff = (ILFF*) ilff_;

  if (nChars == 0) return -1;

  ILFF_addr_t idx1, idx2;
  int rci = readindex(ilff, lnnum, &idx1, &idx2);
  if (rci != 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to read index for line %ld: %s\n",
	    lnnum, strerror(errno));
    *nChars = 0;
    return -1;
  }

  int64_t const dlen = idx2 - idx1;

  if (data == 0) {
    *nChars = dlen;
    return 0;
  }

  int64_t const rlen = min(*nChars, dlen);

  fseek(ilff->mainFile, idx1, SEEK_SET);

  size_t nrd = fread(data, 1, rlen, ilff->mainFile);
  *nChars = nrd;

  return 0;
}

int ilffGetLines(ILFFFile* ilff_, int64_t const lnnum, int64_t const N, char** data, int64_t* lengths) {
  ILFF* ilff = (ILFF*) ilff_;

  if (lengths == 0) return -1;

  int res = 0;

  ILFF_addr_t* index = malloc((N + 1)*ILFF_ADDRSZ);

  int rci = 0;
  if (lnnum > 0) {
    rci = ilffGetIndex(ilff_, lnnum-1, N+1, index);
  } else {
    index[0] = 0;
    rci = ilffGetIndex(ilff_, lnnum, N, index + 1);
  }
  if (rci != 0) {
    free(index);
    return -1;
  }

  if (data == 0) {
    for (int64_t i = 0; i < N; ++i) {
      lengths[i] = index[i+1] - index[i];
    }
    free(index);
    return 0;
  }

  int rcr = 0, rcs = 0;
  rcs = fseek(ilff->mainFile, index[0], SEEK_SET);
  if (rcs != 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to seek file to %ld at line %ld: %s\n",
	    index[0], lnnum, strerror(errno));
    return -1;
  }


  for (int64_t i = 0; i < N; ++i) {

    int64_t const dlen = index[i+1] - index[i];
    int64_t const rlen = min(lengths[i], dlen);

    rcr = fread(data[i], 1, rlen, ilff->mainFile);
    lengths[i] = rcr;

    if (rcr != rlen) {
      fprintf(stderr,
	      "ILFF: Error: Failed to read file at line %ld: %s\n",
	      lnnum + i, strerror(errno));
      res = -1;
      break;
    }

    if (rcr < dlen) {
      rcs = fseek(ilff->mainFile, index[i], SEEK_SET);
      if (rcs != 0) {
	fprintf(stderr,
		"ILFF: Error: Failed to seek file to %ld at line %ld: %s\n",
		index[i], lnnum, strerror(errno));
	return -1;
      }
    }

  }

  free(index);
  return res;
}

int ilffGetRange(ILFFFile *ilff_, int64_t lnnum, int64_t N, char* data, int64_t* nChars) {
  ILFF* ilff = (ILFF*) ilff_;

  if (nChars == 0) return -1;

  ILFF_addr_t idx1, idx2;
  ILFF_addr_t idx3, idx4;

  readindex(ilff, lnnum,         &idx1, &idx2);
  readindex(ilff, lnnum + N - 1, &idx3, &idx4);

  int64_t const dlen = idx4 - idx1;

  if (data == 0) {
    *nChars = dlen;
    return 0;
  }

  int64_t const rlen = min(*nChars, dlen);

  int rcs = fseek(ilff->mainFile, idx1, SEEK_SET);
  if (rcs != 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to seek file to %ld at line %ld: %s\n",
	    idx1, lnnum, strerror(errno));
    return -1;
  }

  size_t rcr = fread(data, 1, rlen, ilff->mainFile);
  *nChars = rcr;

  return 0;
}

int ilffGetIndex(ILFFFile* ilff_, int64_t lnnum, int64_t const N, int64_t* index) {
  ILFF* ilff = (ILFF*) ilff_;

  if (lnnum < 0 || N < 0 || index == 0) {
    return -1;
  }

  int rcs = fseek(ilff->indexFile, lnnum*ILFF_ADDRSZ, SEEK_SET);
  if (rcs != 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to seek index file to offset %ld: %s\n",
	    lnnum*ILFF_ADDRSZ, strerror(errno));
    return -2;
  }

  int rcr = fread(index, ILFF_ADDRSZ, N, ilff->indexFile);
  if (rcr != N) {
    fprintf(stderr,
	    "ILFF: Error: Failed to read from index file at offset %ld: %s\n",
	    ftell(ilff->indexFile), strerror(errno));
    return rcr;
  }

  return 0;
}

int64_t ilffNLines(ILFFFile* ilff_) {
  ILFF* ilff = (ILFF*) ilff_;
  return get_nlines(ilff);
}

#define getTime(tv) (tv.tv_sec + 1e-9 * tv.tv_nsec)

int ilffCheck(ILFFFile *ilff_) {
  ILFF* ilff = (ILFF*) ilff_;

  int res = 0;
  struct stat stf, sti;

  fstat(fileno(ilff->mainFile), &stf);
  fstat(fileno(ilff->indexFile), &sti);
  if (getTime(stf.st_mtim) - getTime(sti.st_mtim) > 2) {
    res |= 1;
  }

  if (ilff->idx != stf.st_size) {
    res |= 2;
  }

  return res;
}

int ilffCheckPrint(ILFFFile *ilff_, int res) {
  ILFF* ilff = (ILFF*) ilff_;
  if (res & 1) {
    fprintf(stderr, "Warning: index file is outdated, consider reindexing %s\n", ilff->mainFileName);
  }
  if (res & 2) {
    fprintf(stderr, "Main file is larger than last index. consider reindexing %s\n", ilff->mainFileName);
  }
  return 0;
}

int ilffReindex(ILFFFile *ilff_) {
  ILFF* ilff = (ILFF*) ilff_;

  int rcs2 = fseek(ilff->indexFile, 0, SEEK_SET);
  int rct2 = ftruncate(fileno(ilff->indexFile), 0);

  int rcs1 = fseek(ilff->mainFile, 0, SEEK_SET);

  if (!(rcs1 == 0 && rcs2 == 0 && rct2 == 0)) {
    return -1;
  }

  ilff->nlines = 0;
  ilff->idx = 0;

  size_t nbuf = 256;
  ssize_t nrd = 0;
  char *buffer = malloc(nbuf);

  while (1) {
    nrd = getline(&buffer, &nbuf, ilff->mainFile);
    if (nrd <= 0) {
      break;
    }
    ++ilff->nlines;
    ilff->idx += nrd;
    writeindex(ilff, ilff->idx);
    if (buffer[nrd-1] != '\n') {
      break;
    }
  }

  free(buffer);

  return 0;
}

int ilffDumpindex(ILFFFile *ilff_) {
  ILFF* ilff = (ILFF*) ilff_;

  ILFF_addr_t ln = 0, idx1 = 0, idx2 = 0, n = 0;

  n = get_nlines(ilff);

  fseek(ilff->indexFile, 0, SEEK_SET);

  for ( ; ln < n; ++ln) {
    idx1 = idx2;
    readint(ilff->indexFile, &idx2);
    fprintf(stdout, "%ld: %ld - %ld (%ld)\n", ln, idx1, idx2, idx2 - idx1);
  }

  return 0;
}

int ilffTruncate(ILFFFile* ilff_) {
  ILFF* ilff = (ILFF*) ilff_;
  int rcs1 = fseek(ilff->mainFile, 0, SEEK_SET);
  int rct1 = ftruncate(fileno(ilff->mainFile), 0);
  int rcs2 = fseek(ilff->indexFile, 0, SEEK_SET);
  int rct2 = ftruncate(fileno(ilff->indexFile), 0);
  ilff->nlines = 0;
  ilff->idx = 0;
  return rcs1 == 0 && rcs2 == 0 && rct1 == 0 && rct2 == 0 ? 0 : -1;
}

int ilffFlush(ILFFFile* ilff_) {
  ILFF* ilff = (ILFF*) ilff_;
  fflush(ilff->mainFile);
  fflush(ilff->indexFile);
  return 0;
}

int ilffRemove(char const* name) {
  char* indexFileName = getIndexFileName(name, 0);

  int rc1 = unlink(name);
  int rc2 = unlink(indexFileName);

  free(indexFileName);

  return rc1 == 0 && rc2 == 0 ? 0 : -1;
}
