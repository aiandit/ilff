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

static char* getIndexFileName(char const *name, int createIndexDir) {
  char* ncopy1 = strdup(name);
  char* fdir = dirname(ncopy1);

  char* ncopy2 = strdup(name);
  char* fbase = basename(ncopy2);

  char* indexFileName = (char*) malloc(strlen(fdir) + sizeof(ILFF_INDEX_DIR) + 3 + strlen(fbase) + sizeof(ILFF_INDEX_SUFF));

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

static ILFF *openILFF(char const *name, char const *mode) {
  ILFF *ilff = allocILFF();

  ilff->mainFileName = strdup(name);
  ilff->mode = strdup(mode);
  ilff->indexFileName = getIndexFileName(name, 1);
  if (ilff->indexFileName == 0) {
    closeILFF(ilff);
    return 0;
  }

  char mymode[3] = {'r', 'b', 0};
  mymode[0]= mode[0];

  ilff->mainFile = fopen(ilff->mainFileName, mymode);
  if (ilff->mainFile == 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to open file %s: %s\n",
	    ilff->mainFileName, strerror(errno));
    closeILFF(ilff);
    return 0;
  }

  ilff->indexFile = fopen(ilff->indexFileName, mymode);
  if (ilff->indexFile == 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to open index file %s: %s\n",
	    ilff->indexFileName, strerror(errno));
    closeILFF(ilff);
    return 0;
  }

  return ilff;
}

ILFFFile* ilffOpen(char const *name, char const *mode) {
  ILFF* ilff = openILFF(name, mode);
  return ilff;
}

int ilffClose(ILFFFile *ilff_) {
  ILFF* ilff = (ILFF*) ilff_;
  return closeILFF(ilff);
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

  return rcr;
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
  struct stat st;
  int rcs = fstat(fileno(ilff->indexFile), &st);
  if (rcs != 0) {
    fprintf(stderr,
	    "ILFF: Error: Failed to stat index file %s: %s\n",
	    ilff->indexFileName, strerror(errno));
    return 0;
  }
  return st.st_size/ILFF_ADDRSZ;
}

int ilffWrite(ILFFFile *ilff_, char const *data, int64_t len) {
  return ilffWriteLine(ilff_, data, len);
}

int ilffWriteLine(ILFFFile* ilff_, char const *data, int64_t len) {
  ILFF* ilff = (ILFF*) ilff_;

  if (data[len-1] == '\n') {
    --len;
  }

  fwrite(data, 1, len, ilff->mainFile);
  fputc('\n', ilff->mainFile);

  ilff->idx = ilff->idx + len + 1;
  writeindex(ilff, ilff->idx);

  ++ilff->nlines;
  return 0;
}

int ilffGetLine(ILFFFile* ilff_, int64_t lnnum, char*data, int64_t* nChars) {
  ILFF* ilff = (ILFF*) ilff_;

  if (nChars == 0) return -1;

  ILFF_addr_t idx1, idx2;
  readindex(ilff, lnnum, &idx1, &idx2);

  int64_t const dlen = idx2 - idx1 - 1;

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

int ilffGetLines(ILFFFile* ilff_, int64_t const lnnum, int64_t const N, char** data, int64_t* lengths, int64_t* nLines) {

  if (data == 0) return -1;
  if (nLines == 0) return -1;
  if (lengths == 0) return -1;

  int64_t i = 0, offs = lnnum;

  for ( ; i < N; ++i) {
    if (*data == 0) {
      break;
    }

    int rcl = ilffGetLine(ilff_, offs, data[i], lengths + i);

    if (rcl != 0) {
      break;
    }
  }

  *nLines = i;
  return 0;
}

int ilffGetRange(ILFFFile *ilff_, int64_t lnnum, int64_t N, char* data, int64_t* nChars) {
  ILFF* ilff = (ILFF*) ilff_;

  if (nChars == 0) return -1;

  ILFF_addr_t idx1, idx2;
  readindex(ilff, lnnum - 1, &idx1, &idx2);

  ILFF_addr_t idx3, idx4;
  readindex(ilff, lnnum + N - 1, &idx3, &idx4);

  int64_t const dlen = idx4 - idx1 - 1;

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

int64_t ilffNLines(ILFFFile* ilff_) {
  ILFF* ilff = (ILFF*) ilff_;
  return get_nlines(ilff);
}

int ilffReindex(ILFFFile *ilff_) {
  ILFF* ilff = (ILFF*) ilff_;
  return 0;
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
