import os
import uuid
import re

expression = "[a-fA-F0-9]{32}"
p = re.compile(expression, re.IGNORECASE)

def gen_uuid():
    u = uuid.uuid4().hex
    c = u.replace("-", "")
    return c


# unused for now
def is_collection_dir(dir):
    for o in os.listdir(dir):
        item = os.path.join(dir,o)
        if os.path.isfile(item):
            return o == ".collection"
        
        
def is_file_valid_uuid(file):
    basename = os.path.basename(file)
    return p.match(basename)


# given a fullpath filename, return a UUID basename
def process_file(file, rename_source=False):
    if not is_file_valid_uuid(file):
        # print(f"Fixing {file}")
        ext = os.path.splitext(file)[1]
        uuid_basename = gen_uuid()
        new_basename = uuid_basename+ext
        idx = file.find(os.path.basename(file))
        filepath = file[:idx]
        new_file = os.path.join(filepath,new_basename)
        if rename_source:
            os.rename(file, new_file)
        return new_basename
    else:
        return os.path.basename(file)



def process_dir(dir):
    print(f"process_dir: {dir}")
    for o in os.listdir(dir):
        item = os.path.join(dir,o)
        if os.path.isfile(item):
            process_file(item)
        elif os.path.isdir(item):
            process_dir(item)
        else:
            print(f"{item} is a {type(item)}")




