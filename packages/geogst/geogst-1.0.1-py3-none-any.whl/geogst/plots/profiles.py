import numbers
from functools import singledispatch
import collections

import os.path
from warnings import warn

import imageio

import matplotlib
from matplotlib import pyplot as plt, axis, gridspec
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from bokeh.plotting import figure, output_notebook, show

from geogst.core.geometries.grids.rasters import *
from geogst.core.geometries.points import *
from geogst.core.profiles.geoprofiles import *
from geogst.core.profiles.profilers import *
from geogst.core.profiles.profiletraces import *
from geogst.core.profiles.profiletraces import *
from geogst.plots.parameters import *

from geogst.plots.maps import subplot_map


def plot_points_as_pointtraces(
    fig,
    points_projections: Dict,
    **kwargs,
):

    point_projections_params = kwargs.get("point_projections_params", None)

    if point_projections_params is None:
        point_projections_params = PointPlotParams()

    projected_ids = []
    projected_s = []
    projected_z = []
    projected_dist = []

    for rec_id, point_projection in points_projections.items():
        projected_ids.append(rec_id)
        projected_s.append(point_projection.s)
        projected_z.append(point_projection.z)
        projected_dist.append(point_projection.dist)

    axes = fig.gca()

    axes.plot(
        projected_s,
        projected_z,
        marker=point_projections_params.marker,
        color=point_projections_params.color,
        markersize=point_projections_params.markersize,
        alpha=point_projections_params.alpha,
        linestyle='None',
    )

    return


def plot_points_from_dicts(
    fig,
    points_projections: Dict,
    section_length: numbers.Real,
    **kwargs,
):

    #print(f"Point projections (inside): {points_projections}")

    for category, dataset in points_projections.items():

        # parameters

        points_projections_params = kwargs.pop(category, GenericPlotParams())

        if points_projections_params.plot_type == PointLikePlotTypes.POINTS:

            projected_categories = []
            projected_s = []
            projected_z = []
            projected_dist = []

            for rec_id, point_projection in dataset.items():
                projected_categories.append(rec_id)
                projected_s.append(point_projection.s)
                projected_z.append(point_projection.z)
                projected_dist.append(point_projection.dist)

            axes = fig.gca()

            color = points_projections_params.color
            axes.plot(
                projected_s,
                projected_z,
                marker=points_projections_params.marker,
                color=color,
                markersize=points_projections_params.markersize,
                alpha=points_projections_params.alpha,
                linestyle='None',
            )

            if points_projections_params.labels:

                for category, s, z in zip(
                    projected_categories,
                    projected_s,
                    projected_z):

                    label = f"{category}"

                    axes.annotate(
                        label,
                        (s + 75, z + 75),
                        color=color,
                        fontsize=6,
                    )

        elif points_projections_params.plot_type == PointLikePlotTypes.ATTITUDES:

            projected_categories = []
            projected_s = []
            projected_z = []
            src_dip_dirs = []
            src_dip_angs = []

            for rec_id, profile_attitude in dataset.items():
                projected_categories.append(rec_id)
                projected_s.append(profile_attitude.s)
                projected_z.append(profile_attitude.z)
                src_dip_dirs.append(profile_attitude.src_dip_dir)
                src_dip_angs.append(profile_attitude.src_dip_ang)

            axes = fig.gca()
            vertical_exaggeration = axes.get_aspect()

            axes.plot(
                projected_s,
                projected_z,
                marker=points_projections_params.marker,
                color=points_projections_params.color,
                markersize=points_projections_params.markersize,
                alpha=points_projections_params.alpha,
                linestyle='None',
            )

            # plot segments representing structural data

            for _, structural_attitude in dataset.items():
                structural_segment_s, structural_segment_z = structural_attitude.create_segment_for_plot(
                    section_length,
                    vertical_exaggeration)

                fig.gca().plot(
                    structural_segment_s,
                    structural_segment_z,
                    '-',
                    color=points_projections_params.color,
                    alpha=points_projections_params.alpha,
                )

            if points_projections_params.label_orientations or points_projections_params.label_ids:

                for rec_id, src_dip_dir, src_dip_ang, s, z in zip(
                        projected_categories,
                        src_dip_dirs,
                        src_dip_angs,
                        projected_s,
                        projected_z):

                    if points_projections_params.label_orientations and points_projections_params.label_ids:
                        label = f"{rec_id}-{src_dip_dir:05.01F}/{src_dip_ang:04.01F}"
                    elif points_projections_params.label_orientations:
                        label = f"{src_dip_dir:05.01F}/{src_dip_ang:04.01F}"
                    else:
                        label = f"{rec_id}"

                    axes.annotate(label, (s + 15, z + 15))


def process_points_projections(
    fig,
    points_projections: Dict,
    section_length: numbers.Real,
    **kwargs,
):

    if not isinstance(points_projections, dict):
        print(
            f"Warning: Points projections are not of type 'Dict' but {type(points_projections)}")
        return

    values = points_projections.values()
    value_types = set(map(lambda value: type(value), values))
    if len(value_types) != 1:
        print(
            f"Warning: Points projections values must be of a unique type {len(value_types)} found"
        )
        return

    point_projection_type = value_types.pop()

    if point_projection_type == PointTrace:

        plot_points_as_pointtraces(
            fig,
            points_projections,
            **kwargs,
        )

    elif point_projection_type == collections.defaultdict:

        plot_points_from_dicts(
            fig,
            points_projections,
            section_length,
            **kwargs,
        )

    else:

        print(f"Got non-managed point projection type: {point_projection_type}")

    return


