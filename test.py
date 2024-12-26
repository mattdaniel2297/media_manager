from metadata_tools import print_all_file_metadata, get_tag_values

my_test_file = "/home/mdaniel/Pictures/2024/01/02f769dc64b3472fba9fe07914e67781.jpg"

print_all_file_metadata(my_test_file)

tag_key = "Xmp.digiKam.TagsList"
copy_tags = ['Photo Stream']

r = get_tag_values(my_test_file, tag_key)
v = r.raw_value
print(type(v))
for tag in copy_tags:
    if tag in v:
        print("Winner!")