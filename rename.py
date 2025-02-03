import os
import re


def rename_pattern_in_files_and_dirs(root_dir, pattern, replacement):
    # Compile the regex pattern
    regex = re.compile(pattern)

    # Walk through the directory
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename files
        for filename in filenames:
            new_filename = regex.sub(replacement, filename)
            if new_filename != filename:
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)
                os.rename(old_file_path, new_file_path)
                print(f"Renamed file: {old_file_path} -> {new_file_path}")

    # Rename directories
    for dirname in dirnames:
        new_dirname = regex.sub(replacement, dirname)
        if new_dirname != dirname:
            old_dir_path = os.path.join(dirpath, dirname)
            new_dir_path = os.path.join(dirpath, new_dirname)
            os.rename(old_dir_path, new_dir_path)
            print(f"Renamed directory: {old_dir_path} -> {new_dir_path}")


# Example usage
root_directory = "data"  # Change this to your target directory
pattern_to_replace = r"old_pattern"  # Change this to your pattern
replacement_string = "new_pattern"  # Change this to your replacement

rename_pattern_in_files_and_dirs(root_directory, pattern_to_replace, replacement_string)

mapping = {
    "HF": "H",
    "MF": "M",
    "NF": "L",
    "PK": "PC",
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
}
