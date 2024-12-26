import sqlite3
import os
import shutil
import fnmatch
from cksum import get_file_cksum
from UUID_namer import is_file_valid_uuid, process_file
from catalog_utils import create_db
from metadata_tools import get_create_time, get_modified_time, add_copyright_metadata


def update_catalog_item(file):
    None


def import_media(src, dest, catalog=False, is_remove=True, norename=False, is_copyright=False):
    print(f"Starting import of {src} to {dest} with remove {is_remove}")
    db_loc = os.path.join(dest, "catalog.db")
    if not os.path.exists(db_loc):
        if catalog:
            create_db(dest)
        else:
            raise Exception(f"No catalog found at destination {dest}")
    
    con = sqlite3.connect(db_loc)
    cur = con.cursor()
    
    count = 0
    for root, directory, files in os.walk(src):
        # Just image processing for now
        # for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp', 'mp4', 'webm', 'avi', 'mov', 'wmv', 'ogg', 'mkv']:
        directory[:] = [d for d in directory if not d[0] == '.']
        files[:] = [f for f in files if not f[0] == '.']
        for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp']:
            for filename in fnmatch.filter(files, '*.' + extension):
                file = os.path.join(root, filename)
                # print(root, filename)
                print(f"Root: {root} Directory: {directory}")
                cksum = get_file_cksum(file)
                size_bytes = os.path.getsize(file)
                created_ts = get_create_time(file)
                created_year = created_ts.strftime("%Y")
                created_month = created_ts.strftime("%m")
                modified_ts = get_modified_time(file)

                uuid_name = process_file(file, rename_source=False)
                dest_dir = os.path.join(dest, created_year, created_month)
                os.makedirs(dest_dir, exist_ok=True)
                new_filename = filename

                data = (uuid_name, filename, cksum, cksum, os.path.abspath(dest_dir), size_bytes, created_ts, modified_ts)
                try:
                    cur.execute("insert into item VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
                    count += 1
                except sqlite3.IntegrityError as ie:
                    print("failed to catalog likely duplicate item.", data)
                    continue
                if norename:
                    print(f"Norename copy {file} to {dest_dir}")
                    shutil.copy2(file, dest_dir)
                else:
                    if is_file_valid_uuid(file):
                        print(f"No need to rename, copy {file} to {dest_dir}")
                        shutil.copy2(file, dest_dir)
                    else:
                        new_filename = os.path.join(dest_dir, uuid_name)
                        print(f"Rename copy {file} to {new_filename}")
                        shutil.copy2(file, new_filename )
                if is_remove:
                    os.remove(file)
                if is_copyright:
                    add_copyright_metadata(new_filename)
                    update_catalog_item(new_filename)
                

    con.commit()
    con.close()
    print(f"source items processed: {count}")