@singledispatch
def profiles(
    obj,
    **kargs
): #-> Optional[Figure]:
    """

    :param obj:
    :param kargs:
    :return:
    """

    fig = kargs.pop("fig", None)
    aspect = kargs.pop("aspect", 1)
    width = kargs.pop("width", FIG_WIDTH_INCHES_DEFAULT)
    height = kargs.pop("height", FIG_HEIGHT_INCHES_DEFAULT)

    if fig is None:

        fig, ax = plt.subplots()
        fig.set_size_inches(width, height)

        ax.set_aspect(aspect)

    else:

        plt.gca()

    #return fig


@profiles.register(ZTrace)
def _(
    xyarrays: ZTrace,
    **kargs
): #-> Optional[Figure]:

    fig = kargs.pop("fig", None)
    width = kargs.pop("width", FIG_WIDTH_INCHES_DEFAULT)
    height = kargs.pop("height", FIG_HEIGHT_INCHES_DEFAULT)
    z_min = kargs.pop("z_min", None)
    z_max = kargs.pop("z_max", None)
    aspect = kargs.pop("aspect", None)
    grid = kargs.pop("grid", False)
    grid_color = kargs.pop("grid_color", 'tan')
    grid_width = kargs.pop("grid_width", 0.2)
    breaklines = kargs.pop("breaklines", True)
    breaklines_color = kargs.pop("breaklines_color", 'yellow')
    breaklines_width = kargs.pop("breaklines_width", 1.5)
    breaklines_style = kargs.pop("breaklines_style", 'dotted')
    file_path = kargs.pop("file_path", None)

    if z_min is None or z_max is None:
        z_range = xyarrays.y_max() - xyarrays.y_min()
        z_min = xyarrays.y_min() - FIG_Z_PADDING_DEFAULT * z_range
        z_max = xyarrays.y_max() + FIG_Z_PADDING_DEFAULT * z_range

    if np.isnan(z_min) or np.isnan(z_max):
        return

    if fig is None:

        fig = plt.figure()
        fig.set_size_inches(width, height)

    ax = fig.add_subplot()

    if aspect is not None:
        ax.set_aspect(aspect)

    if z_min is not None or z_max is not None:
        ax.set_ylim([z_min, z_max])

    if grid:
        ax.grid(
            True,
            linestyle='-',
            color=grid_color,
            linewidth=grid_width)

    ax.plot(
        xyarrays.x_arr(),
        xyarrays.y_arr(),
        **kargs
    )

    if breaklines:
        bottom, top = ax.get_ylim()
        ax.vlines(
            xyarrays.x_breaks(),
            bottom,
            top,
            color=breaklines_color,
            linewidth=breaklines_width,
            linestyles=breaklines_style
        )

    if file_path is not None:
        plt.savefig(file_path)


@profiles.register(ZTraces)
def _(
    z_profiles: ZTraces,
    **kargs
): # -> Optional[Figure]:

    fig = kargs.pop("fig", None)
    width = kargs.pop("width", FIG_WIDTH_INCHES_DEFAULT)
    height = kargs.pop("height", FIG_HEIGHT_INCHES_DEFAULT)
    z_min = kargs.pop("z_min", None)
    z_max = kargs.pop("z_max", None)
    aspect = kargs.pop("aspect", None)

    grid = kargs.pop("grid", False)
    grid_color = kargs.pop("grid_color", 'tan')
    grid_width = kargs.pop("grid_width", 0.2)

    breaklines = kargs.pop("breaklines", True)
    breaklines_color = kargs.pop("breaklines_color", 'yellow')
    breaklines_width = kargs.pop("breaklines_width", 1.5)
    breaklines_style = kargs.pop("breaklines_style", 'dotted')

    single_plot = kargs.pop("single_plot", False)
    file_path = kargs.pop("file_path", None)

    if z_min is None or z_max is None:
        z_range = z_profiles.z_max() - z_profiles.z_min()
        z_min = z_profiles.z_min() - FIG_Z_PADDING_DEFAULT * z_range
        z_max = z_profiles.z_max() + FIG_Z_PADDING_DEFAULT * z_range

    if np.isnan(z_min) or np.isnan(z_max):
        return

    if fig is None:
        if not single_plot:
            fig, axs = plt.subplots(z_profiles.num_profiles())
            fig.set_size_inches(width, height * z_profiles.num_profiles() * 0.9)
        else:
            fig, axs = plt.subplots()
            fig.set_size_inches(width, height)
    else:
        axs = fig.axes

    if aspect is None:
        aspect = 1

    if grid:
        axs.grid(
            True,
            linestyle='-',
            color=grid_color,
            linewidth=grid_width)

    if not single_plot:
        for ndx in range(z_profiles.num_profiles()):
            z_prof = z_profiles[ndx]
            ax = axs[ndx]
            ax.set_aspect(aspect)
            if z_min is not None or z_max is not None:
                ax.set_ylim([z_min, z_max])
            ax.plot(
                z_prof.x_arr(),
                z_prof.y_arr(),
                ** kargs
            )
    else:
        axs.set_aspect(aspect)
        if z_min is not None or z_max is not None:
            axs.set_ylim([z_min, z_max])
        for ndx in range(z_profiles.num_profiles()):
            z_prof = z_profiles[ndx]
            axs.plot(
                z_prof.x_arr(),
                z_prof.y_arr(),
                ** kargs
            )

    if breaklines:

        if not single_plot:

            for ndx in range(z_profiles.num_profiles()):
                z_prof = z_profiles[ndx]
                ax = axs[ndx]

                bottom, top = ax.get_ylim()
                ax.vlines(
                    z_profiles.s_breaks(),
                    bottom,
                    top,
                    color=breaklines_color,
                    linewidth=breaklines_width,
                    linestyles=breaklines_style
                )

        else:

            bottom, top = axs.get_ylim()
            axs.vlines(
                z_profiles.s_breaks(),
                bottom,
                top,
                color=breaklines_color,
                linewidth=breaklines_width,
                linestyles=breaklines_style
            )

    if file_path is not None:
        plt.savefig(file_path)


