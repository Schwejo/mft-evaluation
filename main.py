from glob import glob
import itertools
import os
import matplotlib.pyplot as plot
import pandas as pd
from pathlib import Path
import re
from reflection_spectrum_evaluation import (
    evaluate_reflection_spectrum,
    plot_first_and_last_measurement,
)
from lab_evaluation import plot_delta_e_2000, plot_delta_lab_bar_chart, plot_lab
import time

start = time.time()

output_path = Path("output/new5")

data_path = Path("data")

# one directory per type of measurement setting
subdirs = sorted(os.listdir(data_path))

# match any string including "spect_convert.txt"
spect_regex = re.compile(".*spect_convert\.txt$")

# match any string NOT including "spect"
not_spect_regex = re.compile("^((?!spect).)*$")

figure = plot.figure(figsize=[10, 10], dpi=500)


def plot_overview(
    reflection_spectrum_data: list[tuple[str, pd.DataFrame]],
    delta_lab_data: list[tuple[str, tuple[list, list]]],
):
    figure.clear()
    figure.set_layout_engine("constrained")

    gs = figure.add_gridspec(3, 2, wspace=0.1, hspace=0.2)

    for i, datum in enumerate(delta_lab_data):
        plot_delta_lab_bar_chart(datum, figure.add_subplot(gs[i, 0]))

    for i, datum in enumerate(reflection_spectrum_data):
        plot_first_and_last_measurement(
            datum[1], figure.add_subplot(gs[i, 1]), datum[0]
        )

    figure.savefig(
        output_path.joinpath("{}_3.png".format(reflection_spectrum_data[0][0][3:]))
    )


def plot_lab_values_overview(lab_means: list[tuple[str, pd.DataFrame]]):
    figure.clear()
    figure.set_layout_engine("constrained")

    gs = figure.add_gridspec(3, 2, wspace=0.1, hspace=0.2)

    for i, datum in enumerate(lab_means):
        plot_lab(
            datum[1],
            figure.add_subplot(gs[i, 0]),
            figure.add_subplot(gs[i, 1]),
            datum[0],
        )

    figure.savefig(output_path.joinpath("{}_2.png".format(lab_means[0][0][3:])))


for sample_folder in sorted(os.listdir(data_path.joinpath(subdirs[0]))):
    # related sample_folders (and files) share their name except for the first letter
    all_sample_files = sorted(
        glob("data/**/*{}*.txt".format(sample_folder[1:]), recursive=True)
    )

    # tuple (sample identifier, dataframe)
    reflection_spectrum_means: list[tuple[str, pd.DataFrame]] = []

    # tuple (sample identifier, tuple (means, standard deviation))
    delta_labs: list[tuple[str, tuple[list, list]]] = []

    lab_means: list[tuple[str, pd.DataFrame]] = []

    for key, files in itertools.groupby(all_sample_files, lambda x: Path(x).parts[-2]):
        spect_convert_files: list[Path] = []
        not_spect_files: list[Path] = []

        filename = key

        for file in files:
            file = Path(file)
            if spect_regex.match(file.parts[-1]):
                spect_convert_files.append(file)

            if not_spect_regex.match(file.parts[-1]):
                not_spect_files.append(file)

        reflection_spectrum_means.append(
            (
                key,
                evaluate_reflection_spectrum(spect_convert_files),
            )
        )

        labs, lab_mean = plot_delta_e_2000(not_spect_files, False)

        lab_means.append((key, lab_mean))

        delta_labs.append((key, labs))

    plot_overview(reflection_spectrum_means, delta_labs)
    plot_lab_values_overview(lab_means)


print("done", time.time() - start)
