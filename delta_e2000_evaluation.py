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

data_directory = "data/HF_GA_AUP"

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
        usecols=["time", "delta_e_2000"],
        # index_col="time",
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

    function_values_dfs = []

    # linespace to evaluate function at 1000 points between 0 and 300
    x_new = np.linspace(0, 300, 1000)

    for i, datum in enumerate(data):
        datum = datum.set_index("time")

        # generate function from data
        z = np.polyfit(datum.index.to_list(), datum["delta_e_2000"], 16)
        f = np.poly1d(z)

        y_new = f(x_new)

        df = pd.DataFrame(y_new, x_new, columns=["delta_e_2000"])
        df.index.name = "time"

        # save new values
        function_values_dfs.append(df)

        # axes.plot(x_new, y_new, linewidth=0.4, color="black")

        axes.plot(
            datum["delta_e_2000"],
            "o",
            label="measure {}".format(i),
            color="gray",
            markersize=0.5,
            linewidth=0.8,
        )

    df_mean = pd.concat(function_values_dfs).groupby("time").mean()
    df_mean2 = pd.concat(data).groupby("index").mean().set_index("time")

    # df_std = pd.concat(function_values_dfs).groupby("time").std()
    # df_std2 = pd.concat(data).groupby("index").std()

    axes.plot(
        df_mean,
        "-",
        label="mean",
        color="green",
        linewidth=0.3,
    )

    axes.legend()
    figure.savefig("{}/{}.png".format(output_directory, output_filename), dpi=1200)


plot_delta_e_2000(dataframes, "delta_e_2000")