@profiles.register(GeoProfile)
def _(
    geoprofile: GeoProfile,
    **kwargs
): # -> Union[type(None), Figure]:
    """
    Plot a single geological profile.

    :param geoprofile: the geoprofile to plot
    :return: the figure.
    """

    if not geoprofile.has_topography():
        print("Warning: geoprofile has no topography defined")
        return

    # keyword parameters extraction

    fig = kwargs.pop("fig", None)
    width = kwargs.pop("width", None)
    height = kwargs.pop("height", None)
    spec = kwargs.pop("spec", None)

    profile_ndx = kwargs.pop("profile_ndx", 0)
    superposed = kwargs.pop("superposed", TOPOPROF_SUPERPOSED_CHOICE_DEFAULT)

    # axis params

    axis_params = kwargs.pop("axis_params", AxisPlotParams())
    z_min = axis_params.z_min
    z_max = axis_params.z_max
    aspect = axis_params.vertical_exaggeration

    # elevation parameters

    elevation_params = kwargs.pop("elevation_params", ElevationPlotParams())

    # line intersections parameters

    line_intersections_style = kwargs.pop("line_intersections", PointPlotParams())

    # polygons intersections parameters

    polygon_intersections = kwargs.pop("polygon_intersections", None)
    polygon_intersections_linewidth = PLINT_LINE_WIDTH_DEFAULT  #if polygon_intersections is None else polygon_intersections.get("line_width", PLINT_LINE_WIDTH_DEFAULT)
    polygon_intersections_colors = polygon_intersections  #None if polygon_intersections is None else polygon_intersections.get("colors", None)
    polygon_inters_marker_label = PLINT_LABELS_DEFAULT  #if polygon_intersections is None else polygon_intersections.get("linelabels", PLINT_LABELS_DEFAULT)
    polygon_inters_legend_on = PLINT_LEGEND_DEFAULT  #if polygon_intersections is None else polygon_intersections.get("legend", PLINT_LEGEND_DEFAULT)

    # figure definitions

    if fig is None:

        fig = plt.figure()
        fig.set_size_inches(width, height)

    if superposed:

        ax = fig.add_axes(
            [0.1, 0.1, 0.8, 0.8]
        )
    elif spec is not None:
        ax = fig.add_subplot(
            spec[profile_ndx, 0]
        )
    else:
        ax = fig.add_subplot()

    ax.set_aspect(aspect)

    # profile parameters

    section_length = geoprofile.length_2d()

    # definition of elevation range

    if z_min is None or z_max is None:
        z_range = geoprofile.z_max() - geoprofile.z_min()
        z_min = geoprofile.z_min() - FIG_Z_PADDING_DEFAULT * z_range
        z_max = geoprofile.z_max() + FIG_Z_PADDING_DEFAULT * z_range

    if np.isnan(z_min) or np.isnan(z_max):
        print(f"z min = {z_min}, z_max = {z_max}")
        return

    if z_min is not None or z_max is not None:
        ax.set_ylim([z_min, z_max])

    # plot of elevation profiles

    if geoprofile._topo_profile:

        if superposed:
            linecolor = LNINT_ADDITIONAL_COLORS[profile_ndx % len(LNINT_ADDITIONAL_COLORS)]
        else:
            if elevation_params.color is None:
                linecolor = 'peru'
            elif isinstance(elevation_params.color, str):
                linecolor = elevation_params.color
            else:
                linecolor = 'peru'

        if axis_params.grid:
            ax.grid(
                True,
                color=axis_params.grid_color,
                linestyle=axis_params.grid_linestyle,
                linewidth=axis_params.grid_linewidth)

        ax.plot(
            geoprofile._topo_profile.x_arr(),
            geoprofile._topo_profile.y_arr(),
            color=linecolor,
            linestyle=elevation_params.linestyle,
            linewidth=elevation_params.width
        )

        ax.set_ylim([z_min, z_max])
        ax.set_aspect(aspect)

        if axis_params.breaklines:

            bottom, top = ax.get_ylim()
            ax.vlines(
                geoprofile._topo_profile.x_breaks(),
                bottom,
                top,
                color=axis_params.breaklines_color,
                linewidth=axis_params.breaklines_width,
                linestyles=axis_params.breaklines_style
            )

    # plot of polygons intersections

    if geoprofile._polygons_intersections:

        if not geoprofile._topo_profile:

            print('Warning: topographic profile is not defined, so intersections cannot be plotted')

        elif not polygon_intersections:

            print('Warning: polygon intersection styles are not defined, so intersections cannot be plotted')

        else:

            for ndx, polygon_intersection_element in enumerate(geoprofile._polygons_intersections):

                polygon_intersection_id = polygon_intersection_element.id
                polygon_intersection_subparts = polygon_intersection_element.arrays

                for s_range in polygon_intersection_subparts:

                    s_start = s_range[0]
                    s_end = s_range[1] if len(s_range) > 1 else None
                    s_mid = s_start if s_end is None else (s_start + s_end) / 2

                    plot_symbol = '-' if len(s_range) > 1 else 'o'

                    s_vals = geoprofile._topo_profile.x_subset(
                        s_start,
                        s_end
                    )

                    if s_vals is None:
                        continue

                    z_vals = geoprofile._topo_profile.ys_from_x_range(
                        s_start,
                        s_end
                    )

                    if z_vals is None:
                        continue

                    fig.gca().plot(
                        s_vals,
                        z_vals,
                        plot_symbol,
                        color=polygon_intersections_colors[str(polygon_intersection_id)],
                        linewidth=polygon_intersections_linewidth
                    )

                    if polygon_inters_marker_label:

                        fig.gca().annotate(
                            f"{polygon_intersection_id}",
                            (s_mid, z_min + int((z_max - z_min) / 20)),
                            color=polygon_intersections_colors[str(polygon_intersection_id)]
                        )

            if polygon_inters_legend_on:

                legend_patches = []
                for polygon_code in polygon_intersections_colors:
                    legend_patches.append(mpatches.Patch(color=polygon_intersections_colors[polygon_code], label=str(polygon_code)))

                # from: https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
                # Shrink current axis by 20%
                box = ax.get_position()
                ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

                # Put a legend to the right of the current axis
                ax.legend(
                    handles=legend_patches,
                    loc='center left',
                    bbox_to_anchor=(1, 0.5)
                )

    # plot of line intersections

    if geoprofile._lines_intersections:

        if not geoprofile._topo_profile:

            warn('Topographic profile is not defined, so intersections cannot be plotted')

        else:

            for ndx, line_intersection_element in enumerate(geoprofile._lines_intersections):

                line_intersection_id = line_intersection_element.id
                line_intersection_subparts = line_intersection_element.arrays

                for s_range in line_intersection_subparts:

                    s_start = s_range[0]
                    s_end = s_range[1] if len(s_range) > 1 else None
                    plot_symbol = '-' + line_intersections_style.marker if len(s_range) > 1 else line_intersections_style.marker

                    s_vals = geoprofile._topo_profile.x_subset(
                        s_start,
                        s_end
                    )

                    z_vals = geoprofile._topo_profile.ys_from_x_range(
                        s_start,
                        s_end
                    )

                    if s_vals is None or z_vals is None:
                        print(f"Warning: null intersection data present in profile {profile_ndx+1}")
                        continue

                    if len(s_vals) != len(z_vals):
                        print(f"Error with numerosity of line intersection data to plot for profile {profile_ndx+1}: s values are {len(s_vals)} while z_values are {len(z_vals)}")
                        continue

                    parsed_s_vals, parsed_z_vals = [], []

                    for s_val, z_val in zip(s_vals, z_vals):
                        if not isinstance(s_val, (numbers.Real, numbers.Integral)) or not isinstance(z_val, (numbers.Real, numbers.Integral)):
                            print(f"Discarding s-z couple for profile {profile_ndx+1} line intersections plot: s -> {s_val} z -> {z_val}")
                            continue
                        if not isfinite(s_val) or not isfinite(z_val):
                            print(f"Discarding s-z couple for profile {profile_ndx+1} line intersections plot: s -> {s_val} z -> {z_val}")
                            continue
                        parsed_s_vals.append(s_val)
                        parsed_z_vals.append(z_val)

                    fig.gca().plot(
                        parsed_s_vals,
                        parsed_z_vals,
                        plot_symbol,
                        color=line_intersections_style.color,
                        markersize=line_intersections_style.markersize,
                        alpha=line_intersections_style.alpha,
                        linestyle='None',
                    )

                    if line_intersections_style.labels:

                        fig.gca().annotate(
                            f"{line_intersection_id}",
                            (s_vals[-1], z_vals[-1] + 40),
                            color=line_intersections_style.color,
                            alpha=line_intersections_style.alpha,
                        )

    # plot of point projections

    if geoprofile._points_projections:

        process_points_projections(
            fig,
            geoprofile._points_projections,
            section_length,
            **kwargs
        )
            # plot of traces with attitudes intersections

    if geoprofile._lines_intersections_with_attitudes:

        section_length = geoprofile.length_2d()

        projected_ids = []
        projected_s = []
        projected_z = []
        src_dip_dirs = []
        src_dip_angs = []

        for rec_id, profile_attitudes in geoprofile._lines_intersections_with_attitudes.items():

            for profile_attitude in profile_attitudes:
                projected_ids.append(rec_id)
                projected_s.append(profile_attitude.s)
                projected_z.append(geoprofile._topo_profile.y_linear_interpol(profile_attitude.s))
                src_dip_dirs.append(profile_attitude.src_dip_dir)
                src_dip_angs.append(profile_attitude.src_dip_ang)

        axes = fig.gca()
        vertical_exaggeration = axes.get_aspect()

        line_attitudes_projections_params = GenericPlotParams(
            color="yellow",
            markersize=8,
            alpha=0.4,
            label_orientations=False
        )

        axes.plot(
            projected_s,
            projected_z,
            marker="o",  #line_attitudes_projections_params.marker,
            color="yellow",  #qcolor2rgbmpl(line_attitudes_projections_params.color) if isinstance(line_attitudes_projections_params.color, QColor) else line_attitudes_projections_params.color,
            markersize=8,  #line_attitudes_projections_params.markersize,
            alpha=line_attitudes_projections_params.alpha,
            linestyle='None',
        )

        # plot segments representing structural data

        for _, profile_attitudes in geoprofile._lines_intersections_with_attitudes.items():
            for profile_attitude in profile_attitudes:
                structural_segment_s, structural_segment_z = profile_attitude.create_segment_for_plot(
                    section_length,
                    geoprofile._topo_profile.y_linear_interpol(profile_attitude.s),
                    vertical_exaggeration,
                    segment_scale_factor=3)

                fig.gca().plot(
                    structural_segment_s,
                    structural_segment_z,
                    '-',
                    linewidth=10,
                    color=line_attitudes_projections_params.color,
                    alpha=line_attitudes_projections_params.alpha,
                )

        if line_attitudes_projections_params.label_orientations or line_attitudes_projections_params.label_ids:

            for rec_id, src_dip_dir, src_dip_ang, s, z in zip(
                    projected_ids,
                    src_dip_dirs,
                    src_dip_angs,
                    projected_s,
                    projected_z):

                if line_attitudes_projections_params.label_orientations and line_attitudes_projections_params.label_ids:
                    label = f"{rec_id}-{src_dip_dir:05.01F}/{src_dip_ang:04.01F}"
                elif line_attitudes_projections_params.label_orientations:
                    label = f"{src_dip_dir:05.01F}/{src_dip_ang:04.01F}"
                else:
                    label = f"{rec_id}"

                axes.annotate(label, (s + 15, z + 15))

    # labelling profile index in plot

    ax.text(geoprofile.s_min(), z_max - 0.075 * (z_max - z_min), f"Profile {profile_ndx+1}")

    #return fig


