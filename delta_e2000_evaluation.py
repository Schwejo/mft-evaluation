import pandas as pd
import matplotlib.pyplot as plot
from pathlib import Path
import numpy as np

'''hallo'''
def plot_delta_e_2000(data: list[pd.DataFrame], output: Path) -> None:
    figure = plot.figure()
    axes = figure.subplots()
    # axes.set_ylabel("Reflectance [%]")
    # axes.set_ylim(0, 80)
    # axes.set_xlabel("Wavelength [nm]")
    # axes.set_xlim(420, 720)
    axes.grid(alpha=0.5)

    function_values_dfs = []

    for i, datum in enumerate(data):
        datum = datum.set_index("time")

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
    figure.savefig(output, dpi=1200)


def evaluate_delta_e2000(files: list[Path], output: Path):
    # list that holds a dataframe for each measurement file
    dataframes = []

    delta_e2000_curvefit_dataframes = []

    # make x values to evaluate all functions at to make them comparable
    # TODO read stop value from the measurement file
    x_values_uniform = np.linspace(0, 300, 300, dtype=int)

    for file in files:
        df = pd.read_csv(
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
            usecols=["time", "delta_e_2000"],
            index_col="time",
        )

        dataframes.append(df)

        # generate function from data
        fit = np.polyfit(df.index.to_list(), df["delta_e_2000"], 16)
        f = np.poly1d(fit)

        y_values = f(x_values_uniform)

        df_delta_e2000_curvefit = pd.DataFrame(
            y_values, x_values_uniform, columns=["delta_e_2000"]
        )

        df_delta_e2000_curvefit.index.name = "time"

        delta_e2000_curvefit_dataframes.append(df_delta_e2000_curvefit)

    df_delta_e200_mean = (
        pd.concat(delta_e2000_curvefit_dataframes).groupby("time").mean()
    )

    print(df_delta_e200_mean)

    # plot_delta_e_2000(
    #     dataframes, output.joinpath("{}_delta_e2000.png".format(files[0].stem))
    # )
