import argparse
import os
import UUID_namer
from catalog_utils import create_catalog
from import_media import import_media

parser = argparse.ArgumentParser("Media Importer")
parser.add_argument("--src", nargs=1, help="directory of media files to import")
parser.add_argument("--dest", nargs=1, help="directory of destination media files")
parser.add_argument("--catalog", action="store_true", help="create catalog for destination if not existing")
parser.add_argument("--remove", action="store_true", help="remove items from source")
parser.add_argument("--copyright", action="store_true", help="apply copyright to metadata")
parser.add_argument("--norename", action="store_true", help="Do not rename destination files with UUID")
args = parser.parse_args()

if os.path.isdir(args.src[0]):
    source_root = args.src[0]
    print(f"Process source {source_root}")
else:
    raise Exception("Source is not a valid directory")

if os.path.isdir(args.dest[0]):
    dest_root = args.dest[0]
    print(f"Process dest {dest_root}")
else:
    raise Exception("Destination is not a valid directory")

# print(f"Starting import of {source_root} to {dest_root})"
print(f"OPTIONS:")
print(f"     catalog is {args.catalog}")
print(f"     remove is {args.remove}")
print(f"     norename is {args.norename}")
print(f"     copyright is {args.copyright}")      

db_loc = os.path.join(dest_root, "catalog.db")
if os.path.exists(db_loc):
    print(f"Existing catalog found for destination at {db_loc}")
else:
    if args.catalog:
        create_catalog(dest_root)
    else:
        raise Exception("No catalog found for destination.")
    
import_media(source_root, 
             dest_root, 
             is_remove=args.remove, 
             catalog=args.catalog, 
             norename=args.norename, 
             is_copyright=args.copyright
             )