@profiles.register(GeoProfiles)
def _(
    geoprofiles: GeoProfiles,
    **kargs
): #-> Optional[List[Optional[Figure]]]:
    """
    Plot a set of geological profiles.

    :param geoprofiles: the geoprofiles to plot
    :return: the figures.
    """

    if not geoprofiles.have_topographies():
        print("Geoprofiles have no topographic set defined")
        return

    # keyword parameters extraction

    width = kargs.pop("width", FIG_WIDTH_INCHES_DEFAULT)
    height = kargs.pop("height", FIG_WIDTH_INCHES_DEFAULT / 4) * geoprofiles.num_profiles()

    superposed = kargs.pop("superposed", False)

    # axis parameters

    if "axis_params" in kargs:
        axis_params = kargs.pop("axis_params")
    else:
        axis_params = AxisPlotParams()
        z_range = geoprofiles.z_max() - geoprofiles.z_min()
        z_min = geoprofiles.z_min() - FIG_Z_PADDING_DEFAULT * z_range
        z_max = geoprofiles.z_max() + FIG_Z_PADDING_DEFAULT * z_range
        axis_params.z_min = z_min
        axis_params.z_max = z_max

    # others

    num_profiles = geoprofiles.num_profiles()

    if not superposed:
        fig = plt.figure(constrained_layout=True)
        spec = gridspec.GridSpec(
            ncols=1,
            nrows=num_profiles,
            figure=fig)
    else:
        fig = plt.figure()
        spec = None

    fig.set_size_inches(width, height)

    for ndx in range(geoprofiles.num_profiles()):

        geoprofile = geoprofiles[ndx]

        profiles(
            geoprofile,
            fig=fig,
            spec=spec,
            profile_ndx=ndx,
            axis_params=axis_params,
            **kargs
        )

    return fig


