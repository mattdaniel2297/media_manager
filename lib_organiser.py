import os
import sys
import shutil
from metadata_tools import get_create_time, put_dates_metadata
from datetime import datetime
pcount = 0
ROOT_DIR = None

# Fix an existing photos lib, moving files into YYYY/MM directory structure

def process_file(file):
    global ROOT_DIR
    x = file.rfind('.')
    ext = file[x:]
    if ext.lower() not in ['.jpg', '.gif', '.jpeg', '.png']:
        print(f"reject {file} with extension {ext}")
        return False
    # dest_dir = None
    try:
        # print(f"Process {file} created at {get_create_time(file)}")
        created_ts = get_create_time(file)
        created_year = created_ts.strftime("%Y")
        created_month = created_ts.strftime("%m")
        dest_dir = os.path.join(ROOT_DIR, created_year, created_month)
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(file, dest_dir)
        os.remove(file)
        dir_path = os.path.dirname(os.path.realpath(file))
        if len(os.listdir(dir_path)) == 0:
            shutil.rmtree(dir_path)
        return True
    except KeyError as ke:
        real_path = os.path.realpath(file)
        rel_dir = os.path.basename(os.path.dirname(real_path))
        created_year = rel_dir[0:4]
        created_month = rel_dir[4:6]
        created_day = rel_dir[6:8]
        dest_dir = os.path.join(ROOT_DIR, created_year, created_month)
        dir_struct_date = datetime(int(created_year), int(created_month), int(created_day))
        new_file = os.path.join(dest_dir, file)
        print(f"<<<<<< {rel_dir} >>>>>> {created_year}  {created_month}")
        dest_dir = os.path.join(ROOT_DIR, created_year, created_month)
        os.makedirs(dest_dir, exist_ok=True)
        # put date into metadata
        put_dates_metadata(new_file, dir_struct_date)
        shutil.copy2(file, dest_dir)
        os.remove(file)
        dir_path = os.path.dirname(os.path.realpath(file))
        if len(os.listdir(dir_path)) == 0:
            shutil.rmtree(dir_path)
        return True
    except shutil.SameFileError:
        return False

def process_dir(dir):
    global pcount, ROOT_DIR
    if ROOT_DIR == None:
        ROOT_DIR = dir
    nbp = os.path.basename(os.path.normpath(dir))
    print(f"process_dir: {dir} basename: {nbp} first: {nbp[0]}")
    if nbp[0]  == '.':
        print("skipping hidden dir")
        return

    if len(os.path.basename(os.path.normpath(dir))) < 3:
        print("SKIPPING dir")
        return
    
    for o in os.listdir(dir):
        if o[:0] == '.': 
            continue
        item = os.path.join(dir,o)
        if os.path.isfile(item):
            if process_file(item):
                pcount += 1
            else:
                print(f"Rejected {item}")
        elif os.path.isdir(item):
            process_dir(item)
        else:
            print(f"{item} is a {type(item)}")


root = sys.argv[1]
process_dir(root)
print(f"Count: {pcount}")