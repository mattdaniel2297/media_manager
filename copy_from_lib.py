import os
import argparse
import fnmatch
import shutil
from metadata_tools import get_tag_values, get_modified_time

TAG_KEY = "Xmp.digiKam.TagsList"
COPY_TAGS = ['Photo Stream']


class FileItem:
    """Object to keep unique id (UUID filename) and file together"""
    def __init__(self, file):
        self.file = file
        self.basename = os.path.basename(file)
    

    def get_mod_ts(self):
        return get_modified_time(self.file)



def get_tagged_files(directory):
    file_list = []
    for root, directory, files in os.walk(directory):
        # Just image processing for now
        directory[:] = [d for d in directory if not d[0] == '.']
        files[:] = [f for f in files if not f[0] == '.']
        for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp']:
            for filename in fnmatch.filter(files, '*.' + extension):
                file = os.path.join(root, filename)
                for tag in COPY_TAGS:
                    values = get_tag_values(file, TAG_KEY)
                    if values and tag in values:
                        fi = FileItem(file)
                        file_list.append(fi)
    return file_list    


def export(src, dest):
    # Look through meta of every src item for copy tags
    export_files= get_tagged_files(src)
    existing_files = get_tagged_files(dest)
    print(f"{len(export_files)} Export files")
    print("++++++++++++++++++++++++++++++++")
    print(f"{len(existing_files)} Existing files")
    match_count = 0
    need_update_count = 0
    files_to_copy = []

    for a in export_files:
        is_matched = False
        is_need_copy = True
        for b in existing_files:
            if a.basename == b.basename:
                is_matched = True
                print(f"Matched {a.basename} mod at: {a.get_mod_ts()} <<<>>> {b.get_mod_ts()}") 
                try:
                    if a.get_mod_ts() > b.get_mod_ts():
                        need_update_count += 1
                        is_need_copy = True
                        print(f"Needs Updated {a.basename} mod at: {a.get_mod_ts()} <<<>>> {b.get_mod_ts()}") 
                    else:
                        match_count += 1
                        is_need_copy = False
                    break
                except:
                    None
        if not is_matched or is_need_copy:
            files_to_copy.append(a)
    print(match_count, need_update_count, len(files_to_copy))
    
    copy_count = 0
    for fi in files_to_copy:
        shutil.copy2(fi.file, dest)
        # shutil.copy(fi.file, dest)

        copy_count += 1
    print(f"Copy Count: {copy_count}")
    # Now find files in the target that are longer tagged or existing in the source
    files_to_remove = []
    for b in existing_files:
        is_matched = False
        for a in export_files:
            if b.basename == a.basename:
                is_matched = True
                break
        if not is_matched:
            files_to_remove.append(b)
    print(f"Files to remove {len(files_to_remove)}")
    for fi in files_to_remove:
        os.remove(fi.file)
        print(f"Removed: {fi.file}")
        


parser = argparse.ArgumentParser("Media Exporter")
parser.add_argument("--src", nargs=1, help="directory of media files to import")
parser.add_argument("--dest", nargs=1, help="directory of destination media files")
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

export(source_root,dest_root)