@profiles.register(MultiGridsProfiles)
def _(
    grid_profiles: MultiGridsProfiles,
    **kargs
): #-> Optional[List[Optional[Figure]]]:
    """
    Plot a set of geological profiles.

    :param geoprofiles: the geoprofiles to plot
    :return: the figures.
    """

    # keyword parameters extraction

    width = kargs.pop("width", FIG_WIDTH_INCHES_DEFAULT)
    height = kargs.pop("height", FIG_WIDTH_INCHES_DEFAULT / 4) * grid_profiles.num_profiles()

    superposed = kargs.pop("superposed", True)

    # axis parameters

    if "axis_params" in kargs:
        axis_params = kargs.pop("axis_params")
        aspect = axis_params.vertical_exaggeration
    else:
        axis_params = AxisPlotParams()
        z_range = grid_profiles.z_max() - grid_profiles.z_min()
        z_min = grid_profiles.z_min() - FIG_Z_PADDING_DEFAULT * z_range
        z_max = grid_profiles.z_max() + FIG_Z_PADDING_DEFAULT * z_range
        axis_params.z_min = z_min
        axis_params.z_max = z_max
        aspect = 1

    # elevation parameters

    elevation_params = kargs.pop("elevation_params", ElevationPlotParams())

    # others

    num_profiles = grid_profiles.num_profiles()

    if not superposed:
        fig = plt.figure(constrained_layout=True)
        spec = gridspec.GridSpec(
            ncols=1,
            nrows=num_profiles,
            figure=fig)
    else:
        fig = plt.figure()
        ax = fig.add_axes(
            [0.1, 0.1, 0.8, 0.8]
        )
        spec = None

    fig.set_size_inches(width, height)


    if axis_params.grid:
        ax.grid(
            True,
            color=axis_params.grid_color,
            linestyle=axis_params.grid_linestyle,
            linewidth=axis_params.grid_linewidth)

    x_arr = grid_profiles._zarray._s_array

    for profile_ndx in range(grid_profiles.num_profiles()):

        if superposed:
            linecolor = LNINT_ADDITIONAL_COLORS[profile_ndx % len(LNINT_ADDITIONAL_COLORS)]
        else:
            if elevation_params.color is None:
                linecolor = 'peru'
            elif isinstance(elevation_params.color, str):
                linecolor = elevation_params.color
            else:
                linecolor = 'peru'

        ax.plot(
            x_arr,
            grid_profiles._zarray._z_array[profile_ndx, :],
            color=linecolor,
            linestyle=elevation_params.linestyle,
            linewidth=elevation_params.width
        )

    ax.set_aspect(aspect)
    ax.set_ylim([axis_params.z_min, axis_params.z_max])

    if axis_params.breaklines:
        bottom, top = ax.get_ylim()
        ax.vlines(
            grid_profiles._zarray._s_breaks_array,
            bottom,
            top,
            color=axis_params.breaklines_color,
            linewidth=axis_params.breaklines_width,
            linestyles=axis_params.breaklines_style
        )

    #return fig


