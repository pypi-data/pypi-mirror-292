from typing import Optional
import matplotlib
import matplotlib.gridspec, matplotlib.figure
from mpl_toolkits.axes_grid1 import Divider, Size
import warnings


def make_square_ax(
    fig: matplotlib.figure.Figure,
    ax_width: float,
    left_h: Optional[float] = None,
    bottom_v: Optional[float] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
) -> matplotlib.axes.Axes:
    """Makes a square axes of fixed size in a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to put the axes in
    ax_width : float
        width of the square axes.
    left_h : Optional[float], optional
        Distance of the left axis to the figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    bottom_v : Optional[float], optional
        Distance of the lower axis to the bottom figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    xlabel : Optional[str], optional
        Label for the x-axis, by default None
    ylabel : Optional[str], optional
        Label for the y-axis, by default None
    **kwargs
        Additional keyword arguments like scales, limits etc. for the axes.

    Returns
    -------
    matplotlib.axes.Axes
        axes plaxed in the figure

    Raises
    ------
    ValueError
        if position is not valid.
    UnscientificWarning
        if no xlabel or ylabel is provided. Thanks Simon.
    """
    fig_width, fig_height = fig.get_size_inches()

    if left_h is None:
        left_h = (fig_width - ax_width) / 2
    if bottom_v is None:
        bottom_v = (fig_height - ax_width) / 2

    if ax_width + left_h >= fig_width:
        raise ValueError("Axes width exceeds figure width")
    if ax_width + bottom_v >= fig_height:
        raise ValueError("Axes height exceeds figure height")

    top_v = fig_height - ax_width - bottom_v
    right_h = fig_width - ax_width - left_h
    h = [Size.Fixed(left_h), Size.Scaled(1), Size.Fixed(right_h)]
    v = [Size.Fixed(bottom_v), Size.Scaled(1), Size.Fixed(top_v)]
    div = Divider(fig, (0.0, 0.0, 1.0, 1.0), h, v, aspect=False)
    ax = fig.add_axes(div.get_position(), axes_locator=div.new_locator(nx=1, ny=1))

    if xlabel is not None:
        ax.set_xlabel(xlabel)
    else:
        warnings.warn("Unscientific behavior. No xlabel provided.")

    if ylabel is not None:
        ax.set_ylabel(ylabel)
    else:
        warnings.warn("Unscientific behavior. No ylabel provided.")

    ax.set(**kwargs)
    return ax


def make_rect_ax(
    fig: matplotlib.figure.Figure,
    ax_width: float,
    ax_height: float,
    left_h: Optional[float] = None,
    bottom_v: Optional[float] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    **kwargs,
):
    """Makes a rectangular axes of fixed size in a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to put the axes in.
    ax_width : float
        width of the axes.
    ax_height : float
        height of the axes.
    left_h : Optional[float], optional
        Distance of the left axis to the figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    bottom_v : Optional[float], optional
        Distance of the lower axis to the bottom figure edge.
        Needs to be chosen bigger than the labels and ticks otherwise they will be cut off.
        Optional can be omitted to enable centered positioning, by default None
    xlabel : Optional[str], optional
        Label for the x-axis, by default None
    ylabel : Optional[str], optional
        Label for the y-axis, by default None
    **kwargs
        Additional keyword arguments like scales, limits etc. for the axes.

    Returns
    -------
    matplotlib.axes.Axes
        axes plaxed in the figure

    Raises
    ------
    ValueError
        if position is not valid.
    UnscientificWarning
        if no xlabel or ylabel is provided. Thanks Simon.
    """
    fig_width, fig_height = fig.get_size_inches()

    if left_h is None:
        left_h = (fig_width - ax_width) / 2
    if bottom_v is None:
        bottom_v = (fig_height - ax_width) / 2

    if ax_width + left_h >= fig_width:
        raise ValueError("Axes width exceeds figure width")
    if ax_height + bottom_v >= fig_height:
        raise ValueError("Axes height exceeds figure height")

    top_v = fig_height - ax_height - bottom_v
    right_h = fig_width - ax_width - left_h
    h = [Size.Fixed(left_h), Size.Scaled(1), Size.Fixed(right_h)]
    v = [Size.Fixed(bottom_v), Size.Scaled(1), Size.Fixed(top_v)]
    div = Divider(fig, (0.0, 0.0, 1.0, 1.0), h, v, aspect=False)
    ax = fig.add_axes(div.get_position(), axes_locator=div.new_locator(nx=1, ny=1))

    if xlabel is not None:
        ax.set_xlabel(xlabel)
    else:
        warnings.warn("Unscientific behavior. No xlabel provided.")

    if ylabel is not None:
        ax.set_ylabel(ylabel)
    else:
        warnings.warn("Unscientific behavior. No ylabel provided.")

    ax.set(**kwargs)

    return ax


def make_square_axs(
    fig: matplotlib.figure.Figure,
    left_h: float,
    bottom_v: float,
    ax_width: float,
    ax_layout: tuple[int, int] = (1, 1),
    v_sep: float = 0.05,
    h_sep: float = 0.05,
):
    fig_width = float(fig.get_figwidth())
    fig_height = float(fig.get_figheight())

    n_rows, n_cols = ax_layout
    n_row_skips = n_rows - 1
    n_col_skips = n_cols - 1

    if (n_rows * ax_width) + left_h + (n_row_skips * v_sep) >= fig_width:
        raise ValueError(
            "Axes widths exceed figure width. Try adjusting v_sep or fig_height."
        )
    if (n_cols * ax_width) + bottom_v + (n_col_skips * h_sep) >= fig_height:
        raise ValueError(
            "Axes heights exceed figure height. Try adjusting h_sep or fig_width."
        )

    h_frac = left_h / fig_width
    v_frac = bottom_v / fig_height

    axs_width = n_cols * ax_width + n_col_skips * h_sep
    axs_width_frac = axs_width / fig_width
    axs_height = n_rows * ax_width + n_row_skips * v_sep
    axs_height_frac = axs_height / fig_height

    total_height_frac = axs_height_frac + v_frac
    total_width_frac = axs_width_frac + h_frac

    gs = fig.add_gridspec(
        nrows=n_rows,
        ncols=n_cols,
        wspace=h_frac,
        hspace=v_frac,
        left=h_frac,
        bottom=v_frac,
        right=total_width_frac,
        top=total_height_frac,
    )

    for i in range(n_rows):
        for j in range(n_cols):
            fig.add_subplot(gs[i, j])
