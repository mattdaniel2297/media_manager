import sqlite3
import os
import sys
import fnmatch
from cksum import memcrc
from UUID_namer import is_file_valid_uuid, process_file
from metadata_tools import get_create_time, get_modified_time, add_copyright_metadata

is_existing_catalog = False

def create_db(dir):
    db_loc = os.path.join(dir, "catalog.db")
    con = sqlite3.connect(db_loc)
    cur = con.cursor()
    cur.execute("""
                CREATE TABLE "item"
                ("id"	TEXT NOT NULL,
                "previous_name" TEXT,
                "cksum" INTEGER NOT NULL, 
                "original_cksum" INTEGER NOT NULL UNIQUE, 
                "path"	TEXT NOT NULL,
                "size_bytes" INTEGER,
                "created_date" TEXT NOT NULL,
                "modified_date" TEXT NOT NULL,
                PRIMARY KEY("id")
                )""")


def create_catalog(dir):
    db_loc = os.path.join(dir, "catalog.db")
    if not os.path.exists(db_loc):
        print(f"no catalog.db found at {db_loc}")
        create_db(dir)
    else:
        raise Exception(f"Catalog already exists as {db_loc}")

    con = sqlite3.connect(db_loc)
    cur = con.cursor()

    total = 0
    count = 0
    for root, dir, files in os.walk(dir):
        # Just image processing for now
        # for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp', 'mp4', 'webm', 'avi', 'mov', 'wmv', 'ogg', 'mkv']:
        dir[:] = [d for d in dir if not d[0] == '.']
        files[:] = [f for f in files if not f[0] == '.']
        for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp']:
            for filename in fnmatch.filter(files, '*.' + extension):
                file = os.path.join(root, filename)
                print(root, filename)

                buffer = open(file, 'rb').read()
                ck = memcrc(buffer)
                size_bytes = os.path.getsize(file)
                created_ts = get_create_time(file)
                modified_ts = get_modified_time(file)
                # This will rename the actual file to be compliant
                basename = process_file(file, rename_source=True)
                real_path = os.path.realpath(file)
                dir_name = os.path.dirname(real_path)
                new_filename = os.path.join(dir_name, basename)
                
                data = (basename, filename, ck, ck, dir_name, size_bytes, created_ts, modified_ts)
                add_copyright_metadata(new_filename)
                cur.execute("insert into item VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
                count += 1
                if count > 1000:
                    con.commit()
                    total += count
                    count = 0
                    print(f"----- rows created so far: {total} -----")
    con.commit()
    con.close()
    print(f"total items: {total}")


def dedupe(dir):
    db_loc = os.path.join(dir, "catalog.db")
    con = sqlite3.connect(db_loc)
    cur = con.cursor()
    res = cur.execute("""select cksum, count(*)
            from item
            group by cksum
            having count(*) > 1""")
    data = res.fetchall()
    cur.close()

    print(len(data))
    for item in data:
        cur = con.cursor()
        res = cur.execute(f"select * from item where cksum = {item[0]}")
        dupe_data = res.fetchall()
        print(f"dupe_count from data {len(dupe_data)}")
        dupe_count = len(dupe_data)
        for dupe_item in dupe_data[1:]:
            if not is_file_valid_uuid(dupe_item):
                file_to_delete = os.path.join(dupe_item[2], dupe_item[0])
                print(file_to_delete)
                os.remove(file_to_delete)
    cur.close()    
    con.close()

# 
# create_catalog(sys.argv[1])
# dedupe(sys.argv[1])