@singledispatch
def subplot(
    object: Any,
    ax: 'matplotlib.axis',
    **kargs
) -> Optional['matplotlib.axis']:
    """

    :param object: generic object to plot.
    :param ax: the matplotlib axis to plot into.
    :param kargs: the keyword arguments.
    :return: an optional axis.
    """

    aspect = kargs.pop("aspect", 1)
    ax.set_aspect(aspect)

    return ax


@subplot.register(GeoProfile)
def _(
    geoprofile: GeoProfile,
    ax: 'matplotlib.axis',
    **kargs
) -> Optional['matplotlib.axis']:
    """
    Plot a single geological profile.

    :param geoprofile: the geoprofile to plot.
    :param ax: the matplotlib axis to plot into.
    :return: the axis.
    """

    if not geoprofile.has_topography():
        print("Geoprofile has no topography defined")
        return

    z_min = kargs.pop("z_min", None)
    z_max = kargs.pop("z_max", None)
    profile_ndx = kargs.pop("profile_ndx", 0)
    aspect = kargs.pop("aspect", TOPOPROF_ASPECT_DEFAULT)
    color = kargs.pop("color", TOPOPROF_LINE_COLOR_DEFAULT)

    gridded = kargs.pop("gridded", False)
    grid_color = kargs.pop("grid_color", 'tan')
    grid_width = kargs.pop("grid_width", 0.2)

    breaklines = kargs.pop("breaklines", True)
    breaklines_color = kargs.pop("breaklines_color", 'yellow')
    breaklines_width = kargs.pop("breaklines_width", 1.5)
    breaklines_style = kargs.pop("breaklines_style", 'dotted')

    attitudes = kargs.pop("attitudes", None)
    attitudes_color = PTATT_COLOR_DEFAULT if attitudes is None else attitudes.get("color", PTATT_COLOR_DEFAULT)
    attitudes_labels_orien = PTATT_LABELS_ORIENTIONS_DEFAULT if attitudes is None else attitudes.get("label_orientations", PTATT_LABELS_ORIENTIONS_DEFAULT)
    attitudes_labels_ids = PTATT_LABELS_IDS_DEFAULT if attitudes is None else attitudes.get("label_ids", PTATT_LABELS_IDS_DEFAULT)

    line_intersections = kargs.pop("line_intersections", None)
    line_intersections_color = LNINT_COLOR_DEFAULT if line_intersections is None else line_intersections.get("color", LNINT_COLOR_DEFAULT)
    line_intersections_size = LNINT_SIZE_DEFAULT if line_intersections is None else line_intersections.get("size", LNINT_SIZE_DEFAULT)
    line_intersections_alpha = LNINT_ALPHA_DEFAULT if line_intersections is None else line_intersections.get("alpha", LNINT_ALPHA_DEFAULT)
    line_intersections_label = LNINT_LABELS_DEFAULT if line_intersections is None else line_intersections.get("linelabels", LNINT_LABELS_DEFAULT)

    polygon_intersections = kargs.pop("polygon_intersections", None)
    polygon_intersections_linewidth = PLINT_LINE_WIDTH_DEFAULT if polygon_intersections is None else polygon_intersections.get("line_width", PLINT_LINE_WIDTH_DEFAULT)
    polygon_intersections_colors = None if polygon_intersections is None else polygon_intersections.get("colors", None)
    polygon_inters_marker_label = PLINT_LABELS_DEFAULT if polygon_intersections is None else polygon_intersections.get("linelabels", PLINT_LABELS_DEFAULT)
    polygon_inters_legend_on = PLINT_LEGEND_DEFAULT if polygon_intersections is None else polygon_intersections.get("legend", PLINT_LEGEND_DEFAULT)

    points_projections = kargs.pop("points", None)
    points_projections_color = PTATT_COLOR_DEFAULT

    beachball_projections = kargs.pop("beachball_projections", None)

    # processings

    if z_min is None or z_max is None:
        z_range = geoprofile.z_max() - geoprofile.z_min()
        z_min = geoprofile.z_min() - FIG_Z_PADDING_DEFAULT * z_range
        z_max = geoprofile.z_max() + FIG_Z_PADDING_DEFAULT * z_range

    if np.isnan(z_min) or np.isnan(z_max):
        return

    ax.set_aspect(aspect)

    if z_min is not None or z_max is not None:
        ax.set_ylim([z_min, z_max])

    if geoprofile._topo_profile:

        if gridded:
            ax.grid(
                True,
                linestyle='-',
                color=grid_color,
                linewidth=grid_width)

        ax.plot(
            geoprofile._topo_profile.x_arr(),
            geoprofile._topo_profile.y_arr(),
            color=color,
            **kargs
        )

        ax.set_ylim([z_min, z_max])
        ax.set_aspect(aspect)

        if breaklines:

            bottom, top = ax.get_ylim()
            ax.vlines(
                geoprofile._topo_profile.x_breaks(),
                bottom,
                top,
                color=breaklines_color,
                linewidth=breaklines_width,
                linestyles=breaklines_style
            )

    if geoprofile._points_projections:

        section_length = geoprofile.length_2d()

        projected_ids = []
        projected_s = []
        projected_z = []
        projected_dist = []

        for rec_id, point_projection in geoprofile._points_projections.items():
            projected_ids.append(rec_id)
            projected_s.append(point_projection.s)
            projected_z.append(point_projection.z)
            projected_dist.append(point_projection.dist)

        ax.plot(
            projected_s,
            projected_z,
            'o',
            color=points_projections_color
        )

    if geoprofile._polygons_intersections:

        if not geoprofile._topo_profile:

            warn('Topographic profile is not defined, so intersections cannot be plotted')

        else:

            for ndx, polygon_intersection_element in enumerate(geoprofile._polygons_intersections):

                polygon_intersection_id = polygon_intersection_element.id
                polygon_intersection_subparts = polygon_intersection_element.arrays

                for s_range in polygon_intersection_subparts:

                    s_start = s_range[0]
                    s_end = s_range[1] if len(s_range) > 1 else None
                    s_mid = s_start if s_end is None else (s_start + s_end) / 2

                    plot_symbol = '-' if len(s_range) > 1 else 'o'

                    s_vals = geoprofile._topo_profile.x_subset(
                        s_start,
                        s_end
                    )

                    if s_vals is None:
                        continue

                    z_vals = geoprofile._topo_profile.ys_from_x_range(
                        s_start,
                        s_end
                    )

                    if z_vals is None:
                        continue

                    ax.plot(
                        s_vals,
                        z_vals,
                        plot_symbol,
                        color=polygon_intersections_colors[polygon_intersection_id],
                        linewidth=polygon_intersections_linewidth
                    )

                    if polygon_inters_marker_label:

                        ax.annotate(
                            f"{polygon_intersection_id}",
                            (s_mid, z_min + int((z_max - z_min) / 20)),
                            color=polygon_intersections_colors[polygon_intersection_id]
                        )

            if polygon_inters_legend_on:

                legend_patches = []
                for polygon_code in polygon_intersections_colors:
                    legend_patches.append(mpatches.Patch(color=polygon_intersections_colors[polygon_code], label=str(polygon_code)))

                # from: https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
                # Shrink current axis by 20%
                box = ax.get_position()
                ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

                # Put a legend to the right of the current axis
                ax.legend(
                    handles=legend_patches,
                    loc='center left',
                    bbox_to_anchor=(1, 0.5)
                )

    if geoprofile._lines_intersections:

        if not geoprofile._topo_profile:

            warn('Topographic profile is not defined, so intersections cannot be plotted')

        else:

            for ndx, line_intersection_element in enumerate(geoprofile._lines_intersections):

                line_intersection_id = line_intersection_element.id
                line_intersection_subparts = line_intersection_element.arrays

                for s_range in line_intersection_subparts:

                    s_start = s_range[0]
                    s_end = s_range[1] if len(s_range) > 1 else None
                    plot_symbol = '-o' if len(s_range) > 1 else 'o'

                    s_vals = geoprofile._topo_profile.x_subset(
                        s_start,
                        s_end
                    )

                    z_vals = geoprofile._topo_profile.ys_from_x_range(
                        s_start,
                        s_end
                    )

                    ax.plot(
                        s_vals,
                        z_vals,
                        plot_symbol,
                        color=LNINT_ADDITIONAL_COLORS[ndx] if line_intersections_color is None else line_intersections_color,
                        markersize=line_intersections_size,
                        alpha=line_intersections_alpha
                    )

                    if line_intersections_label:

                        ax.annotate(
                            f"{line_intersection_id}",
                            (s_vals[-1], z_vals[-1] + 40),
                            color=LNINT_ADDITIONAL_COLORS[ndx] if line_intersections_color is None else line_intersections_color,
                            alpha=line_intersections_alpha)

    '''20220508: temporarily deactivated
    if geoprofile.profile_attitudes:

        attitudes = geoprofile.profile_attitudes

        section_length = geoprofile.length_2d()

        projected_ids = []
        projected_s = []
        projected_z = []
        src_dip_dirs = []
        src_dip_angs = []

        for rec_id, profile_attitude in attitudes.items():
            projected_ids.append(rec_id)
            projected_s.append(profile_attitude.s)
            projected_z.append(profile_attitude.z)
            src_dip_dirs.append(profile_attitude.src_dip_dir)
            src_dip_angs.append(profile_attitude.src_dip_ang)

        vertical_exaggeration = ax.get_aspect()

        ax.plot(
            projected_s,
            projected_z,
            'o',
            color=attitudes_color
        )

        # plot segments representing structural data

        for _, structural_attitude in attitudes.items():

            structural_segment_s, structural_segment_z = structural_attitude.create_segment_for_plot(
                section_length,
                vertical_exaggeration)

            ax.plot(
                structural_segment_s,
                structural_segment_z,
                '-',
                color=attitudes_color
            )

        if attitudes_labels_orien or attitudes_labels_ids:

            for rec_id, src_dip_dir, src_dip_ang, s, z in zip(
                    projected_ids,
                    src_dip_dirs,
                    src_dip_angs,
                    projected_s,
                    projected_z):

                if attitudes_labels_orien and attitudes_labels_ids:
                    label = "%s-%03d/%02d" % (rec_id, src_dip_dir, src_dip_ang)
                elif attitudes_labels_ids:
                    label = "%s" % rec_id
                elif attitudes_labels_orien:
                    label = "%03d/%02d" % (src_dip_dir, src_dip_ang)
                else:
                    raise Exception(f"Unhandled case with {attitudes_labels_orien} and {attitudes_labels_ids}")

                ax.annotate(label, (s + 15, z + 15))
    '''

    ax.text(geoprofile.s_min(), z_max - 0.075 * (z_max - z_min), f"Profile {profile_ndx+1}")

    return ax


