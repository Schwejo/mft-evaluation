import os
import re

mappings = [
    {
        "HF": "H",
        "MF": "M",
        "NF": "L",
    },
    {"PK": "PC"},
    {
        "BBL": "PRB",
        "GSP": "VDG",
        "BLW": "LWH",
        "MEN": "REL",
        "AUP": "ORP",
        "ZIN": "VML",
        "HGE": "HYE",
        "HRO": "HRE",
        "SGE": "SYE",
        "SRO": "SRE",
        "AQP": "WCP",
        "BMR": "BMP",
        "ROS": "PNK",
        "RVH": "RVL",
        "RVN": "RVM",
        "BVN": "BVM",
        "CDG": "CDY",
        "ZKG": "ZNG",
    },
]


def rename_pattern_in_files_and_dirs(root_dir, mapping: dict[str, str]):
    # Walk through the directory
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename files
        for filename in filenames:
            for key, value in mapping.items():
                regex = re.compile(key)
                new_filename = regex.sub(value, filename)
                if new_filename != filename:
                    old_file_path = os.path.join(dirpath, filename)
                    new_file_path = os.path.join(dirpath, new_filename)
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed file: {old_file_path} -> {new_file_path}")

        # Rename directories
        for dirname in dirnames:
            for key, value in mapping.items():
                regex = re.compile(key)
                new_dirname = regex.sub(value, dirname)
                if new_dirname != dirname:
                    old_dir_path = os.path.join(dirpath, dirname)
                    new_dir_path = os.path.join(dirpath, new_dirname)
                    os.rename(old_dir_path, new_dir_path)
                    print(f"Renamed directory: {old_dir_path} -> {new_dir_path}")


# Example usage
root_directory = "data"

for mapping in mappings:
    rename_pattern_in_files_and_dirs(root_directory, mapping)
