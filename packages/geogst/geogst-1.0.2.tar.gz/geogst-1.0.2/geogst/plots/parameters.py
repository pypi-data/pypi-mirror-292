
import numbers
from enum import Enum

from geogst.core.inspections.errors import *


class PointLikePlotTypes(Enum):
    POINTS = 1
    ATTITUDES = 2


# General figure

FIG_WIDTH_INCHES_DEFAULT = 8.5
FIG_HEIGHT_INCHES_DEFAULT = 5.0
FIG_Z_PADDING_DEFAULT = 0.2

# Grids

GRID_COLORMAP_DEFAULT: str = "gist_earth"
GRID_USE_HILLSHADE_DEFAULT: bool = True
GRID_HS_VERT_EXAGG_DEFAULT: numbers.Real = 1.0
GRID_HS_BLEND_MODE_DEFAULT: str = 'overlay'  # one of 'hillshade', 'hsv', 'overlay', 'soft'
GRID_HS_LIGHT_SOURCE_AZIM_DEFAULT: numbers.Real = 315.0
GRID_HS_LIGHT_SOURCE_DEGR_DEFAULT: numbers.Real = 45.0
GRID_PLOT_COLORBAR_DEFAULT: bool = True

# Profiles

TOPOPROF_ASPECT_DEFAULT = 1
TOPOPROF_MAX_PTS_NUM_DEFAULT = 1e4
TOPOPROF_LINE_COLOR_DEFAULT = 'grey'
TOPOPROF_SUPERPOSED_CHOICE_DEFAULT = False

# General

# lines
LN_MARKER_STYLE_DEFAULT: str = '-'
LN_WIDTH_STYLE_DEFAULT: numbers.Real = 0.95

# labels
LBLS_PLOT_DEFAULT: bool = True
LBLS_CONTENT_DEFAULT: str = 'key'  # values: 'key', 'index', 'orientation', 'index-orientation',


# Points/Attitudes

PTATT_COLOR_DEFAULT = "red"
PTATT_MARKER_DEFAULT = 'o'
PTATT_MARKER_SIZE_DEFAULT = 6
PTATT_ALPHA_SIZE_DEFAULT = 1.0
PTATT_PLOT_TYPE_DEFAULT = PointLikePlotTypes.POINTS
PTATT_LABELS_ORIENTIONS_DEFAULT = True
PTATT_LABELS_IDS_DEFAULT = False

# Lines intersections

LNINT_COLOR_DEFAULT = "red"
LNINT_SIZE_DEFAULT = 3
LNINT_ALPHA_DEFAULT = 0.5
LNINT_LABELS_DEFAULT = True
LNINT_ADDITIONAL_COLORS = [
    "red",
    "green",
    "blue",
    "yellow",
    "hotpink",
    "darkseagreen",
    "darkgoldenrod",
    "darkviolet",
    "powderblue",
    "yellowgreen",
    "palevioletred",
    "seagreen",
    "darkturquoise",
    "beige",
    "darkkhaki",
    "magenta",
    "cyan",
    "chartreuse"
]

# Polygons intersections

PLINT_LINE_WIDTH_DEFAULT = 2
PLINT_LABELS_DEFAULT = True
PLINT_LEGEND_DEFAULT = True


max_parallel_profiles_number = 20


class FigureParams:

    def __init__(
            self,
            width: numbers.Real = FIG_WIDTH_INCHES_DEFAULT,
            height: numbers.Real = FIG_HEIGHT_INCHES_DEFAULT,
    ):
        self.width = width
        self.height = height


class AxisPlotParams:

    def __init__(self,
                 z_min: Union[type(None), numbers.Real] = -1000,
                 z_max: Union[type(None), numbers.Real] = 1000,
                 vertical_exaggeration: numbers.Real = TOPOPROF_ASPECT_DEFAULT,
                 grid=True,  #
                 grid_color='tan',  #
                 grid_linestyle='--',  #
                 grid_linewidth=0.2,  #
                 breaklines=True,  #
                 breaklines_color='grey',  #
                 breaklines_width=1.05,  #
                 breaklines_style='dotted'  #
                 ):

        self.z_min = z_min
        self.z_max = z_max
        self.vertical_exaggeration = vertical_exaggeration
        self.grid = grid
        self.grid_color = grid_color
        self.grid_linestyle = grid_linestyle
        self.grid_linewidth = grid_linewidth
        self.breaklines = breaklines
        self.breaklines_color = breaklines_color
        self.breaklines_width = breaklines_width
        self.breaklines_style = breaklines_style


