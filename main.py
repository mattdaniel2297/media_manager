import argparse
import os
import UUID_namer

parser = argparse.ArgumentParser("UUID Namer")
parser.add_argument("dir", help="directory of files to rename as UUIDs")
args = parser.parse_args()

if os.path.isdir(args.dir):
    root = args.dir
    print(f"Process root {root}")
    UUID_namer.process_dir(root)
else:
    raise Exception("Root is not a valid directory")