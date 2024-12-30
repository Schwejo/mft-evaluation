from glob import glob
import pandas as pd
import matplotlib.pyplot as plot
from pathlib import Path
from os import makedirs, listdir
import re
import numpy as np

# directory to put generated files in
output_directory = "output"

# make sure the directory exists
makedirs(output_directory, exist_ok=True)

data_directory = "data/HF_Box1/HF_GA_AUP"

# match any .txt file
filename_pattern = "*.txt"

files = sorted(glob("{}/{}".format(data_directory, filename_pattern)))

# match every string that does NOT include "spect"
filename_regex = re.compile("^((?!spect).)*$")

files = [i for i in files if filename_regex.match(i)]

# list that holds a dataframe for each measurement file
dataframes = []

for file in files:
    df = pd.read_csv(
        file,
        sep="\t",
        skiprows=3,
        header=0,
        names=["time", "L", "a", "b", "dE76", "dE94", "delta_e_2000", "dL", "da", "db"],
        usecols=[
            "time",
            "L",
            "a",
            "b",
            "dE76",
            "dE94",
            "delta_e_2000",
            "dL",
            "da",
            "db",
        ],
    )
    df.index.name = "index"
    dataframes.append(df)


def plot_delta_e_2000(data: list[pd.DataFrame], output_filename: str) -> None:
    figure = plot.figure()
    axes = figure.subplots()
    # axes.set_ylabel("Reflectance [%]")
    # axes.set_ylim(0, 80)
    # axes.set_xlabel("Wavelength [nm]")
    # axes.set_xlim(420, 720)
    axes.grid(alpha=0.5)

    # linespace to evaluate function at 1000 points between 0 and 300
    x_new = np.linspace(0, 300, 1000)

    df_mean = pd.concat(data).groupby("index").mean().set_index("time")
    df_std = pd.concat(data).groupby("index").std()

    # generate function from data
    z = np.polyfit(df_mean.index.to_list(), df_mean["delta_e_2000"], 16)
    f = np.poly1d(z)

    y_new = f(x_new)

    # dirty
    y_new[0] = 0

    df = pd.DataFrame(y_new, x_new, columns=["delta_e_2000"])
    df.index.name = "time"

    axes.plot(x_new, y_new, linewidth=0.4, color="black")

    # axes.plot(df_mean, "o", label="mean", color="green", linewidth=0.3, markersize=0.3)

    result_dfs = [df_mean.tail(1), df_std.tail(1)]

    for i, datum in enumerate(data):
        result_dfs.insert(0, (datum.tail(1)))

    result_concat = pd.concat(result_dfs, ignore_index=True)

    result_concat["name"] = ""
    result_concat["name"][5] = "mean"
    result_concat["name"][6] = "standard deviation"

    result_concat.index.name = "index"

    result_concat = result_concat.drop("time", axis=1)

    result_concat.to_csv(
        "{}/{}.csv".format(output_directory, output_filename),
        columns=["name", "dE76", "dE94", "delta_e_2000", "dL", "da", "db"],
    )

    # axes.legend()
    figure.savefig("{}/{}.png".format(output_directory, output_filename), dpi=1200)

    figure.clf()

    axes = figure.subplots()
    axes.set_ylabel("b*")
    axes.set_xlabel("a*")
    axes.set_title("a*b* values")
    # axes.plot(
    # df_mean["a"],
    # df_mean["b"],
    # "o",
    # markersize=0.4,
    # linewidth=0.4,
    # color="green",
    # )

    # figure.savefig("{}/{}.png".format(output_directory, "ab_values"), dpi=1200)

    figure.clf()

    axes = figure.subplots()
    axes.set_ylabel("L*")
    axes.set_xlabel("Time")
    axes.set_title("L* values")
    # axes.plot(
    # df_mean["L"],
    # "o",
    # markersize=0.4,
    # linewidth=0.4,
    # color="green",
    # )

    # figure.savefig("{}/{}.png".format(output_directory, "l_values"), dpi=1200)

    lab_end_mean_values = df_mean.tail(1)[["db", "da", "dL"]].values[0]
    lab_end_std_values = df_std.tail(1)[["db", "da", "dL"]].values[0]

    colors = ["" for _ in range(3)]

    for index, value in enumerate(lab_end_mean_values):
        if value < 0:
            if index == 0:
                colors[0] = "#565656"
            if index == 1:
                colors[1] = "#4dd72f"
            if index == 2:
                colors[2] = "#1a71e3"
        else:
            if index == 0:
                colors[0] = "#aeaeae"
            if index == 1:
                colors[1] = "#e3371a"
            if index == 2:
                colors[2] = "#e3c81a"

    colors.reverse()

    figure.clf()

    axes = figure.subplots()
    axes.yaxis.set_ticks([0, 1, 2], ["db", "da", "dL"])
    axes.barh(
        [0, 1, 2],
        lab_end_mean_values,
        height=1,
        color=colors,
    )

    axes.errorbar(
        lab_end_mean_values,
        [0, 1, 2],
        xerr=lab_end_std_values,
        fmt=",",
        color="black",
        capsize=10,
        elinewidth=1,
    )

    figure.savefig("{}/{}.png".format(output_directory, "dLab"), dpi=1200)


plot_delta_e_2000(dataframes, "delta_e_2000_01")
