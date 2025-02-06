from glob import glob
from os import makedirs, listdir
from pathlib import Path
from itertools import groupby
from pandas import DataFrame, concat
from matplotlib.pyplot import figure
from re import compile
import time
import multiprocessing

from reflection_spectrum_evaluation import (
    evaluate_reflection_spectrum,
    plot_first_and_last_measurement,
)
from lab_evaluation import (
    plot_delta_e_2000,
    plot_delta_lab_bar_chart,
    plot_lab,
    plot_overview_table,
    plot_curve_fit_delta_e,
)
from plot_util import init_figure

start = time.time()

output_path = Path("output/new10")

# make sure the output directory exists
makedirs(output_path, exist_ok=True)

data_path = Path("data")

# one directory per type of measurement setting
subdirs = sorted(listdir(data_path))

# match any string including "spect_convert.txt"
spect_regex = compile(".*spect_convert.txt$")

# match any string NOT including "spect"
not_spect_regex = compile("^((?!spect).)*$")

# reuse one figure for all plots
fig = figure(figsize=[10, 10], dpi=500)


def plot_overview(
    reflection_spectrum_data: list[tuple[str, DataFrame]],
    delta_lab_data: list[tuple[str, tuple[list, list]]],
):
    gs = init_figure(fig, 3, 2)

    val_min_dev_array = []
    val_pl_dev_array = []

    for i in range(0, 3):
        for j in range(0, 3):
            val_min_dev_array.append(
                delta_lab_data[i][1][0][j] - delta_lab_data[i][1][1][j]
            )
            val_pl_dev_array.append(
                delta_lab_data[i][1][0][j] + delta_lab_data[i][1][1][j]
            )

    if min(val_min_dev_array) < 0 and max(val_pl_dev_array) < 0:
        x_lim_max = 0.1
        x_lim_min = min(val_min_dev_array) * 1.1
    elif min(val_min_dev_array) > 0 and max(val_pl_dev_array) > 0:
        x_lim_min = -0.1
        x_lim_max = max(val_pl_dev_array) * 1.1
    else:
        x_lim_min = min(val_min_dev_array) * 1.1
        x_lim_max = max(val_pl_dev_array) * 1.1

    for i, datum in enumerate(delta_lab_data):
        plot_delta_lab_bar_chart(datum, fig.add_subplot(gs[i, 0]), x_lim_min, x_lim_max)

    for i, datum in enumerate(reflection_spectrum_data):
        plot_first_and_last_measurement(datum[1], fig.add_subplot(gs[i, 1]), datum[0])

    fig.savefig(
        output_path.joinpath("{}_3.png".format(reflection_spectrum_data[0][0][2:]))
    )


def plot_overview_table_overview(overview_table_data: list[tuple[str, DataFrame]]):
    gs = init_figure(fig, 3, 1)

    for i, datum in enumerate(overview_table_data):
        plot_overview_table(datum[1], fig.add_subplot(gs[i]), datum[0])

    fig.savefig(output_path.joinpath("{}_1.png".format(overview_table_data[0][0][2:])))

    concat(map(lambda x: x[1], overview_table_data)).to_csv(
        output_path.joinpath("{}_1.csv".format(overview_table_data[0][0][2:])),
        columns=["dE76", "dE94", "delta_e_2000", "dL", "da", "db", "L", "a", "b"],
        header=["dE76", "dE94", "dE00", "dL", "da", "db", "L", "a", "b"],
    )


def plot_lab_values_overview(lab_means: list[tuple[str, DataFrame]]):
    gs = init_figure(fig, 3, 2)

    for i, datum in enumerate(lab_means):
        plot_lab(
            datum[1],
            fig.add_subplot(gs[i, 0]),
            fig.add_subplot(gs[i, 1]),
            datum[0],
        )

    fig.savefig(output_path.joinpath("{}_2.png".format(lab_means[0][0][2:])))


def plot_curve_fit_delta_e_overview(
    curve_fit_delta_e_dfs: list[tuple[str, DataFrame]],
    lab_means: list[tuple[str, DataFrame]],
    lab_stds: list[tuple[str, DataFrame]],
):
    gs = init_figure(fig)

    plot_curve_fit_delta_e(
        curve_fit_delta_e_dfs, lab_means, lab_stds, fig.add_subplot(gs[0])
    )

    fig.savefig(
        output_path.joinpath("{}_1_1.png".format(curve_fit_delta_e_dfs[0][0][2:]))
    )


def handle_sample_folder(sample_folder):
    # related sample_folders (and files) share their name except for the first letter
    all_sample_files = sorted(
        glob("data/**/*{}*.txt".format(sample_folder[1:]), recursive=True),
        key=lambda filename: (
            "A"
            if filename.startswith("data/H")
            else "B" if filename.startswith("data/M") else "C"
        ),
    )

    # tuple (sample identifier, dataframe)
    reflection_spectrum_means: list[tuple[str, DataFrame]] = []

    # tuple (sample identifier, tuple (means, standard deviation))
    delta_labs: list[tuple[str, tuple[list, list]]] = []

    # tuple (sample identifier, dataframe)
    lab_means: list[tuple[str, DataFrame]] = []
    lab_stds: list[tuple[str, DataFrame]] = []

    overview_table_data: list[tuple[str, DataFrame]] = []

    curve_fit_dfs: list[tuple[str, DataFrame]] = []

    # Group by folder name and iterate over each group. 'files' hold all file names in the current folder.
    for folder, files in groupby(all_sample_files, lambda x: Path(x).parts[-2]):
        spect_convert_files: list[Path] = []
        not_spect_files: list[Path] = []

        for file in files:
            file = Path(file)
            if spect_regex.match(file.parts[-1]):
                spect_convert_files.append(file)

            if not_spect_regex.match(file.parts[-1]):
                not_spect_files.append(file)

        reflection_spectrum_means.append(
            (
                folder,
                evaluate_reflection_spectrum(spect_convert_files),
            )
        )

        labs, lab_mean, lab_std, overview_table_df, curve_fit_delta_e_df = (
            plot_delta_e_2000(not_spect_files)
        )

        lab_means.append((folder, lab_mean))
        lab_stds.append((folder, lab_std))

        overview_table_data.append((folder, overview_table_df))

        curve_fit_dfs.append((folder, curve_fit_delta_e_df))

        delta_labs.append((folder, labs))

    plot_overview(reflection_spectrum_means, delta_labs)
    plot_lab_values_overview(lab_means)
    plot_overview_table_overview(overview_table_data)
    plot_curve_fit_delta_e_overview(curve_fit_dfs, lab_means, lab_stds)


# for sample_folder in sorted(listdir(data_path.joinpath(subdirs[0]))):
#     handle_sample_folder(sample_folder)

pool = multiprocessing.Pool()
pool.map(handle_sample_folder, sorted(listdir(data_path.joinpath(subdirs[0]))))
pool.close()
pool.join()

print("done", time.time() - start)