def map_profile(
    grid: Grid,
    geoprofile: GeoProfile,
    width: numbers.Real = 5,  # inches
    height: numbers.Real = 2.5,  # inches
    width_ratios_map: numbers.Real = 1.0,
    width_ratios_profile: numbers.Real = 5.0,
    grid_colormap="gist_earth",
    lines: List[Ln] = None,
    linecolor: str = "red",
    linestyle: str = '-',
    linewidth: numbers.Real = 1.5,
    linelabels: bool = True,
    map_zoom: numbers.Real = 1,
    plot_colorbar: bool = False,
    hillshade: bool = False,
    hs_vert_exagg: numbers.Real = 1.0,
    hs_blend_mode: str = 'hillshade',  # one of 'hillshade', 'hsv', 'overlay', 'soft'
    hs_light_source_azim: numbers.Real = 315.0,
    hs_light_source_degr: numbers.Real = 45.0,
    file_path: Optional[str] = None,
    **kargs
) -> Tuple[Union[type(None), Figure], Error]:
    """

    """

    # plot grid

    if grid.has_rotation:
        return None, Error(
            True,
            caller_name(),
            Exception(f"Grids with rotations are not supported"),
            traceback.format_exc()
        )

    if not geoprofile.has_topography():
        return None, Error(
            True,
            caller_name(),
            Exception(f"Geoprofile has no topography defined"),
            traceback.format_exc()
        )

    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        gridspec_kw={
            'width_ratios': [
                width_ratios_map,
                width_ratios_profile
            ]
        }
    )

    fig.set_size_inches(
        width,
        height
    )

    err = subplot_map(
        ax=ax1,
        grid=grid,
        lines=lines,
        grid_colormap=grid_colormap,
        linecolor=linecolor,
        linestyle=linestyle,
        linewidth=linewidth,
        linelabels=linelabels,
        map_zoom=map_zoom,
        plot_colorbar=plot_colorbar,
        hillshade=hillshade,
        hs_vert_exagg=hs_vert_exagg,
        hs_blend_mode=hs_blend_mode,
        hs_light_source_azim=hs_light_source_azim,
        hs_light_source_degr=hs_light_source_degr,
    )

    if err:
        return None, err

    subplot(
        geoprofile,
        ax2,
        **kargs
    )

    if file_path is not None:
        plt.savefig(file_path)

    return fig, Error()


