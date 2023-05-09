import ilff
import sys
import os

def run():
    base = sys.argv[1]

    indexDir = os.path.join(base, '.ilff-index')

    files = [f for f in os.listdir(indexDir) if os.path.isfile(os.path.join(indexDir, f))]

    for indexFile in files:
        if indexFile.endswith('.idx'):
            fullname = os.path.join(indexDir, indexFile)
            mainname = indexFile[:-4]
            if not os.path.isfile(os.path.join(base, mainname)):
                print(f'stale index {fullname}')
                os.remove(fullname)

if __name__ == "__main__":
    run()
