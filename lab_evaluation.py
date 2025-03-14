from glob import glob
from pathlib import Path
import pandas as pd
import matplotlib.axes as axes
import matplotlib.pyplot as plot
import re
import numpy as np
from pandas.core.interchange.dataframe_protocol import DataFrame

from plot_util import add_grid


def plot_lab(
    df: pd.DataFrame, l_axes: axes.Axes, ab_axes: axes.Axes, title: str
) -> None:
    df = df.drop(df.tail(1).index)

    l_axes.set_ylabel("L*")
    l_axes.set_xlabel("Time")
    l_axes.set_title(title)
    l_axes.plot(
        df["L"],
        "o",
        markersize=0.4,
        linewidth=0.4,
        color="blue",
    )
    add_grid(l_axes)

    ab_axes.set_ylabel("b*")
    ab_axes.set_xlabel("a*")
    ab_axes.set_title(title)
    ab_axes.plot(
        df["a"],
        df["b"],
        "o",
        markersize=0.4,
        linewidth=0.4,
        color="blue",
    )
    add_grid(ab_axes)

    head = df.head(1)
    tail = df.tail(1)
    # print(first_and_last)
    ab_axes.scatter(
        head["a"], head["b"], marker="X", c="green", alpha=0.7, label="Start"
    )
    ab_axes.scatter(tail["a"], tail["b"], marker="s", c="red", alpha=0.5, label="End")
    ab_axes.legend()


def plot_overview_table(df: pd.DataFrame, axes: axes.Axes, title: str):
    axes.table(
        df.values,
        colLabels=df.columns,
        rowLabels=["1", "2", "3", "4", "5", "mean", "std"],
        colColours=["lightgray"] * len(df.columns),
        rowColours=["lightgray"] * len(df),
        loc="best",
    )
    axes.set_title(title)
    axes.axis("off")
    axes.axis("tight")


def plot_curve_fit_delta_e(
    data: list[tuple[str, pd.DataFrame]],
    means: list[tuple[str, pd.DataFrame]],
    stds: list[tuple[str, pd.DataFrame]],
    axes: axes.Axes,
):
    colors = ["#1a71e3", "#4dd72f", "#e3371a"]

    for i, (title, df) in enumerate(data):
        axes.plot(
            df,
            linewidth=1,
            color=colors[i],
            label=title,
        )

    for i, (title, df) in enumerate(means):
        axes.plot(
            df["delta_e_2000"],
            "o",
            color=colors[i],
            markersize=1.2,
            label=title,
        )
    for i, (title, df) in enumerate(stds):
        axes.fill_between(
            df.index,
            df["delta_e_2000_min"],
            df["delta_e_2000_max"],
            color=colors[i],
            alpha=0.2
        )

    axes.legend()
    add_grid(axes)
    axes.set_xlabel("time [s]")
    axes.set_ylabel("dE00")