@singledispatch
def animated_profiles(

):
    """
    Create an animation of profiles with their map traces.
    """


@animated_profiles.register(GeoProfiles)
def _(
    geoprofiles: GeoProfiles,
    grid: Grid,
    traces: List[Ln],
    animation_flpth: str,
    dpi_resolution: numbers.Integral = 250,
    **kargs
) -> Error:
    """
    Base commands from: https://towardsdatascience.com/basics-of-gifs-with-pythons-matplotlib-54dd544b6f30
    (cons.2021-08-01)
    """

    print("Creating geoprofiles animation")

    try:

        animation_folder_path = os.path.dirname(animation_flpth)

        z_min = kargs.pop("z_min", None)
        z_max = kargs.pop("z_max", None)

        if z_min is None or z_max is None:
            z_range = geoprofiles.z_max() - geoprofiles.z_min()
            z_min = geoprofiles.z_min() - FIG_Z_PADDING_DEFAULT * z_range
            z_max = geoprofiles.z_max() + FIG_Z_PADDING_DEFAULT * z_range

        if np.isnan(z_min) or np.isnan(z_max):
            return Error(
                True,
                caller_name(),
                Exception("z min and/or z max are Nan"),
                traceback.format_exc()
            )

        filepaths = []

        for ndx in range(geoprofiles.num_profiles()):

            print(f"Creating profile {ndx}")

            curr_trace = traces[ndx]
            geoprofile = geoprofiles[ndx]

            fig, err = map_profile(
                grid,
                geoprofile,
                lines=[curr_trace],
                z_min=z_min,
                z_max=z_max,
                profile_ndx=ndx,
                **kargs
            )

            if err:
                return err

            filepath = os.path.join(
                animation_folder_path,
                f"map_profile_{ndx:02d}.png"
            )
            filepaths.append(filepath)

            fig.savefig(filepath, dpi=dpi_resolution)

        # build gif
        with imageio.get_writer(animation_flpth, mode='I', fps=3) as writer:
            for filepath in filepaths:
                image = imageio.imread(filepath)
                writer.append_data(image)

        print(f"Geoprofiles animation saved as {animation_flpth}")

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


# bokeh profiles

default_width = 18.5
default_height = 10.5


@singledispatch
def plot(
    obj,
    **kargs
) -> Optional[figure]:
    """

    :param obj:
    :param kargs:
    :return:
    """

    fig = kargs.get("fig", None)
    aspect = kargs.get("aspect", 1)
    width = kargs.get("width", default_width)
    height = kargs.get("height", default_height)

    if fig is None:

        output_notebook()
        fig = figure()

    show(fig)

    return fig


@plot.register(ZTrace)
def _(
    xyarrays: ZTrace,
    **kargs
) -> Optional[figure]:

    fig = kargs.get("fig", None)

    if fig is None:

        output_notebook()
        fig = figure()

    fig.match_aspect = True

    fig.line(
        xyarrays.x_arr(),
        xyarrays.y_arr(),
        line_width=0.75,
    )

    show(fig)

    return fig

