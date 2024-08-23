
from typing import Dict
import os
import json

import numpy as np

from geogst.core.mathematics.utils import *



def save_surface_as_vtk(
    output_filepath,
    geodata
):

    try:

        geosurface, grid_dims = geodata
        X, Y, Z = geosurface

        X_arr = np.array(X, dtype=float)
        Y_arr = np.array(Y, dtype=float)
        Z_arr = np.array(Z, dtype=float)

        n_points = np.size(X_arr)

        n_rows, n_cols = grid_dims

        with open(output_filepath, 'w') as outfile:

            outfile.write('# vtk DataFile Version 2.0\n')
            outfile.write('Geosurface - qgSurf vers. 0.3.0\n')
            outfile.write('ASCII\n')
            outfile.write('\nDATASET POLYDATA\n')

            outfile.write('POINTS %d float\n' % n_points)
            for n in range(n_points):
                outfile.write('%.4f %.4f %.4f\n' % (X_arr[n], Y_arr[n], Z_arr[n]))

            outfile.write('\n')

            outfile.write('TRIANGLE_STRIPS %d %d\n' % (n_cols-1, (n_cols-1)*(1+n_rows*2)))

            num_points_strip = n_rows * 2
            for l in range(n_cols - 1):
                triangle_strip_string = "%d " % num_points_strip
                for p in range(n_rows):
                    triangle_strip_string += "%d %d " % ((l+1)*n_rows+p, l*n_rows+p)
                triangle_strip_string += "\n"
                outfile.write(triangle_strip_string)

            return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )
            
def save_surface_as_grass(
    output_filepath,
    geodata
) -> Error:

    try:

        # Save in Grass format

        geosurface, grid_dims = geodata
        X, Y, Z = geosurface

        X_arr = np.array(X, dtype=float)
        Y_arr = np.array(Y, dtype=float)
        Z_arr = np.array(Z, dtype=float)

        n_rows, n_cols = grid_dims

        with open(output_filepath, 'w') as outfile:
            outfile.write('VERTI:\n')
            for l in range(n_cols - 1):
                for p in range(n_rows - 1):
                    start_point_ndx = l*n_rows + p
                    forward_line_point_ndx = start_point_ndx + n_rows
                    outfile.write('F 4\n')
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[start_point_ndx], Y_arr[start_point_ndx], Z_arr[start_point_ndx]))
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[start_point_ndx+1], Y_arr[start_point_ndx+1], Z_arr[start_point_ndx+1]))
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[forward_line_point_ndx], Y_arr[forward_line_point_ndx], Z_arr[forward_line_point_ndx]))
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[start_point_ndx], Y_arr[start_point_ndx], Z_arr[start_point_ndx]))
                    outfile.write('F 4\n')
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[forward_line_point_ndx], Y_arr[forward_line_point_ndx], Z_arr[forward_line_point_ndx]))
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[start_point_ndx+1], Y_arr[start_point_ndx+1], Z_arr[start_point_ndx+1]))
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[forward_line_point_ndx+1], Y_arr[forward_line_point_ndx+1], Z_arr[forward_line_point_ndx+1]))
                    outfile.write(' %.4f %.4f %.4f\n' % (X_arr[forward_line_point_ndx], Y_arr[forward_line_point_ndx], Z_arr[forward_line_point_ndx]))

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )

def save_surface_as_gas(
    output_filepath,
    geodata,
) -> Error:

    try:

        with open(output_filepath, 'w') as outfile:
            json.dump(geodata, outfile)

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def save_surface_as_ascii_grid(
    output_filepath: str,
    geodata: Dict,
    esri_nullvalue: numbers.Real = -99999.9
) -> Error:

    try:

        geographical_params = geodata['geographical params']

        if geographical_params['grid rot angle degr'] != 0:
            return Error(
                True,
                caller_name(),
                Exception("Ascii grid do not handle non-zero rotations")
            )

        nrows, ncols = geodata['grid dims']
        _, _, Z = geodata['geosurface']

        z_array = np.empty([nrows, ncols])
        for j in range(ncols):
            for i in range(nrows):
                z_array[i, j] = Z[i + nrows*j]

        x_min = geographical_params['geog x min']
        y_min = geographical_params['geog y min']
        width = geographical_params['grid width x']
        height = geographical_params['grid height y']

        if are_close(width/ncols, height/nrows):
            cell_size = 0.5*(width/ncols + height/nrows)
        else:
            return Error(
                True,
                caller_name(),
                Exception(f"To save an ESRI ascii grid cell sizes must be equal in x- and y-directions.\nFound {width/ncols} for x and {height/nrows} for y")
            )

        # checking existence of output slope grid

        if os.path.exists(output_filepath):
            return Error(
                True,
                caller_name(),
                Exception(f"Output grid '{output_filepath}' already exists")
            )

        outputgrid = open(output_filepath, 'w')  # create the output ascii file

        # writes header of grid ascii file

        outputgrid.write("NCOLS %d\n" % ncols)
        outputgrid.write("NROWS %d\n" % nrows)
        outputgrid.write("XLLCORNER %.8f\n" % x_min)
        outputgrid.write("YLLCORNER %.8f\n" % y_min)
        outputgrid.write("CELLSIZE %.8f\n" % cell_size)
        outputgrid.write("NODATA_VALUE %f\n" % esri_nullvalue)

        esrigrid_outvalues = np.where(np.isnan(z_array), esri_nullvalue, z_array)

        # output of results

        for i in range(0, nrows):
            for j in range(0, ncols):
                outputgrid.write("%.8f " % (esrigrid_outvalues[i, j]))
            outputgrid.write("\n")

        outputgrid.close()

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )

            