def plot_delta_e_2000(files: list[Path]):
    # list that holds a dataframe for each measurement file
    dataframes = []

    for file in files:
        curve_fit_delta_e_df = pd.read_csv(
            file,
            sep="\t",
            skiprows=3,
            header=0,
            names=[
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
        curve_fit_delta_e_df.index.name = "index"
        dataframes.append(curve_fit_delta_e_df)

    # figure = plot.figure()
    # axes = figure.subplots()
    # axes.set_ylabel("Reflectance [%]")
    # axes.set_ylim(0, 80)
    # axes.set_xlabel("Wavelength [nm]")
    # axes.set_xlim(420, 720)
    # axes.grid(alpha=0.5)

    # linespace to evaluate function at 1000 points between 0 and 300
    x_new = np.linspace(0, 300, 1000)

    df_concat_new = pd.concat(dataframes, axis=1)
                 # .groupby("index"))
    # print(df_concat["L"][0])
    df_concat_l = df_concat_new["L"]
    #df_concat_l = df_concat_l.drop(index=151, axis=1)
    df_concat_l_mean = df_concat_l.mean(axis=1)
    df_mean = pd.concat(dataframes).groupby("index").mean()
    df_std = pd.concat(dataframes).groupby("index").std()
    if len(df_mean["L"]) > 151:
        df_mean = df_mean.drop(index=151, axis=1)
        df_std = df_std.drop(index=151, axis=1)
    else:
        pass
    df_mean = df_mean.set_index("time")
    df_std = df_std.set_index("time")
    dE_00_std = df_std["delta_e_2000"]
    dE_00_std_df = dE_00_std.to_frame().set_index(df_mean.index)
    dE_00_std_df["delta_e_2000_min"] = df_mean["delta_e_2000"] - dE_00_std_df["delta_e_2000"]
    dE_00_std_df["delta_e_2000_max"] = dE_00_std_df["delta_e_2000"] + df_mean["delta_e_2000"]
    #print(dE_00_std_df)
    #print(df_mean["delta_e_2000"])

    # generate function from data
    z = np.polyfit(df_mean.index.to_list(), df_mean["delta_e_2000"], 16)
    f = np.poly1d(z)

    y_new = f(x_new)

    # dirty
    y_new[0] = 0

    curve_fit_delta_e_df = pd.DataFrame(y_new, x_new, columns=["dE00"])
    curve_fit_delta_e_df.index.name = "time"

    # axes.plot(df_mean, "o", label="mean", color="green", linewidth=0.3, markersize=0.3)

    result_dfs = [df_mean.tail(1), df_std.tail(1)]

    for i, datum in enumerate(dataframes):
        result_dfs.insert(0, (datum.tail(1)))

    result_concat = pd.concat(result_dfs, ignore_index=True)

    # result_concat["name"] = ""
    # result_concat["name"][5] = "mean"
    # result_concat["name"][6] = "standard deviation"

    result_concat.index.name = "index"

    result_concat = result_concat.drop("time", axis=1)

    # result_concat.to_csv(
    #     "{}/{}.csv".format(output_directory, output_filename),
    #     columns=["name", "dE76", "dE94", "delta_e_2000", "dL", "da", "db"],
    # )

    # axes.legend()

    lab_end_mean_values = df_mean.tail(2)[["db", "da", "dL"]].values[0]
    lab_end_std_values = df_std.tail(2)[["db", "da", "dL"]].values[0]

    return (
        (lab_end_mean_values, lab_end_std_values),
        df_mean, dE_00_std_df,
        result_concat,
        curve_fit_delta_e_df,
    )


def plot_delta_lab_bar_chart(data: tuple[str, tuple[list, list]], axes: axes.Axes, x_axis_min, x_axis_max):
    colors = ["" for _ in range(3)]

    if data[0] == "HF":
        print("now")

    for index, value in enumerate(data[1][0]):
        if value < 0:
            if index == 2:
                colors[2] = "#565656"
                # dark grey
            elif index == 1:
                colors[1] = "#4dd72f"
                # green
            else:
                colors[0] = "#1a71e3"
                # blue
        else:
            if index == 2:
                colors[2] = "#aeaeae"
                # light grey
            elif index == 1:
                colors[1] = "#e3371a"
                # red
            else:
                colors[0] = "#e3c81a"
                # yellow

    # colors.reverse()

    axes.set_title(data[0])
    axes.set_xlim(x_axis_min, x_axis_max)
    axes.yaxis.set_ticks([0, 1, 2], ["db", "da", "dL"])
    axes.barh(
        [0, 1, 2],
        data[1][0],
        height=1,
        color=colors,
    )

    axes.errorbar(
        data[1][0],
        [0, 1, 2],
        xerr=data[1][1],
        fmt=",",
        color="black",
        capsize=10,
        elinewidth=1,
    )


# only execute if this script is called directly
if __name__ == "__main__":
    data_directory = "data/MF_Box2/MF_GA_AQP/"

    # match any .txt file
    filename_pattern = "*.txt"

    files = sorted(glob("{}/{}".format(data_directory, filename_pattern)))

    # match every string that does NOT include "spect"
    filename_regex = re.compile("^((?!spect).)*$")

    files = [i for i in files if filename_regex.match(i)]

    plot_delta_e_2000(files)
