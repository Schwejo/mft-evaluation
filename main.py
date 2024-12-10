import os
from pathlib import Path
import re
from reflection_spectrum_evaluation import evaluate_reflection_spectrum

data_path = Path("data")

output_path = Path("output")

# match every string that includes "spect_convert.txt"
spect_regex = re.compile(".*spect_convert\.txt$")

# match every string that does NOT include "spect"
not_spect_regex = re.compile("^((?!spect).)*$")

for dir in next(os.walk(data_path))[1]:
    spect_convert_files: list[Path] = []
    not_spect_files: list[Path] = []

    for file in data_path.joinpath(dir).rglob("*.txt"):
        if spect_regex.match(file.parts[-1]):
            spect_convert_files.append(file)

        if not_spect_regex.match(file.parts[-1]):
            not_spect_files.append(file)

evaluate_reflection_spectrum(sorted(spect_convert_files), output_path)
