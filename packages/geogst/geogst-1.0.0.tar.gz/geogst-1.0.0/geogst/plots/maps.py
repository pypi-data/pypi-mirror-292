import numbers
import traceback
from typing import Union, Dict, Optional, List

import numpy as np

from matplotlib import pyplot as plt, cm, axis
from matplotlib.colors import LightSource

from geogst.core.geometries.grids.rasters import Grid
from geogst.core.geometries.lines import Ln
from geogst.core.geometries.points import Point
from geogst.core.inspections.errors import Error
from geogst.core.inspections.functions import caller_name
from geogst.plots.parameters import MapPlotParams, FigureParams, GridPlotParams, GenericPlotParams


def maps(
    grid: Union[Grid, Dict],
    points: Union[type(None), Dict] = None,
    lines: Union[type(None), Dict] = None,
    lines_with_attitudes: Union[type(None), Dict] = None,
    map_params: Union[type(None), MapPlotParams] = None,
    fig_params: Union[type(None), FigureParams] = None,
    file_path: Optional[str] = None,
    **kargs
) -> Error:

    try:

        if isinstance(grid, Grid):
            grid_values = grid
            grid_params = GridPlotParams()
        elif isinstance(grid, Dict):
            grid_values = grid["values"]
            grid_params = grid["params"]
        else:
            return Error(
                True,
                caller_name(),
                Exception(f"Grid expected as Grid or Dict type but got {type(grid)} type"),
                traceback.format_exc())

        if map_params is None:
            map_params = MapPlotParams()

        if fig_params is None:
            fig_params = FigureParams()

        if map_params.map_zoom != 1:
            grid_values, err = grid_values.zoom_in(
                zoom_factor=map_params.map_zoom
            )
            if err:
                return err

        top_left_geogcoord, top_right_geogcoord, btm_right_geogcoord, btm_left_geogcoord = grid_values.corners_geog()

        x_extent = (btm_left_geogcoord[0], top_right_geogcoord[0])
        y_extent = (btm_left_geogcoord[1], top_right_geogcoord[1])

        geo_extent = [
            btm_left_geogcoord[0], top_right_geogcoord[0],
            btm_left_geogcoord[1], top_right_geogcoord[1]]

        # figure processings

        fig, ax = plt.subplots()
        fig.set_size_inches(fig_params.width, fig_params.height)

        # grid processings

        if grid_params.hillshade:

            dx, dy = grid_values.cellsize_x, grid_values.cellsize_y

            ls = LightSource(
                azdeg=grid_params.hs_light_source_azim,
                altdeg=grid_params.hs_light_source_degr)

            plot = ax.imshow(
                ls.hillshade(
                    grid_values.array,
                    vert_exag=grid_params.hs_vert_exagg,
                    dx=dx,
                    dy=dy),
                extent=geo_extent,
                cmap=grid_params.grid_colormap,
                vmin=np.nanmin(grid_values.array),
                vmax=np.nanmax(grid_values.array)
            )

            if grid_params.hs_blend_mode in ('hsv', 'overlay', 'soft'):
                rgb = ls.shade(
                    grid_values.array,
                    cmap=cm.get_cmap(grid_params.grid_colormap),
                    blend_mode=grid_params.hs_blend_mode,
                    vert_exag=grid_params.hs_vert_exagg,
                    dx=dx,
                    dy=dy
                )
                ax.imshow(
                    rgb,
                    extent=geo_extent)

        else:

            plot = ax.imshow(
                grid_values.array,
                extent=geo_extent,
                cmap=grid_params.grid_colormap)

        if grid_params.plot_colorbar:
            fig.colorbar(plot)

        # lines processings

        if lines:

            for key_value, ln_dataset in lines.items():

                line_geoms = ln_dataset["data"]
                line_params = ln_dataset.get("params", GenericPlotParams())

                if isinstance(line_geoms, list):

                    if not isinstance(line_params, GenericPlotParams):
                        line_params = GenericPlotParams()

                    for ndx, line in enumerate(line_geoms):

                        ax.plot(
                            line.x_list(),
                            line.y_list(),
                            color=line_params.color,
                            linestyle=line_params.linestyle,
                            linewidth=line_params.width,
                            alpha=line_params.alpha,
                            **kargs)

                        if line_params.labels:
                            end_point = line[-1].end_pt
                            if len(line_geoms) == 1:
                                label = f"{key_value}"
                            else:
                                label = f'{ndx}'

                            ax.text(
                                end_point.x,
                                end_point.y,
                                label,
                                color=line_params.color,
                                weight='bold',
                            )

                elif isinstance(line_geoms, Dict):

                    for subcat_key, subcat_lines in line_geoms.items():

                        if isinstance(line_params, Dict):

                            line_color = line_params[subcat_key].color
                            line_style = line_params[subcat_key].linestyle
                            line_width = line_params[subcat_key].width
                            line_alpha = line_params[subcat_key].alpha
                            linelabels = line_params[subcat_key].labels

                        else:

                            line_color = line_params.color
                            line_style = line_params.linestyle
                            line_width = line_params.width
                            line_alpha = line_params.alpha
                            linelabels = line_params.labels

                        for ndx, line in enumerate(subcat_lines):

                            ax.plot(
                                line.x_list(),
                                line.y_list(),
                                color=line_color,
                                linestyle=line_style,
                                linewidth=line_width,
                                alpha=line_alpha,
                                **kargs)

                            if linelabels:
                                end_point = line[-1].end_pt
                                label = f'{key_value}'

                                ax.text(end_point.x, end_point.y, label)

                else:

                    return Error(
                        True,
                        caller_name(),
                        Exception(f"Unexpected types for 'line_geoms' (found {type(line_geoms)}) and 'line_params' (found {type(line_params)})"),
                        traceback.format_exc()
                    )

            plt.xlim(x_extent)
            plt.ylim(y_extent)

        # lines with attitudes processings

        if lines_with_attitudes:

            for key_value, ln_dataset in lines_with_attitudes.items():

                line_geoms = ln_dataset["data"]
                line_params = ln_dataset.get("params", GenericPlotParams())

                if isinstance(line_geoms, list):

                    if not isinstance(line_params, GenericPlotParams):
                        line_params = GenericPlotParams()

                    for ndx, (attitude, lines) in enumerate(line_geoms):

                        for line in lines:

                            ax.plot(
                                line.x_list(),
                                line.y_list(),
                                color=line_params.color,
                                linestyle=line_params.linestyle,
                                linewidth=line_params.width,
                                alpha=line_params.alpha,
                                **kargs)

                            if line_params.labels:
                                end_point = line[-1].end_pt
                                label = f'{key_value}'

                                ax.text(end_point.x, end_point.y, label)

                elif isinstance(line_geoms, Dict):

                    for subcat_key, subcat_lines in line_geoms.items():

                        if isinstance(line_params, Dict):

                            line_color = line_params[subcat_key].color
                            line_style = line_params[subcat_key].linestyle
                            line_width = line_params[subcat_key].width
                            line_alpha = line_params[subcat_key].alpha
                            linelabels = line_params[subcat_key].labels

                        else:

                            line_color = line_params.color
                            line_style = line_params.linestyle
                            line_width = line_params.width
                            line_alpha = line_params.alpha
                            linelabels = line_params.labels

                        if isinstance(subcat_lines, List):

                            for attitude, lines in subcat_lines:

                                for line in lines:

                                    ax.plot(
                                        line.x_list(),
                                        line.y_list(),
                                        color=line_color,
                                        linestyle=line_style,
                                        linewidth=line_width,
                                        alpha=line_alpha,
                                        **kargs)

                                    if linelabels:
                                        end_point = line[-1].end_pt
                                        label = f'{key_value}'

                                        ax.text(end_point.x, end_point.y, label)

                        else:

                            attitude, lines = subcat_lines

                            for line in lines:

                                ax.plot(
                                    line.x_list(),
                                    line.y_list(),
                                    color=line_color,
                                    linestyle=line_style,
                                    linewidth=line_width,
                                    alpha=line_alpha,
                                    **kargs)

                                if linelabels:
                                    end_point = line[-1].end_pt
                                    label = f'{key_value}'

                                    ax.text(end_point.x, end_point.y, label)

                else:

                    return Error(
                        True,
                        caller_name(),
                        Exception(f"Unexpected types for 'line_geoms' (found {type(line_geoms)}) and 'line_params' (found {type(line_params)})"),
                        traceback.format_exc()
                    )

            plt.xlim(x_extent)
            plt.ylim(y_extent)

        # points processings

        if points:

            #print(f"currently with points")

            for pts_cat in points.keys():

                #print(f"\tCategory: {pts_cat}")

                pts_dataset = points[pts_cat]

                if isinstance(pts_dataset, List):

                    #print("Points are in List")

                    points_params = GenericPlotParams()

                    point_marker = points_params.marker
                    point_markersize = points_params.markersize
                    point_color = points_params.color
                    point_alpha = points_params.alpha
                    point_label = points_params.labels

                    for ndx, point_dataset in enumerate(pts_dataset):

                        #print(f"ndx {ndx} point_dataset {point_dataset}")
                        if isinstance(point_dataset, Point):
                            point = point_dataset
                        elif isinstance(point_dataset[1], Point):
                            point = point_dataset[1]
                        else:
                            print(f"Point instance not found in 'point_dataset' variable")
                            continue

                        ax.plot(
                            point.x,
                            point.y,
                            marker=point_marker,
                            markersize=point_markersize,
                            color=point_color,
                            alpha=point_alpha,
                            **kargs)

                        if point_label:
                            label = f'{key_value}'

                            ax.text(point.x, point.y, label)

                elif isinstance(pts_dataset, Dict):

                    #print("Points are in Dict")

                    points_type = pts_dataset.get("type", "points")  # one of "points", "attitudes", "beachballs"
                    points_data = pts_dataset["data"]
                    points_params = pts_dataset.get("params", GenericPlotParams())

                    point_marker = points_params.marker
                    point_markersize = points_params.markersize
                    point_color = points_params.color
                    point_alpha = points_params.alpha
                    point_label = points_params.labels

                    if points_type in ("points", "attitudes"):  # currently 'attitudes' just plot a point marker, could plot an azimuth

                        for ndx, point_dataset in enumerate(points_data):

                            #print(f"ndx {ndx} point_dataset {point_dataset}")
                            if isinstance(point_dataset, Point):
                                point = point_dataset
                            elif isinstance(point_dataset[1], Point):
                                point = point_dataset[1]
                            else:
                                print(f"Point instance not found in 'point_dataset' variable")
                                continue

                            ax.plot(
                                point.x,
                                point.y,
                                marker=point_marker,
                                markersize=point_markersize,
                                color=point_color,
                                alpha=point_alpha,
                                **kargs)

                            if point_label:
                                label = f'{pts_cat}'

                                ax.text(point.x, point.y, label)

                    elif points_type == "beachballs":  # possibly to implement without major difficulties

                        return Error(
                            True,
                            caller_name(),
                            NotImplementedError,
                            traceback.format_exc()
                        )

                    else:

                        return Error(
                            True,
                            caller_name(),
                            Exception(f"Unexpected types for points type"),
                            traceback.format_exc()
                        )

                else:

                    return Error(
                        True,
                        caller_name(),
                        Exception(f"Unexpected types for points input"),
                        traceback.format_exc()
                    )

        plt.xlim(x_extent)
        plt.ylim(y_extent)

        if file_path is not None:
            plt.savefig(file_path)
            print(f"Figure saved as {file_path}")

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def subplot_map(
    ax: axis,
    grid: Grid,
    lines: List[Ln] = None,
    grid_colormap="gist_earth",
    linecolor: str = "blue",
    linestyle: str = '-',
    linewidth: numbers.Real = 0.5,
    linelabels: bool = True,
    map_zoom: numbers.Real = 1,
    plot_colorbar: bool = False,
    hillshade: bool = False,
    hs_vert_exagg: numbers.Real = 1.0,
    hs_blend_mode: str = 'hillshade', # one of 'hillshade', 'hsv', 'overlay', 'soft'
    hs_light_source_azim: numbers.Real = 315.0,
    hs_light_source_degr: numbers.Real = 45.0,
) -> Error:
    """
    Plot a grid with geographic coordinates.

    :param ax: the figure axis.
    :param grid: the input Grid instance.
    :param lines: optional input lines to plot.
    :param grid_colormap: the colormap to apply to the visualized grid.
    :param linecolor: the color to apply to the lines.
    :param linestyle: the style for the lines.
    :param linewidth: the line width.
    :param linelabels: whether to plot also line labels.
    :param map_zoom: the grid-centered zoom to apply to the figure.
    :param plot_colorbar: whether to plot the grid colobar.
    :param hillshade: whether to create a hillshaded map.
    :param hs_vert_exagg: the vertical exaggeration for the hillshading.
    :param hs_blend_mode: the blend mode for the hillshading.
    :param hs_light_source_azim: the light source azimuth for the hillshading.
    :param hs_light_source_degr: the light source inclination for the hillshading.
    :return: the eventual error_qt.
    """

    # if there is a zoom factor, creates a new, zoomed grid and set the grid level to zero
    if map_zoom != 1:
        grid, err = grid.zoom_in(
            zoom_factor=map_zoom
        )
        if err:
            return err

    top_left_coord, top_right_coord, btm_right_coord, btm_left_coord = grid.corners_geog()

    geo_extent = [
        btm_left_coord[0], top_right_coord[0],
        btm_left_coord[1], top_right_coord[1]]

    grid_values = grid.array

    if hillshade:

        dx, dy = grid.cellsize_x, grid.cellsize_y

        ls = LightSource(
            azdeg=hs_light_source_azim,
            altdeg=hs_light_source_degr)

        plot = ax.imshow(
            ls.hillshade(
                grid_values,
                vert_exag=hs_vert_exagg,
                dx=dx,
                dy=dy),
            extent=geo_extent,
            cmap='gray'
        )

        if hs_blend_mode in ('hsv', 'overlay', 'soft'):
            rgb = ls.shade(
                grid_values,
                cmap=cm.get_cmap(grid_colormap), # plt.cm.gist_earth ,
                blend_mode=hs_blend_mode,
                vert_exag=hs_vert_exagg,
                dx=dx,
                dy=dy
            )
            ax.imshow(
                rgb,
                extent=geo_extent)

    else:

        plot = ax.imshow(
            grid_values,
            extent=geo_extent,
            cmap=grid_colormap)

    if plot_colorbar:
        plt.colorbar(plot)
        #ax.colorbar(plot)

    # plot lines

    for ndx, line in enumerate(lines):

        if linelabels and (ndx + 1) % 5 == 0:
           line_color = 'red'
           line_width = linewidth * 2
        else:
            line_color = linecolor
            line_width = linewidth

        ax.plot(
            line.x_list(),
            line.y_list(),
            color=line_color,
            linestyle=linestyle,
            linewidth=line_width)

        if linelabels and (ndx + 1) % 5 == 0:
            end_point = line[-1].end_pt
            ax.text(end_point.x, end_point.y, f'{ndx+1}')
