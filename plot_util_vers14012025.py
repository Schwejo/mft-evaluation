import matplotlib.pyplot as plot
import matplotlib.figure as figure
import matplotlib.axes as axes
import matplotlib.gridspec as grid


def init_figure(
    figure: figure.Figure, nrows: int = 1, ncols: int = 1, **kwags
) -> grid.GridSpec:
    """
    Clear figure and add new grid spec
    """
    figure.clear()
    figure.set_layout_engine("constrained")
    return figure.add_gridspec(nrows, ncols, wspace=0.1, hspace=0.2)


def add_grid(axes: axes.Axes) -> None:
    axes.grid(alpha=0.4)