class GenericPlotParams:

    def __init__(
            self,
            marker: Union[type(None), str] = PTATT_MARKER_DEFAULT,
            markersize: numbers.Real = PTATT_MARKER_SIZE_DEFAULT,
            color: Union[type(None), str] = PTATT_COLOR_DEFAULT,
            linestyle: Union[type(None), str] = LN_MARKER_STYLE_DEFAULT,
            width: Union[type(None), numbers.Real] = LN_WIDTH_STYLE_DEFAULT,
            alpha: numbers.Real = PTATT_ALPHA_SIZE_DEFAULT,
            plot_type: PointLikePlotTypes = PTATT_PLOT_TYPE_DEFAULT,
            labels: bool = LBLS_PLOT_DEFAULT,
            label_orientations: bool = PTATT_LABELS_ORIENTIONS_DEFAULT,
            label_ids: bool = PTATT_LABELS_IDS_DEFAULT,
    ):

        self.marker = marker
        self.markersize = markersize
        self.color = color
        self.linestyle = linestyle
        self.width = width
        self.alpha = alpha
        self.plot_type = plot_type
        self.labels = labels
        self.label_orientations = label_orientations
        self.label_ids = label_ids


class ElevationPlotParams(GenericPlotParams):

    def __init__(self,
        color: Union[type(None), str] = "darkgrey",
        width: numbers.Real = 1.0,
        alpha: numbers.Real = 1.0,
    ):

        super(ElevationPlotParams, self).__init__(
            marker=None,
            color=color,
            width=width,
            alpha=alpha,
            labels=False,
        )


class PointPlotParams(GenericPlotParams):

    def __init__(self,
        marker: Union[type(None), str] = 'o',
        markersize: numbers.Real = 3,
        color: Union[type(None), str] = "red",
        alpha: numbers.Real = 0.85,
        labels: bool = False,
    ):

        super(PointPlotParams, self).__init__(
            marker=marker,
            markersize=markersize,
            color=color,
            linestyle=None,
            width=None,
            alpha=alpha,
            plot_type=PointLikePlotTypes.POINTS,
            labels=labels,
        )


class AttitudePlotParams(GenericPlotParams):
    """
    Attitude projection params.
    """

    def __init__(self,
                 marker: Union[type(None), str] = 'o',
                 markersize: numbers.Real = 3,
                 color: Union[type(None), str] = "red",
                 alpha: numbers.Real = 0.85,
                 labels: bool = True,
                 label_orientations: bool = PTATT_LABELS_ORIENTIONS_DEFAULT,
                 label_ids: bool = PTATT_LABELS_IDS_DEFAULT,
                 ):

        super(AttitudePlotParams, self).__init__(
            marker=marker,
            markersize=markersize,
            color=color,
            linestyle=None,
            width=None,
            alpha=alpha,
            plot_type=PointLikePlotTypes.ATTITUDES,
            labels=labels,
            label_orientations=label_orientations,
            label_ids=label_ids
        )


class MapPlotParams:

    def __init__(
        self,
        map_zoom: numbers.Real = 1,
):

        self.map_zoom = map_zoom


class GridPlotParams:

    def __init__(
        self,
        grid_colormap: str = GRID_COLORMAP_DEFAULT,
        hillshade: bool = GRID_USE_HILLSHADE_DEFAULT,
        hs_vert_exagg: numbers.Real = GRID_HS_VERT_EXAGG_DEFAULT,
        hs_blend_mode: str = GRID_HS_BLEND_MODE_DEFAULT,  # one of 'hillshade', 'hsv', 'overlay', 'soft'
        hs_light_source_azim: numbers.Real = GRID_HS_LIGHT_SOURCE_AZIM_DEFAULT,
        hs_light_source_degr: numbers.Real = GRID_HS_LIGHT_SOURCE_DEGR_DEFAULT,
        plot_colorbar: bool = GRID_PLOT_COLORBAR_DEFAULT,
    ):

        self.grid_colormap = grid_colormap
        self.hillshade = hillshade
        self.hs_vert_exagg = hs_vert_exagg
        self.hs_blend_mode = hs_blend_mode
        self.hs_light_source_azim = hs_light_source_azim
        self.hs_light_source_degr = hs_light_source_degr
        self.plot_colorbar = plot_colorbar


class StereonetStyleParams:

    def __init__(
        self,
        line_color: Union[type(None), str] = None,
        line_style: Union[type(None), str] = None,
        line_width: Union[type(None), str] = None,
        line_transp: Union[type(None), str] = None,
        marker_color: Union[type(None), str] = None,
        marker_style: Union[type(None), str] = None,
        marker_size: Union[type(None), str] = None,
        marker_transp: Union[type(None), str] = None,
    ):

        self.line_color = line_color if line_color is not None else "#FF0000"
        self.line_style = line_style if line_style is not None else "solid"
        self.line_width = line_width if line_width is not None else "1 pt(s)"
        self.line_transp = line_transp if line_transp is not None else "0%"
        self.marker_color = marker_color if marker_color is not None else "#0000FF"
        self.marker_style = marker_style if marker_style is not None else "circle"
        self.marker_size = marker_size if marker_size is not None else "6 pt(s)"
        self.marker_transp = marker_transp if marker_transp is not None else "0%"
