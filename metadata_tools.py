import pyexiv2
import os
import sys
import fnmatch
from time import strftime, localtime
from date_utils import str_to_datetime
from datetime import datetime

COPYRIGHT_KEYS = ('Exif.Image.Copyright', 'Iptc.Application2.Copyright')
EXIF_COPYRIGHT_KEY = 'Exif.Image.Copyright'
iptc_copyright_key = 'Iptc.Application2.Copyright'
IPTC_CREDIT_KEYS = ('Iptc.Application2.Credit', 'Iptc.Application2.Source')
DATE_KEYS = ('Exif.Image.DateTime', 'Exif.Photo.DateTimeOriginal', 'Exif.Photo.DateTimeDigitized')
COPYRIGHT_NAME = "Matt Daniel"


# def get_create_time_from_dir_structure(file):
#     rel_path = os.path.realpath(file)
def put_dates_metadata(file, struct_date):
    date = struct_date.strftime('%Y-%m-%d %H:%M:%S')
    metadata = pyexiv2.ImageMetadata(file)
    metadata.read()
    metadata['Exif.Image.DateTime'] = date
    metadata['Exif.Photo.DateTimeOriginal'] = date
    metadata.write()
    

def get_create_time_from_filesystem(file):
    # epoc_time = os.path.getctime(file)
    epoc_time = os.path.getmtime(file)
    s = strftime('%Y-%m-%d %H:%M:%S', localtime(epoc_time))
    file_dt = str_to_datetime(s)
    return file_dt


def get_modified_time(file):
    try:
        metadata = pyexiv2.ImageMetadata(file)
        metadata.read()
        value = metadata['Exif.Image.DateTime'].raw_value
        meta_dt = str_to_datetime(value)
        epoc_time = os.path.getmtime(file)
        s = strftime('%Y-%m-%d %H:%M:%S', localtime(epoc_time))
        file_dt = str_to_datetime(s)
        return max(meta_dt, file_dt)
    except Exception as e:
        print(f"No metadata create time for {file}")
        # raise e
        return get_create_time_from_filesystem(file)


def get_create_time(file):
    try:
        metadata = pyexiv2.ImageMetadata(file)
        metadata.read()
        t = metadata['Exif.Photo.DateTimeOriginal']
        return (str_to_datetime(t.raw_value))
    except Exception as e:
        print(f"No metadata create time for {file}")
        # raise e
        return get_create_time_from_filesystem(file)
    

# return true if metadata was added to file
def add_copyright_metadata(file):
    metadata = pyexiv2.ImageMetadata(file)
    metadata.read()
    dates = []
    year = str(datetime.now().year)
    for k in DATE_KEYS:
        if k in metadata.exif_keys:
            t = metadata[k]
            dates.append(t.raw_value)
    if len(dates) > 0:
        dates.sort()
        year = dates[0][:4]

    modify = False
    if EXIF_COPYRIGHT_KEY not in metadata.exif_keys:
            metadata[EXIF_COPYRIGHT_KEY] = f"({year}) {COPYRIGHT_NAME} - All rights reserved"
            modify = True
    if iptc_copyright_key not in metadata.iptc_keys:
            metadata[iptc_copyright_key] = [f"({year}) {COPYRIGHT_NAME} All rights reserved"]
            modify = True
    for iptc_key in IPTC_CREDIT_KEYS:
        if iptc_key not in metadata.iptc_keys:
            metadata[iptc_key] = [COPYRIGHT_NAME]
            modify = True
    if modify:
       now = datetime.now()
       mod_dt = now.strftime('%Y-%m-%d %H:%M:%S')
       metadata['Exif.Image.DateTime'] =mod_dt
       metadata.write()
    return modify


def get_tag_values(file, tag_key):
    metadata = pyexiv2.ImageMetadata(file)
    metadata.read()
    try:
        return metadata[tag_key].raw_value
    except:
        return None

def print_all_file_metadata(file):
    metadata = pyexiv2.ImageMetadata(file)
    metadata.read()
    print("========= exif ==========")
    for k in metadata.exif_keys:
        t = metadata[k]
        print(k, t)
    print("========= iptc ==========")    
    for k in metadata.iptc_keys:
        t = metadata[k]
        print(k, t)
    print("========= xmp ==========") 
    for k in metadata.xmp_keys:
        try:
            t = metadata[k]
            print(f"--->{k}<---  --->{t}<---")
        except Exception as e:
            print(f"failed to read {k} a type of {type(k)}")


def print_all(root_dir):
    file_count = 0
    for (root, dirs, files) in os.walk(root_dir):
        for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp']:
            for filename in fnmatch.filter(files, '*.' + extension):
                file_count += 1
                file = os.path.join(root, filename)
                # print(f"--- {file} ---")
                print_all_file_metadata(file)
                # print("-----------------")
    print(f"total photos: {file_count}")

    
def test(my_test_file):
    if os.path.exists(my_test_file) and os.path.isfile(my_test_file):
        print(f"Process {my_test_file}")
    # print(os.path.getmtime(my_test_file))
        ct = get_create_time(my_test_file)
        mt = get_modified_time(my_test_file)
    # et = os.path.getmtime(my_test_file)
    # print(f"type: {type(et)} value: {et}")

    # ct = ct.replace(':', '-', 2)
        print(f"create time  : {ct}")
        print(f"modified time: {mt}")
