import argparse
from metadata_tools import print_all_file_metadata, get_tag_values


def print_test_file_metadata(test_file):
    print_all_file_metadata(test_file)

    tag_key = "Xmp.digiKam.TagsList"
    copy_tags = ['Photo Stream']

    try:

        r = get_tag_values(test_file, tag_key)
    
        for tag in copy_tags:
            if tag in r:  
                print(f"{tag} is present")
    except Exception as e:
        # print(e)
        None


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Test Suite")
    parser.add_argument("--copyright", action="store_true", help="apply copyright to metadata")
    parser.add_argument("--norename", action="store_true", help="Do not rename destination files with UUID")
    parser.add_argument('--tag', action='append')
    args = parser.parse_args()
    print(f'catalog: {args.copyright}')
    print(f"tags: {args.tag}")

    test_file = "/home/mdaniel/Pictures/2024/01/02f769dc64b3472fba9fe07914e67781.jpg"
    print_test_file_metadata(test_file)
    print("-" * 50)
    print_all_file_metadata('photo_lib/635ca5a4054d4c1fae5fc02269284d9d.jpg')
    
