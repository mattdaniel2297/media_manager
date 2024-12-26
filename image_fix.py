import pyexiv2
import os
import sys
import fnmatch
from datetime import datetime

print(pyexiv2.exiv2_version_info)

print(pyexiv2.version_info)

copyright_keys = ('Exif.Image.Copyright', 'Iptc.Application2.Copyright')
exif_copyright_key = 'Exif.Image.Copyright'
iptc_copyright_key = 'Iptc.Application2.Copyright'
iptc_credit_keys = ('Iptc.Application2.Credit', 'Iptc.Application2.Source')
date_keys = ('Exif.Image.DateTime', 'Exif.Photo.DateTimeOriginal', 'Exif.Photo.DateTimeDigitized')
COPYRIGHT_NAME = "Matt Daniel"


def add_metadata(file):
    metadata = pyexiv2.ImageMetadata(file)
    metadata.read()
    dates = []
    year = str(datetime.now().year)
    for k in date_keys:
        if k in metadata.exif_keys:
            t = metadata[k]
            dates.append(t.raw_value)
    if len(dates) > 0:
        dates.sort()
        year = dates[0][:4]

    print(file, year)
    modify = False
    if exif_copyright_key not in metadata.exif_keys:
            metadata[exif_copyright_key] = f"({year}) {COPYRIGHT_NAME} - All rights reserved"
            modify = True
    if iptc_copyright_key not in metadata.iptc_keys:
            metadata[iptc_copyright_key] = [f"({year}) {COPYRIGHT_NAME} All rights reserved"]
            modify = True
    for iptc_key in iptc_credit_keys:
        if iptc_key not in metadata.iptc_keys:
            metadata[iptc_key] = [COPYRIGHT_NAME]
            modify = True
    if modify:
       metadata.write()

def fix_metadata(root_dir):
    file_count = 0
    for (root, dirs, files) in os.walk(root_dir):
        for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp']:
            for filename in fnmatch.filter(files, '*.' + extension):
                file_count += 1
                file = os.path.join(root, filename)
                # print(f"--- {file} ---")
                add_metadata(file)
                # print("-----------------")
    print(f"total photos: {file_count}")


# def print_file_metadata(file):
#     metadata = pyexiv2.ImageMetadata(file)
#     metadata.read()
#     for k in copyright_keys:
#         if k in metadata.exif_keys:
#             t = metadata[k]
#             print(k, t)
#     for k in iptc_credit_keys:
#         if k in metadata.iptc_keys:
#             t = metadata[k]
#             print(k, t)
#     for k in date_keys:
#         if k in metadata.exif_keys:
#             t = metadata[k]
#             # print(k, t)
#         else:
#             print(f"no date for {file}")


# def print_select(root_dir):
#     file_count = 0
#     for (root, dirs, files) in os.walk(root_dir):
#         for extension in ['jpg', 'jpeg', 'gif', 'png' ,'webp']:
#             for filename in fnmatch.filter(files, '*.' + extension):
#                 file_count += 1
#                 file = os.path.join(root, filename)
#                 # print(f"--- {file} ---")
#                 print_file_metadata(file)
#                 # print("-----------------")
#     print(f"total photos: {file_count}")




# def print_all_metadata(metadata):
#     # metadata = pyexiv2.ImageMetadata('images/md/20231107_090204.jpg')
#     metadata.read()
#     print("========= exif ==========")
#     for k in metadata.exif_keys:
#         t = metadata[k]
#         print(k, t)
#     print("========= iptc ==========")    
#     for k in metadata.iptc_keys:
#         t = metadata[k]
#         print(k, t)
#     print("========= xmp ==========")    
#     for k in metadata.xmp_keys:
#         t = metadata[k]
#         print(k, t)

def test():
    root_dir = sys.argv[1]
    fix_metadata(root_dir)
