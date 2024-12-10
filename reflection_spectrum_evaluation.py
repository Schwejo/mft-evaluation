import pandas as pd
import matplotlib.pyplot as plot
from pathlib import Path


def plot_first_and_last_measurement(data: pd.DataFrame, output: Path) -> None:
    figure = plot.figure()
    axes = figure.subplots()
    axes.set_ylabel("Reflectance [%]")
    axes.set_ylim(0, 80)
    axes.set_xlabel("Wavelength [nm]")
    axes.set_xlim(420, 720)
    axes.grid(alpha=0.5)
    axes.plot(
        data["first_measurement_mapped"],
        label="First Measurement",
        color="green",
        linewidth=0.8,
    )
    axes.plot(
        data["last_measurement_mapped"],
        label="Last Measurement",
        color="red",
        linewidth=0.8,
    )
    axes.legend()
    figure.savefig(output, dpi=1200)


def evaluate_reflection_spectrum(files: list[Path], output: Path):
    # list that holds a dataframe for each measurement file
    dataframes = []

    for file in files:
        # read csv headers to get index of last column
        last_column_index = len(pd.read_csv(file, sep="\t", nrows=0).columns) - 1

        df = pd.read_csv(
            file,
            sep="\t",
            header=0,
            usecols=[0, 1, 3, last_column_index],
            names=["wavelength", "white_std", "first_measurement", "last_measurement"],
            index_col="wavelength",
        )

        # add columns with result of this formula without altering any other column
        df["first_measurement_mapped"] = df["first_measurement"] / df["white_std"] * 100
        df["last_measurement_mapped"] = df["last_measurement"] / df["white_std"] * 100

        dataframes.append(df)

    # remove unused columns
    dataframes_stripped = map(
        lambda frame: frame[["first_measurement_mapped", "last_measurement_mapped"]],
        dataframes,
    )

    # 1: Concatenate all dataframes into one, causing each index (wavelength) to be set multiple times.
    # 2: Group by index column (wavelength) to restore index integrity.
    # 3: Calculate mean over all columns except the one grouped by.
    df_mean = pd.concat(dataframes_stripped).groupby("wavelength").mean()

    plot_first_and_last_measurement(
        dataframes[0], output.joinpath("{}_single.png".format(files[0].stem))
    )

    plot_first_and_last_measurement(
        df_mean, output.joinpath("{}_mean.png".format(files[0].stem))
    )
