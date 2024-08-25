
from collections import defaultdict

#import numpy as np

from geogst.core.geometries.polygons import *
from geogst.core.profiles.methods import *
from geogst.core.profiles.profiletraces import *
from geogst.core.utils.arrays import *


class SegmentProfiler:
    """
    Class storing a linear (straight) profile.
    It intends to represent a segmented vertical profile.
    In a possible future implementations, it would be superseded by a
    plane profilers, not necessarily vertical.
    """

    def __init__(self,
                 segment: Segment):
        """
        Instantiates a 2D segment profile object.

        :param segment: the profile segment.
        """

        self._segment = Segment(
            start_pt=segment.start_pt.as_point2d(),
            end_pt=segment.end_pt.as_point2d()
        )

    @classmethod
    def from_points(cls,
        start_pt: Point,
        end_pt: Point,
    ):
        """
        Instantiates a 2D segment profile object.
        It is represented by two points and an EPSG code.

        :param start_pt: the profile start point.
        :param end_pt: the profile end point.
        """

        _start_pt = Point(
            start_pt.x,
            start_pt.y
        )

        _end_pt = Point(
            end_pt.x,
            end_pt.y
        )

        return cls(
            Segment(_start_pt, _end_pt),
        )

    def segment(self) -> Segment:
        """
        Returns the horizontal segment representing the profile.

        :return: segment representing the profile.
        """

        return self._segment.clone()

    def start_pt(self) -> Point:
        """
        Returns a copy of the segment start point.

        :return: segment start point copy.
        """

        return Point(
            self.segment().start_pt.x,
            self.segment().start_pt.y
        )

    def end_pt(self) -> Point:
        """
        Returns a copy of the segment end point.

        :return: segment end point copy.
        """

        return Point(
            self.segment().end_pt.x,
            self.segment().end_pt.y
        )

    def to_line(self) -> Ln:
        """
        Convert to a line.

        """

        return Ln.from_points(
                self.start_pt(),
                self.end_pt()
        )

    def __repr__(self):
        """
        Representation of a profile instance.

        :return: the textual representation of the instance.
        """

        return f"SegmentProfiler(\n\tstart_pt = {self.start_pt()},\n\tend_pt = {self.end_pt()})"

    def clone(self) -> 'SegmentProfiler':
        """
        Returns a deep copy of the current profilers.

        :return: a deep copy of the current profilers.
        """

        return SegmentProfiler(
            segment=self.segment())

    def length(self) -> numbers.Real:
        """
        Returns the length of the profilers section.

        :return: length of the profilers section.
        """

        return self.segment().length

    def vector(self) -> Vect3D:
        """
        Returns the horizontal 3D vector representing the profile.

        :return: vector representing the profile.
        """

        return Vect3D(
            x=self.segment().delta_x(),
            y=self.segment().delta_y(),
            z=0.0
        )

    def versor(self) -> Vect3D:
        """
        Returns the horizontal 3D versor (unit vector) representing the profile.

        :return: versor representing the profile.
        """

        return self.vector().versor()

    def densify_as_steps_array(self,
                               sampling_distance: numbers.Real
                               ) -> Tuple[bool, Union[str, array]]:
        """
        Returns an array made up by the incremental steps (2D distances) along the profile.

        :param sampling_distance: the segment profilers sampling distance
        :return: optional array storing the incremental steps, with the last step being equal to the segment length.
        """

        return densify_as_array1d_(
            segment_length=self.segment().length_2d(),
            densify_distance=sampling_distance
        )

    def densify_as_2D_points(self,
                             densify_distance: numbers.Real
                             ) -> Tuple[Union[type(None), List[Point]], Error]:
        """
        Returns a list of densified points.

        :param densify_distance: the profilers densify distance.
        :return: optional list of densified points and error status.
        """

        return self.segment().densify_as_pts2d(
            densify_distance=densify_distance
        )

    def vertical_plane(self) -> Optional[CPlane3D]:
        """
        Returns the vertical plane of the segment, as a Cartesian plane.

        :return: the vertical plane of the segment, as a Cartesian plane.
        """

        return vertical_plane_from_segment(
            segment=self.segment()
        )

    def normal_versor(self) -> Tuple[Union[type(None), Vect3D], Error]:
        """
        Returns the perpendicular (horizontal) versor to the profile (vertical) plane.

        :return: the perpendicular (horizontal) versor to the profile (vertical) plane.
        """

        vert_plane = self.vertical_plane()
        if vert_plane is None:
            return None, Error(
                True,
                caller_name(),
                Exception("Vertical plane is None"),
                traceback.format_exc())

        return vert_plane.normal_versor()

    def left_norm_vers(self) -> Vect2D:
        """
        Returns the left horizontal normal versor.

        :return: the left horizontal normal versor.
        """

        return Vect2D(
            x=-self.versor().y,
            y=self.versor().x
        )

    def right_norm_vers(self) -> Vect2D:
        """
        Returns the right horizontal normal versor.

        :return: the right horizontal normal versor.
        """

        return Vect2D(
            x=self.versor().y,
            y=-self.versor().x
        )

    def shift(self,
              dx: numbers.Real,
              dy: numbers.Real
    ) -> 'SegmentProfiler':
        """
        Returns a new LinearProfiler instance, horizontally offset by the
        provided horizontal components.
        """

        return SegmentProfiler(
            segment=self.segment().shift(dx, dy))

    def vector_offset(self,
                      vect: Vect2D
                      ) -> 'SegmentProfiler':
        """
        Returns a new SegmentProfiler instance, horizontally offset by the
        provided vector horizontal components.
        """

        return SegmentProfiler(
            segment=self.segment().shift(vect.x, vect.y))

    def right_parallel_offset(self,
                              offset: numbers.Real
                              ) -> 'SegmentProfiler':
        """
        Returns a copy of the current profilers, offset to the right by the provided offset distance.

        :param offset: the lateral offset to apply to create the new profilers.
        :return: the offset profilers.
        """

        return self.vector_offset(vect=self.right_norm_vers().scale(offset))

    def left_parallel_offset(self,
                             offset: numbers.Real
                             ) -> 'SegmentProfiler':
        """
        Returns a copy of the current profilers, offset to the left by the provided offset distance.

        :param offset: the lateral offset to apply to create the new profilers.
        :return: the offset profilers.
        """

        return self.vector_offset(vect=self.left_norm_vers().scale(offset))

    def point_in_vertical_profile(self,
                                  pt: Point
                                  ) -> bool:
        """
        Checks whether a point lies in the profilers plane.

        :param pt: the point to check.
        :return: whether the point lies in the profilers plane.
        :raise: Exception.
        """

        pt_use = Point(
                pt.x,
                pt.y,
                0.0
            )

        return self.vertical_plane().contains_point(pt_use)

    def point_horizontal_distance(self,
                                  pt: Point
                                  ) -> numbers.Real:
        """
        Calculates the point distance from the profilers plane.

        :param pt: the point to check.
        :return: the point distance from the profilers plane.
        :raise: Exception.
        """

        pt_use = Point(
                pt.x,
                pt.y,
                0.0
            )

        return self.vertical_plane().absolute_distance_to_point(pt_use)

    def sample_grid_with_step(
            self,
            grid: Grid,
            sampling_distance: numbers.Real
    ) -> Tuple[Union[type(None), array], Error]:
        """
        Sample grid values along the profilers points.

        :param sampling_distance: the grid sampling distance along the trace.
        :param grid: the input grid.
        :return: array storing the z values sampled from the grid and an error status.
        """

        try:

            result, error = self.densify_as_2D_points(sampling_distance)

            if error:
                return None, error

            pts_2d = result

            values_arr = array('d', [grid.interpolate_bilinear(pt_2d.x, pt_2d.y) for pt_2d in pts_2d])

            return values_arr, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def profile_grid_as_ztrace(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None
    ) -> Tuple[Union[type(None), ZTrace], Error]:
        """
        Create profile from one grid.

        :param grid: the source grid.
        :param sampling_distance: the distance along to which to sample the grid.
        :return: the potential profile of the scalar variable stored in the grid and an error status.
        """

        try:

            if sampling_distance is None:
                sampling_distance = grid.cellsize_mean

            success, result = self.densify_as_steps_array(sampling_distance)

            if not success:
                msg = result
                return None, Error(
                    True,
                    caller_name(),
                    Exception(msg),
                    traceback.format_exc())

            x_arr = result

            y_arr, err = self.sample_grid_with_step(
                grid,
                sampling_distance)

            if err:
                return None, err

            return ZTrace(x_array=x_arr, y_array=y_arr), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def profile_grid_as_pts3d(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None
    ) -> Tuple[Union[type(None), List[Point]], Error]:
        """
        Create a point-based profile from one grid.

        :param grid: the source grid.
        :param sampling_distance: the distance along to which to sample the grid.
        :return: the optional point-like profile along the grid and an error status.
        """

        try:

            if sampling_distance is None:
                sampling_distance = grid.cellsize_mean

            result, error = self.densify_as_2D_points(sampling_distance)

            if error:
                return None, error

            pts_2d = result

            pts_3d = map(lambda pt2d: grid.interpolate_bilinear_point(pt2d), pts_2d)
            pts_3d = filter(lambda pt3d: pts_3d is not None, pts_3d)

            return list(pts_3d), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def profile_grid_as_pts3d_with_nans(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None
    ) -> Tuple[Union[type(None), List[Point]], Error]:
        """
        Create a point-based profile from one grid.

        :param grid: the source grid.
        :param sampling_distance: the distance along to which to sample the grid.
        :return: the optional point-like profile along the grid and an error status.
        """

        try:

            if sampling_distance is None:
                sampling_distance = grid.cellsize_mean

            result, error = self.densify_as_2D_points(sampling_distance)

            if error:
                return None, error

            pts_2d = result

            pts_3d = map(lambda pt2d: grid.interpolate_bilinear_point_with_nan(pt2d), pts_2d)
            pts_3d = filter(lambda pt3d: pts_3d is not None, pts_3d)

            return list(pts_3d), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def intersect_mline(self,
                        mline: MLine,
                        ) -> List[UnionPtSegment2D]:
        """
        Calculates the intersection with a line/multiline.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param mline: the line/multiline to intersect profile with
        :return: the possible intersections
        """

        if isinstance(mline, (Ln, MultiLine)):
            mline = mline.as_2d()

        return intersect(self.segment(), mline)

    def intersect_line(self,
        line: Ln
    ) -> List[UnionPtSegment2D]:
        """
        Calculates the intersection with a line.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param line: the line to intersect profile with
        :return: the possible intersections
        """

        line = line.as_2d()

        return intersect(self.segment(), line)

    def intersect_lines(self,
                        lines: List[Ln],
                        ) -> List[UnionPtSegment2D]:
        """
        Calculates the intersection with a set of lines.
        Note: the intersections are calculated in a 2D plane (not 3D).

        :param lines: an iterable of georeferenced Lines or MultiLines to intersect profile with
        :return: the optional line-identified intersections
        :raise: Exception
        """

        intersections = []
        for line in lines:
            intersections.extend(self.intersect_line(line))
        return intersections

    def intersect_line_with_attitude(self,
        line: Ln,
        attitude: Plane,
    ) -> Tuple[Union[type(None), List[Tuple[Vect3D, Point]]], Error]:
        """
        Calculates the intersection with a line with a geological attitude.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param line: the line to intersect profile with
        :param attitude: the surface attitude, property of the line to intersect.
        :return: the possible intersections
        """

        try:

            line = line.as_2d()

            intersection_geometries = intersect(self.segment(), line)  # List[Union[type(None), Point, 'Segment']]

            if intersection_geometries is None:
                print(f"Warning: intersecting geometries are None")
                return None, Error()

            # get vertical section plane

            section_plane = self.vertical_plane()
            if section_plane is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("Returned vertical plane from segment profile is None"),
                    traceback.format_exc())

            intersection_results = []

            for ndx, intersection_geometry in enumerate(intersection_geometries):

                if intersection_geometry is None:
                    print(f"Warning: intersecting geometry {ndx} is None")
                    continue

                if isinstance(intersection_geometry, Point):

                    # calculate intersection geometry between attitude and plane
                    # note that intersection point must be transformed
                    # to a 3D point.

                    # Tuple[Union[type(None), Vect3D, CPlane3D], Error]
                    intersection_attitude, err = versor_from_plane_attitude_inters(
                        cartes_plane=section_plane,
                        attitude=attitude,
                        point=intersection_geometry
                    )

                    if err:
                        print(f"Error with intersection geometry {intersection_geometry}: {err!r} ")
                        continue

                    if isinstance(intersection_attitude, CPlane3D):
                        print(f"Warning: intersected geometry is a CPlane3D, that it should mean that it it parallel to the section plane")
                        continue
                    elif isinstance(intersection_attitude, Vect3D):
                        intersection_results.append((intersection_attitude, intersection_geometry))
                    else:
                        print(f"Warning: intersection geometry is a {type(intersection_attitude)}, not a Vect3D")
                        continue

                else:

                    print(f"Warning: intersection geometry is a {type(intersection_geometry)}, not a Point")
                    continue

            return intersection_results, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )

    def intersect_lines_with_attitude(self,
        lines: List[Ln],
        attitude: Plane
    ) -> Tuple[Union[type(None), List[Tuple[Vect3D, Point]]], Error]:
        """
        Calculates the intersection with a set of lines.
        Note: the intersections are calculated in a 2D plane (not 3D).

        :param lines: an iterable of georeferenced Lines or MultiLines to intersect profile with
        :param attitude: the plane expressing the local orientation of the surface traces.
        :return: the optional line-identified intersections
        :raise: Exception
        """

        try:

            point_traces = []

            for line in lines:

                result, err = self.intersect_line_with_attitude(
                    line,
                    attitude)

                if err:
                    print(f"Error: {err!r} ")
                    continue

                if result is None:
                    print(f"Warning: segment intersection with line/attitude is None")
                    continue

                point_traces.extend(result)

            return point_traces, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )

    def intersect_polygon(self,
                          polygon: Polygon) -> List[Segment]:
        """
        Calculates the intersection with a polygon.

        """

        outer_inters, inner_inters = polygon.intersect_segment_base(self._segment)

        full_intersections = []
        full_intersections.extend([outer_inters[key] for key in outer_inters])
        full_intersections.extend([inner_inters[key] for key in inner_inters])

        full_sorted_pts = self.sort_raw_intersections(full_intersections)

        segments = Ln.from_points(self._segment.start_pt, *full_sorted_pts, self._segment.end_pt).remove_coincident_points().segments()

        intersecting_segments = []

        for segment in segments:

            if polygon.point_in_polygon(segment.midpoint()):
                intersecting_segments.append(segment)

        return intersecting_segments

    def sort_raw_intersections(self,
        intersections: List[Union[type(None), Point, Segment]]
    ) -> List[Point]:
        """
        Sort the intersections based on the distance from the profile start.
        """

        inters_points = list(filter(lambda el: isinstance(el, Point), intersections))
        inters_segments = list(filter(lambda el: isinstance(el, Segment), intersections))

        inters_segments_points = []
        for segm in inters_segments:
            inters_segments_points.extend([segm.start_pt, segm.end_pt])

        total_points = inters_points + inters_segments_points
        total_points.sort(key=self._segment.point_distance_from_start)

        return total_points

    def point_along_profile_signed_s(
            self,
            pt: Point,
            offset: numbers.Real = 0.0
    ) -> Union[type(None), numbers.Real]:
        """
        Calculates the point along-profile signed distance (positive in the segment direction, negative otherwise)
        from the profile start.
        The projected point must already lay in the profile vertical plane, otherwise an exception is raised.

        The implementation assumes (and also verifies) that the point lies in the profile vertical plane.
        Given that case, it calculates the signed distance from the section start point,
        by using the triangle law of sines.

        :param pt: the point on the section.
        :param offset: the offset to apply to the distance from segment start (to comply with line profiles).
        :return: the signed distance along the profile or None if outside the segment.
        """

        if pt.is_2d():
            use_pt = Point(
                pt.x,
                pt.y,
                0.0
            )
        else:
            use_pt = pt.clone()

        if not self.point_in_vertical_profile(use_pt):
            raise Exception(f"Projected point should lie in the profile plane but there is a distance of {self.point_horizontal_distance(use_pt)} units")

        if use_pt.as_point2d().is_coincident(self.start_pt()):
            return 0.0 + offset

        # the vector starting at the profile start and ending at the given point

        projected_vector = Segment(
            Point(
                self.start_pt().x,
                self.start_pt().y,
                0.0),
            use_pt
        ).as_vector3d()

        # the rot_angle between the profile vector and the previous vector
        cos_alpha = self.vector().cosine_of_angle(projected_vector)
        if cos_alpha is None:
            return None

        signed_distance = projected_vector.length * cos_alpha

        return signed_distance + offset

    def segment_along_profile(self,
                              segment: Segment,
                              offset: numbers.Real = 0.0
                              ) -> Tuple[Optional[numbers.Real], Optional[numbers.Real]]:
        """
        Calculates the segment distances from the profiles start.
        The segment must already lay in the profile vertical plane, otherwise None is returned.

        :param segment: the analysed segment.
        :param offset: the offset to apply to the distance from segment start (to comply with line profiles).
        :return: the segment vertices distances from the profile start.
        """

        segment_start_distance = self.point_along_profile_signed_s(segment.start_pt, offset)
        segment_end_distance = self.point_along_profile_signed_s(segment.end_pt, offset)

        return segment_start_distance, segment_end_distance

    def pt_segm_along_profile_signed_s(self,
                                       ptsegm2d: UnionPtSegment2D,
                                       offset: numbers.Real = 0.0
                                       ) -> array:
        """
        Calculates the point or segment signed distances from the segment start.

        :param ptsegm2d: point or segment.
        :param offset: the offset to apply to the distance from segment start (to comply with line profiles).
        :return: the distance(s) from the segment start.
        """

        if isinstance(ptsegm2d, Point):
            return array('d', [self.point_along_profile_signed_s(ptsegm2d, offset)])
        elif isinstance(ptsegm2d, Segment):
            return array('d', [*self.segment_along_profile(ptsegm2d, offset)])
        else:
            return NotImplemented

    def get_intersection_slope(self,
        intersection_vector: Vect3D
    ) -> Tuple[Union[Tuple[numbers.Real, str], type(None)], Error]:
        """
        Calculates the slope (in radians) and the downward sense ('left', 'right' or 'vertical')
        for a profile-laying vector.

        :param intersection_vector: the profile-plane lying vector.
        :return: the slope (in radians) and the downward sense.
        """

        try:

            norm_versor, error = self.normal_versor()
            if error:
                return None, error

            angle = degrees(acos(norm_versor.cosine_of_angle(intersection_vector)))
            if abs(90.0 - angle) > 1.0e-4:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("Input argument should lay in the profile plane"),
                    traceback.format_exc())

            slope_radians = abs(radians(intersection_vector.dip_angle()))

            scalar_product_for_downward_sense = self.vector().dot_product(intersection_vector.downward())
            if scalar_product_for_downward_sense > 0.0:
                intersection_downward_sense = "right"
            elif scalar_product_for_downward_sense == 0.0:
                intersection_downward_sense = "vertical"
            else:
                intersection_downward_sense = "left"

            return (slope_radians, intersection_downward_sense), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def calculate_pt_intersection_along_axis(
        self,
        project_axis: Axis,
        pt: Point
    ) -> Tuple[Union[Point, 'ParamLine3D', type(None)], Error]:
        """
        Calculates the optional intersection point between an axis passing through a point
        and the profilers plane.

        :param project_axis: the projection axis.
        :param pt: the point through which the axis passes.
        :return: the optional intersection point.
        :raise: Exception.
        """

        axis_versor = project_axis.as_direction().as_versor()

        l, m, n = axis_versor.x, axis_versor.y, axis_versor.z

        axis_param_line = ParamLine3D(pt, l, m, n)

        return intersect_plane_with_line(axis_param_line, self.vertical_plane())

    def intersect_with_plane(
            self,
            plane: Plane,
            pt: Point
    ) -> Tuple[Union[type(None), Vect3D], Error]:
        """
        Calculate the intersection versor between the segment profilers and
        a plane passing through a point.

        :param plane: the plane orientation.
        :param pt: the record location.
        :return: an optional intersection versor and the error status.
        """

        try:

            # input type checks

            check_type(plane, "Attitude plane", Plane)
            check_type(pt, "Attitude point", Point)

            # calculate intersection versor

            vert_pln = self.vertical_plane()
            if vert_pln is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("the vertical plane is None"),
                    traceback.format_exc())

            intersection, err = vert_pln.intersects_other(
                CPlane3D.from_geol_plane(plane, pt))

            if err:
                return None, err

            if isinstance(intersection, CPlane3D):
                return None, Error(
                    True,
                    caller_name(),
                    Exception("the section and the attitude plane coincide"),
                    traceback.format_exc())

            if not intersection.is_valid():
                return None, Error(
                    True,
                    caller_name(),
                    Exception("intersection is not valid"),
                    traceback.format_exc())

            return intersection, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def nearest_coplanar_projection(
            self,
            plane_attitude: Plane,
            position: Point
    ) -> Tuple[Union[type(None), Point], Error]:
        """
        Calculates the nearest projection of a given attitude on a vertical plane.

        :param plane_attitude: plane attitude.
        :param  position: attitude position.
        :return: the nearest projected point on the vertical section.
        :raise: Exception.
        """

        try:

            check_type(plane_attitude, "Plane attitude", Plane)
            check_type(position, "Position", Point)

            attitude_cplane = CPlane3D.from_geol_plane(
                geol_plane=plane_attitude,
                pt=position)

            intersection, err = self.vertical_plane().intersects_other(attitude_cplane)

            if err:
                return None, err

            if isinstance(intersection, CPlane3D):
                return None, Error(
                    True,
                    caller_name(),
                    Exception("unhandled degenerate case where section and attitude coincides."),
                    traceback.format_exc()
                )

            if not intersection.is_valid():
                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"intersection vector is not valid: {intersection}"),
                    traceback.format_exc()
                )

            vert_plane = self.vertical_plane()
            if vert_plane is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("vertical plane is None"),
                    traceback.format_exc()
                )

            dummy_inters_pt, err = vert_plane.intersects_other_as_pt(attitude_cplane)
            if err:
                return None, err

            dummy_structural_vect = Segment(dummy_inters_pt, position).as_vector3d()
            dummy_distance = dummy_structural_vect.dot_product(intersection)
            offset_vector = intersection.scale(dummy_distance)

            projected_pt = Point(
                dummy_inters_pt.x + offset_vector.x,
                dummy_inters_pt.y + offset_vector.y,
                dummy_inters_pt.z + offset_vector.z
            )

            return projected_pt, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def project_point(
            self,
            point: Point,
            projection_method: ProjectionMethod = ProjectionMethod.NEAREST,
            min_profile_distance: numbers.Real = MIN_DISTANCE_TOLERANCE,
            map_axis: Optional[Axis] = None,
            attitude: Optional[Plane] = None,
            axis_angular_tolerance: numbers.Real = MIN_DISORIENTATION_TOLERANCE
    ) -> Tuple[Union[type(None), Point], Error]:
        """
        Project a point to the segment according to various methods.

        :param point: the point to project.
        :param projection_method: the projection method.
        :param min_profile_distance: the minimum distance of the point from the section to be considered not lying on the section plane.
        :param map_axis: the optional axis to project the point to the section.
        :param attitude: the optional attitude along which to profiles the point to the plane.
        :param axis_angular_tolerance: the minimum angular tolerance (in degrees) between axis and plane.
        :return: the projected point and the error status.
        """

        try:

            # input type checks

            check_type(point, "Position", Point)
            check_type(min_profile_distance, "Min point distance from profile", numbers.Real)

            # get point distance from section plane and possibly return result

            section_plane = self.vertical_plane()
            if section_plane is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("Returned vertical plane from segment profile is None"),
                    traceback.format_exc()
                )

            if projection_method == ProjectionMethod.NEAREST:

                return section_plane.project_point(
                    pt=point,
                    distance_atol=min_profile_distance)

            elif projection_method in (ProjectionMethod.COMMON_AXIS, ProjectionMethod.INDIVIDUAL_AXES):

                return section_plane.project_point(
                    pt=point,
                    axis=map_axis,
                    distance_atol=min_profile_distance,
                    angular_atol=axis_angular_tolerance)

            elif projection_method == ProjectionMethod.ALONG_PLANE:  # project along attitude

                result, err = intersect_plane_with_attitude(
                    section_plane,
                    attitude,
                    point)

                if err:
                    return None, err
                if result is None:
                    return None, Error()

                _, inters_point = result
                return inters_point, Error()

            else:

                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"Projection method is {projection_method}"),
                    traceback.format_exc()
                )

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def project_attitude(
            self,
            attitude: Plane,
            point: Point,
            projection_method: ProjectionMethod = ProjectionMethod.NEAREST,
            min_profile_distance: numbers.Real = MIN_DISTANCE_TOLERANCE,
            map_axis: Optional[Axis] = None,
            axis_angular_tolerance: numbers.Real = MIN_DISORIENTATION_TOLERANCE
    ) -> Tuple[Union[type(None), Tuple[Vect3D, Point]], Error]:
        """
        Project an attitude point to the segment according to various methods.

        :param attitude: the attitude to plot to the plane section.
        :param point: the point defining the attitude location.
        :param projection_method: the projection method.
        :param min_profile_distance: the minimum distance of the point from the section to be considered not lying on the section plane.
        :param map_axis: the optional axis to project the point to the section.
        :param axis_angular_tolerance: the minimum angular tolerance (in degrees) between axis and plane.
        :return: the intersection and an error status.
        """

        try:

            # get vertical section plane

            section_plane = self.vertical_plane()
            if section_plane is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("Returned vertical plane from segment profile is None"),
                    traceback.format_exc())

            # define projected attitude location

            if projection_method == ProjectionMethod.NEAREST:
                result, err = section_plane.project_point(
                    pt=point,
                    distance_atol=min_profile_distance)
            elif projection_method in (ProjectionMethod.COMMON_AXIS, ProjectionMethod.INDIVIDUAL_AXES):
                result, err = section_plane.project_point(
                    pt=point,
                    axis=map_axis,
                    distance_atol=min_profile_distance,
                    angular_atol=axis_angular_tolerance
                )
            else:  # project along attitude
                result, err = intersect_plane_with_attitude(
                    cartes_plane=section_plane,
                    attitude=attitude,
                    point=point
                )

            if err:
                return None, err

            if result is None:
                return None, Error()

            if isinstance(result, Point):
                projected_pt = result
            else:
                _, projected_pt = result

            # calculate intersection geometry between attitude and plane

            intersection, err = versor_from_plane_attitude_inters(
                cartes_plane=section_plane,
                attitude=attitude,
                point=point
            )

            if err:
                return None, err

            return (intersection, projected_pt), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def project_line(
        self,
        line: Ln,
        projection_method: ProjectionMethod = ProjectionMethod.NEAREST,
        min_profile_distance: numbers.Real = MIN_DISTANCE_TOLERANCE,
        map_axis: Optional[Axis] = None,
        attitude: Optional[Plane] = None,
        axis_angular_tolerance: numbers.Real = MIN_DISORIENTATION_TOLERANCE
    ) -> Tuple[Union[type(None), Ln], Error]:
        """
        Project a line to the segment according to various methods.

        :param line: the line to project.
        :param projection_method: the projection method.
        :param min_profile_distance: the minimum distance of the point from the section to be considered not lying on the section plane.
        :param map_axis: the optional axis to project the point to the section.
        :param attitude: the optional attitude along which to plot the point to the plane.
        :param axis_angular_tolerance: the minimum angular tolerance (in degrees) between axis and plane.
        """

        try:

            projected_line = Ln()

            for pt in line.pts():

                projected_pt, err = self.project_point(
                    point=pt,
                    projection_method=projection_method,
                    min_profile_distance=min_profile_distance,
                    map_axis=map_axis,
                    attitude=attitude,
                    axis_angular_tolerance=axis_angular_tolerance
                )

                if err:
                    return None, err

                if projected_pt is not None:
                    projected_line.add_pt(projected_pt)

            return projected_line, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def parse_multipoints_intersections(
            self,
            intersections: Dict[Category, List[UnionPtSegment2D]],
            offset: numbers.Real = 0.0
    ) -> List[IdentifiedArrays]:
        """
        Parse the profile intersections for incorporation
        as elements in a geoprofile.

        :param intersections: the intersections
        :param offset: the offset to apply to the calculated values, to comply with LineProfilers
        :return: the list of resulting along-profile distances.
        """

        parsed_intersections = []

        for rec_id, ptsegm2d_list in intersections.items():
            intersections_arrays = [self.pt_segm_along_profile_signed_s(ptsegm2d, offset) for ptsegm2d in ptsegm2d_list]
            parsed_intersections.append(IdentifiedArrays(rec_id, intersections_arrays))

        return parsed_intersections

    def parse_single_point_projection_result(self,
                                             source_pt: Point,
                                             intersection_point: Point,
                                             max_profile_distance,
                                             offset: numbers.Real = 0.0,
                                             ) -> Tuple[Union[type(None), PointTrace], Error]:
        """
        Parse a point intersection for plotting in a section.

        :param source_pt: the source point.
        :param intersection_point: the projected point in the section plane.
        :param max_profile_distance: the maximum allowed distance of the source point form the section plane.
        :param offset: the s distance offset to apply to the segment-calculated one.
        :return: the potential point trace for plotting, and the error status.
        """

        try:

            # distance between source and projected points

            dist = source_pt.distance(intersection_point)

            if dist > max_profile_distance:
                return None, Error()

            # horizontal spat_distance between projected point and profile start

            signed_distance_from_section_start = self.point_along_profile_signed_s(intersection_point.to2d())
            if signed_distance_from_section_start is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("DEBUG: <signed_distance_from_section_start> is None"),
                    traceback.format_exc()
                )
            elif not (0.0 <= signed_distance_from_section_start <= self.length()):
                return None, Error()

            # solution for current point

            parsed_point_intersection = PointTrace(
                s=signed_distance_from_section_start + offset,
                z=intersection_point.z,
                dist=dist,
            )

            return parsed_point_intersection, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def parse_single_attitude_projection_result(self,
                                                attitude: Plane,
                                                attitude_intersection: Vect3D,
                                                source_pt: Point,
                                                intersection_point: Point,
                                                max_profile_distance,
                                                offset: numbers.Real = 0.0,
                                                ) -> Tuple[Union[type(None), PlaneTrace], Error]:
        """
        Parse an attitude intersection for plotting in a section.

        :param attitude: the attitude plane.
        :param attitude_intersection: the section-attitude intersection vector.
        :param source_pt: the attitude source point.
        :param intersection_point: the projected point in the section plane.
        :param max_profile_distance: the maximum allowed distance of the source point form the section plane.
        :param offset: the s distance offset to apply to the segment-calculated one.
        :return: the potential plane trace for plotting, and the error status.
        """

        try:

            # calculate slope of geological plane onto section plane

            result, error = self.get_intersection_slope(attitude_intersection)
            if error:
                return None, error

            slope_radians, intersection_downward_sense = result

            # distance between source and projected points

            dist = source_pt.distance(intersection_point)

            if dist > max_profile_distance:
                return None, Error()

            # horizontal spat_distance between projected structural point and profile start

            signed_distance_from_section_start = self.point_along_profile_signed_s(intersection_point.to2d())
            if signed_distance_from_section_start is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("DEBUG: <signed_distance_from_section_start> is None"),
                    traceback.format_exc()
                )
            elif not (0.0 <= signed_distance_from_section_start <= self.length()):
                return None, Error()

            # solution for current structural point

            parsed_plane_trace = PlaneTrace(
                s=signed_distance_from_section_start + offset,
                z=intersection_point.z,
                slope_degr=degrees(slope_radians),
                down_sense=intersection_downward_sense,
                dist=dist,
                src_dip_dir=attitude.dipazim,
                src_dip_ang=attitude.dipang
            )

            return parsed_plane_trace, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def parse_traces_with_attitudes_intersections(self,
        vect_points_intersections: List[Tuple[Vect3D, Point]],
        plane_orientation: Plane,
        offset: numbers.Real = 0.0,
    ) -> Tuple[Union[type(None), List[PlaneTrace]], Error]:
        """
        Parse an attitude intersection for plotting in a section.

        :param vect_points_intersections: the attitude plane.
        :param plane_orientation: the section-attitude intersection vector.
        :param offset: the s distance offset to apply to the segment-calculated one.
        :return: the potential plane trace for plotting, and the error status.
        """

        try:

            parsed_traces = []

            for attitude_intersection, intersection_point_2d in vect_points_intersections:

                # calculate slope of geological plane onto section plane

                result, error = self.get_intersection_slope(attitude_intersection)

                if error:
                    return None, error

                slope_radians, intersection_downward_sense = result

                # horizontal distance between structural point and profile start

                signed_distance_from_section_start = self.point_along_profile_signed_s(intersection_point_2d.to2d())

                if signed_distance_from_section_start is None:
                    return None, Error(
                        True,
                        caller_name(),
                        Exception("DEBUG: <signed_distance_from_section_start> is None"),
                        traceback.format_exc()
                    )

                if not (0.0 <= signed_distance_from_section_start <= self.length()):
                    return None, Error()

                # solution for current structural point

                parsed_plane_trace = PlaneTrace2D(
                    s=signed_distance_from_section_start + offset,
                    slope_degr=degrees(slope_radians),
                    down_sense=intersection_downward_sense,
                    src_dip_dir=plane_orientation.dipazim,
                    src_dip_ang=plane_orientation.dipang
                )

                parsed_traces.append(parsed_plane_trace)

            return parsed_traces, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())


class LineProfiler:
    """
    Ln profilers.
    """

    def __init__(self,
                 src_trace: Ln,
                 s_breaks: Optional[np.ndarray] = None
                 ):
        """
        Initialize the parallel linear profilers.

        :param src_trace: the source line for profilers creation
        :param s_breaks: the optional array of distances breaks
        """

        self._profile_line = src_trace.clone()

        if s_breaks is None:
            self._s_breaks = np.array(src_trace.accumulated_length_2d())
        else:
            self._s_breaks = s_breaks

    def clone(self) -> 'LineProfiler':
        """Clone the LineProfiler instance"""

        return LineProfiler(
            src_trace=self._profile_line,
            s_breaks=self._s_breaks
        )

    def __iter__(self):
        """
        Return the segment profilers of the current line profilers.
        """

        return (SegmentProfiler(segment) for segment in self.line)

    def __repr__(self):
        """
        Representation of a profile instance.

        :return: the textual representation of the instance.
        """

        return f"LineProfiler(\n\tsource line = {self._profile_line})"

    @property
    def line(self) -> Ln:
        """
        Returns the line profile.

        :return: the line profile.
        """

        return self._profile_line

    @property
    def s_breaks(self) -> np.ndarray:
        """
        Returns the along-profile cumulated segment lengths.

        :return: the along-profile cumulated segment lengths.
        """

        return self._s_breaks

    def length(self) -> numbers.Real:
        """
        Returns the length of the profilers section.

        :return: length of the profilers section.
        """

        return self._profile_line.length_2d()

    def densified_points(self,
                         sampling_distance) -> List[Point]:
        """
        Returns the list of densified 2D points when respecting source line original vertices.
        """

        segments = list(self._profile_line.segments())
        pts = []
        for ndx, segment in enumerate(segments):
            densified_points = segment.densify_as_points2d(densify_distance=sampling_distance)
            if ndx == len(segments) - 1:
                pts.extend(densified_points)
            else:
                pts.extend(densified_points[:-1])

        return pts

    def profile_grid_as_ztrace(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None,
            enforce_segment_vertices: bool = False
    ) -> Tuple[Union[type(None), ZTrace], Error]:
        """
        Create profile from a grid, given a sampling distance.

        :param grid: the source grid.
        :param sampling_distance: the sampling distance
        :param enforce_segment_vertices: whether to constrain the profile to use segment vertices
        :return: the profile of the scalar variable stored in the grid.
        """

        try:

            if enforce_segment_vertices:

                z_traces = []
                for segment_profiler in self:

                    z_trace, err = segment_profiler.profile_grid_as_ztrace(
                        grid,
                        sampling_distance)

                    if err:
                        return None, err

                    z_traces.append(z_trace)

                joined_ztrace, err = join_ztraces(*z_traces)

                if err:
                    return None, err

            else:

                # convert line to equally spaced points

                if sampling_distance is None:
                    sampling_distance = grid.cellsize_mean
                equally_spaced_points = self._profile_line.densify_as_equally_spaced_points2d(
                    sample_distance=sampling_distance
                )

                # sample grid using points
                x_values = [n*sampling_distance for n in range(len(equally_spaced_points))]
                y_values = [grid.interpolate_bilinear(pt.x, pt.y) for pt in equally_spaced_points]

                joined_ztrace = ZTrace(
                    x_array=np.array(x_values),
                    y_array=np.array(y_values),
                    breaks=self._s_breaks
                )

            return joined_ztrace, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def profile_grid_as_pts3d(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None,
            enforce_segment_vertices: bool = False,
            atol: numbers.Real = MIN_POINT_POS_DIFF,
    ) -> Tuple[Union[type(None), List[Point]], Error]:
        """
        Create profile from a grid, given a sampling distance.

        :param grid: the source grid.
        :param sampling_distance: the sampling distance
        :param enforce_segment_vertices: whether to constrain the profile to use segment vertices
        :param atol: the absolute tolerance between consecutive points distance.
        :return: the profile of the scalar variable stored in the grid.
        """

        try:

            if enforce_segment_vertices:

                total_points = []
                for segment_profiler in self:
                    points_3d, err = segment_profiler.profile_grid_as_pts3d_with_nans(grid, sampling_distance)
                    if err:
                        return None, err
                    total_points.extend(points_3d)

            else:

                # convert line to equally spaced points

                if sampling_distance is None:
                    sampling_distance = grid.cellsize_mean
                equally_spaced_points = self._profile_line.densify_as_equally_spaced_points2d(
                    sample_distance=sampling_distance
                )

                pts_3d = map(lambda pt2d: grid.interpolate_bilinear_point_with_nan(pt2d), equally_spaced_points)
                total_points = list(filter(lambda pt3d: pts_3d is not None, pts_3d))

            total_points = remove_coincident_points_2d(total_points, atol=atol)

            return total_points, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def intersect_lines(self,
                        lines: List[Ln],
                        ) -> List[UnionPtSegment2D]:
        """
        Calculates the attitude_intersection with a set of lines.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param lines: an iterable of Lines or MultiLines to intersect profile with
        :return: the possible intersections
        """

        intersections = []
        for segment_profiler in self:
            result = segment_profiler.intersect_lines(lines)
            if result:
                intersections.extend(result)
        return intersections

    def intersect_lines_with_attitude(
        self,
        lines: List[Ln],
        plane_orientation: Plane
    ) -> Tuple[Union[type(None), List[PlaneTrace]], Error]:

        try:

            plane_traces = []
            segment_offset = 0.0

            for segment_profiler in self:

                result, err = segment_profiler.intersect_lines_with_attitude(
                    lines,
                    plane_orientation
                )

                if err:
                    print(f"Error: {err!r} ")
                    continue

                if result is None:
                    print(f"Warning: segment-profilers / line-attitude intersections are None")
                    continue

                vect_points_intersections = result  #List[Tuple[Vect3D, Point]]]

                result, err = segment_profiler.parse_traces_with_attitudes_intersections(
                    vect_points_intersections,
                    plane_orientation,
                    segment_offset,
                )

                if err:
                    print(f"Error: {err!r} ")
                    continue

                if result is None:
                    print(f"Warning: segment-profilers / line-attitude intersections are None")
                    continue

                plane_traces.extend(result)
                segment_offset += segment_profiler.length()

            return plane_traces, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )

    def intersect_polygon(self,
                          polygon: Polygon,
                          ) -> List[Segment]:
        """
        Calculates the attitude_intersection with a polygon.
        Note: the intersections are considered flat, i.e., in a 2D plane, not 3D.

        :param polygon: the polygon/multipolygon to intersect profile with
        :return: the possible intersections
        """

        segments = []

        for segment_profiler in self:
            segments.extend(segment_profiler.intersect_polygon(polygon))

        return segments

    def intersect_polygons(self,
                           polygons: Dict[Category, List[Polygon]]
                           ) -> Dict[Category, List[Segment]]:
        """
        Calculates the attitude_intersection with a list of polygon.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param polygons: the list of polygons to intersect profile with
        :return: the possible intersections
        """

        intersections = defaultdict(list)

        for polygons_id, polygons_geometries in polygons.items():

            for polygon_geom in polygons_geometries:
                intersections[polygons_id].extend(self.intersect_polygon(polygon_geom))

        return intersections

    def project_points(
        self,
        points: List[Tuple[Category, Point, Fault]],
        max_profile_distance: numbers.Real,
        projection_method: ProjectionMethod = ProjectionMethod.NEAREST,
        **kwargs
    ) -> Tuple[Union[type(None), Dict[Category, List[PointTrace]]], Error]:
        """
        Projects a set of 3D points onto the section profile.

        :param points: the set of 3D points to project onto the section.
        :param max_profile_distance: the maximum allowed projection distance between the points and the profile.
        :param projection_method: the method to use for projecting the points onto the section.
        :param kwargs: the keyword arguments.
        :return: dictionary storing projected points and error status.
        """

        try:

            #print(f"Projecting points for LineProfiler instance")

            if projection_method == ProjectionMethod.NEAREST:
                map_axes = None
            elif projection_method == ProjectionMethod.COMMON_AXIS:
                map_axes = Axis(kwargs['trend'], kwargs['plunge'])
            elif projection_method == ProjectionMethod.INDIVIDUAL_AXES:
                map_axes = [Axis(trend, plunge) for trend, plunge in kwargs['individual_axes_values']]
            else:
                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"Mapping method is {projection_method}"),
                    traceback.format_exc())

            #print(f"Defined projection map axes")

            projected_points = defaultdict(list)

            for ndx_super, (category, position, fault) in enumerate(points):

                #print(f"Projecting point #{ndx_super} - category {category}")

                previous_segments_offset = 0

                for ndx, segment_profiler in enumerate(self):

                    intersection_point, err = segment_profiler.project_point(
                        point=position,
                        projection_method=projection_method,
                        min_profile_distance=MIN_DISTANCE_TOLERANCE,
                        map_axis=map_axes if not isinstance(map_axes, list) else map_axes[ndx],
                        axis_angular_tolerance=MIN_DISORIENTATION_TOLERANCE
                    )

                    if err:
                        return None, err

                    if intersection_point is None:
                        return None, Error()

                    point_trace, err = segment_profiler.parse_single_point_projection_result(
                        source_pt=position,
                        intersection_point=intersection_point,
                        max_profile_distance=max_profile_distance,
                        offset=previous_segments_offset
                    )

                    if err:
                        return None, err

                    if point_trace is not None:
                        projected_points[category].append(point_trace)

                    previous_segments_offset += segment_profiler.length()

            best_projections = defaultdict(PointTrace)

            for category, solutions in projected_points.items():
                if len(solutions) == 1:
                    best_projections[category] = solutions[0]
                else:
                    min_distance = min([solution.dist for solution in solutions])
                    for solution in solutions:
                        if solution.dist <= min_distance:
                            best_projections[category] = solution
                            break

            return best_projections, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def project_attitudes(
        self,
        attitudes: List[Tuple[Category, Point, Plane]],
        max_profile_distance: numbers.Real,
        projection_method: ProjectionMethod,
        **kwargs
    ) -> Tuple[Union[type(None), Dict[Category, PlaneTrace]], Error]:
        """
        Projects a set of space3d attitudes onto the section profile.

        :param attitudes: the set of georeferenced space3d attitudes to plot on the section.
        :param max_profile_distance: the maximum projection distance between the plane_attitude and the profile
        :param projection_method: the method to map the attitudes to the section.
        :return: list of PlaneTrace values.
        """

        try:

            if projection_method == ProjectionMethod.NEAREST:
                map_axes = None
            elif projection_method == ProjectionMethod.COMMON_AXIS:
                map_axes = Axis(kwargs['trend'], kwargs['plunge'])
            elif projection_method == ProjectionMethod.INDIVIDUAL_AXES:
                map_axes = [Axis(trend, plunge) for trend, plunge in kwargs['individual_axes_values']]
            else:
                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"Mapping method is {projection_method}"),
                    traceback.format_exc())

            """
            if mapping_method['method'] not in ('nearest', 'common axis', 'individual axes', 'attitude'):
                return None, Error(True, caller_name(), Exception(
                    f"Mapping method is '{mapping_method['method']}'. One of 'nearest', 'common axis', 'individual axes', 'attitude' expected"))

            if mapping_method['method'] == 'individual axes' and len(mapping_method['individual_axes_values']) != len(attitudes):
                return None, Error(True, caller_name(), Exception(
                    f"Individual axes values are {len(mapping_method['individual_axes_values'])} but attitudes are {len(attitudes)}"))

            if mapping_method['method'] == 'nearest':
                map_axes = None
            elif mapping_method['method'] == 'common axis':
                map_axes = Axis(mapping_method['trend'], mapping_method['plunge'])
            else:
                map_axes = [Axis(trend, plunge) for trend, plunge in mapping_method['individual_axes_values']]
            """

            projected_attitudes = defaultdict(list)

            for ndx, (attitude_id, position, attitude) in enumerate(attitudes):

                previous_segments_offset = 0

                for segment_profiler in self:

                    result, err = segment_profiler.project_attitude(
                        attitude=attitude,
                        point=position,
                        projection_method=projection_method,
                        min_profile_distance=MIN_DISTANCE_TOLERANCE,
                        map_axis=map_axes if not isinstance(map_axes, list) else map_axes[ndx],
                        axis_angular_tolerance=MIN_DISORIENTATION_TOLERANCE
                    )

                    if err:
                        return None, err

                    if result is None:
                        return None, Error()

                    intersection, intersection_point = result

                    profile_attitude, err = segment_profiler.parse_single_attitude_projection_result(
                        attitude=attitude,
                        attitude_intersection=intersection,
                        source_pt=position,
                        intersection_point=intersection_point,
                        max_profile_distance=max_profile_distance,
                        offset=previous_segments_offset
                    )

                    if err:
                        return None, err

                    if profile_attitude is not None:
                        projected_attitudes[attitude_id].append(profile_attitude)

                    previous_segments_offset += segment_profiler.length()

            best_attitude_projections = defaultdict(PlaneTrace)
            for attitude_id, solutions in projected_attitudes.items():
                if len(solutions) == 1:
                    best_attitude_projections[attitude_id] = solutions[0]
                else:
                    min_distance = min([solution.dist for solution in solutions])
                    for solution in solutions:
                        if solution.dist <= min_distance:
                            best_attitude_projections[attitude_id] = solution
                            break

            return best_attitude_projections, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def vector_offset(self,
                      vect: Vect2D
                      ) -> 'LineProfiler':
        """
        Returns a new LineProfiler instance, horizontally offset by the
        provided vector horizontal components.
        """

        return LineProfiler(
            src_trace=self._profile_line.shift_horiz(vect.x, vect.y),
            s_breaks=self._s_breaks
        )

    def right_parallel_offset(self,
                              offset: numbers.Real
                              ) -> 'LineProfiler':
        """
        Returns a copy of the current linear profilers, offset to the right by the provided offset distance.

        :param offset: the lateral offset to apply to create the new LinearProfiler.
        :return: the offset linear profilers.
        """

        return self.vector_offset(
            vect=self._profile_line.as_segment().right_norm_vers2d().scale(offset))

    def left_parallel_offset(self,
                             offset: numbers.Real
                             ) -> 'LineProfiler':
        """
        Returns a copy of the current linear profilers, offset to the left by the provided offset distance.

        :param offset: the lateral offset to apply to create the new LinearProfiler.
        :return: the offset linear profilers.
        """

        return self.vector_offset(vect=self._profile_line.as_segment().left_norm_vers2d().scale(offset))

    def parse_multipoints_intersections(
            self,
            intersections: Dict[Category, List[UnionPtSegment2D]]
    ) -> List[IdentifiedArrays]:
        """
        Parse the profile intersections for incorporation
        as elements in a geoprofile.

        :param intersections: the intersections
        :return: the list of resulting along-profile distances.
        """

        array_lists = []

        offset = 0.0

        for segment_profiler in self:
            array_lists.extend(segment_profiler.parse_multipoints_intersections(intersections, offset))
            offset += segment_profiler.length()

        return array_lists


class Profilers(list):
    """
    Profilers.
    """

    def __init__(self,
                 src_trace: Ln,
                 num_profiles: numbers.Integral = 1,
                 offset: numbers.Real = 50,  # horizontal distance unit, e.g. meters
                 profiles_arrangement: str = "central",  # one of: "left", "central", "right"
                 ):
        """
        Initialize the profilers.

        :param src_trace: the source trace.
        :param num_profiles: the number of profilers to create. Default is 1.
        :param offset: the lateral offset between profilers. Default is 50 horizontal units.
        :param profiles_arrangement: profiles arrangement: one of "left", "central", "right". Default is "central".
        :return: the profilers.
        """

        if num_profiles < 1:
            raise Exception("Profilers number must be >= 1")

        if profiles_arrangement == "central" and num_profiles % 2 != 1:
            raise Exception("When profilers arrangement is 'central' profilers number must be odd")

        if profiles_arrangement == "central":

            side_profs_num = num_profiles // 2
            num_left_profs = num_right_profs = side_profs_num

        elif profiles_arrangement == "left":

            num_left_profs = num_profiles - 1
            num_right_profs = 0

        else:

            num_right_profs = num_profiles - 1
            num_left_profs = 0

        profilers = []

        base_profiler = LineProfiler(src_trace=src_trace)

        for i in range(num_left_profs, 0, -1):

            current_offset = offset * i

            profilers.append(base_profiler.left_parallel_offset(offset=current_offset))

        profilers.append(base_profiler.clone())

        for i in range(1, num_right_profs + 1):

            current_offset = offset * i

            profilers.append(base_profiler.right_parallel_offset(offset=current_offset))

        super(Profilers, self).__init__(profilers)

    def __repr__(self) -> str:
        """
        Represents a parallel linear profilers set.

        :return: the textual representation of the parallel linear profilers set.
        """

        inner_profilers = "\n".join([repr(profiler) for profiler in self])
        return "Profilers([\n{}]\n)".format(inner_profilers)

    @property
    def lines(self) -> List[Ln]:
        """
        Returns the profiles lines.

        :return: the parallel profilers lines.
        """

        return [profiler.line for profiler in self]

    def profile_grid_as_ztraces(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None
    ) -> Tuple[Union[type(None), ZTraces], Error]:
        """
        Create profile from a grid.

        :param grid: the source grid.
        :param sampling_distance: the grid sampling distance.
        :return: list of profiles of the scalar variable stored in the grid and an error status.
        """

        try:

            z_traces = []

            for line_profiler in self:

                z_trace, err = line_profiler.profile_grid_as_ztrace(
                    grid=grid,
                    sampling_distance=sampling_distance
                )

                if err:
                    return None, err
                z_traces.append(z_trace)

            return ZTraces.fromProfiles(z_traces), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def profile_grid_as_pts3d(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None
    ) -> Tuple[Union[type(None), List[List[Point]]], Error]:
        """
        Create profile from a grid.

        :param grid: the source grid.
        :param sampling_distance: the grid sampling distance.
        :return: list of profiles of the scalar variable stored in the grid and an error status.
        """

        try:

            profiles_3d = []

            print(f"There are {len(self)} line profilers in self")

            for line_profiler in self:

                pts_3d, err = line_profiler.profile_grid_as_pts3d(
                    grid=grid,
                    sampling_distance=sampling_distance
                )

                if err:
                    return None, err

                profiles_3d.append(pts_3d)

            print(f"There are {len(profiles_3d)} line profilers in profiles_3d")

            return profiles_3d, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def profile_grid_as_zarrays(
            self,
            grid: Grid,
            sampling_distance: Optional[numbers.Real] = None
    ) -> Tuple[Union[type(None), np.ndarray], Error]:
        """
        Create profile from a grid as ZArray.

        :param grid: the source grid.
        :param sampling_distance: the grid sampling distance.
        :return: list of profiles of the scalar variable stored in the grid and an error status.
        """

        try:

            topo_profiles = []

            for line_profiler in self:

                z_array, err = line_profiler.profile_grid_as_ztrace(
                    grid=grid,
                    sampling_distance=sampling_distance
                )

                if err:
                    return None, err
                topo_profiles.append(z_array)

            return ZTraces.fromProfiles(topo_profiles), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def intersect_lines(self,
                        lines: Dict[Category, List[Ln]]
                        ) -> List[Dict[Category, List[UnionPtSegment2D]]]:

        intersections = []

        for line_profiler in self:
            profile_intersections = defaultdict(list)
            for lines_id, lines_geoms in lines.items():
                result = line_profiler.intersect_lines(lines_geoms)
                if result:
                    profile_intersections[lines_id] = result
            intersections.append(profile_intersections)

        return intersections

    def intersect_lines_with_attitudes(self,
        lines: Dict[Category, Tuple[Plane, List[Ln]]]
    ) -> Tuple[Union[type(None), List[Dict[Category, List[PlaneTrace]]]], Error]:

        try:

            profiles_plane_traces = []

            for line_profiler in self:

                line_profile_plane_traces = defaultdict(list)

                for lines_id, unpacked_data in lines.items():

                    if isinstance(unpacked_data, List):

                        for plane_orientation, rec_id_lines in unpacked_data:

                            plane_traces, err = line_profiler.intersect_lines_with_attitude(
                                lines=rec_id_lines,
                                plane_orientation=plane_orientation)
                            if err:
                                repr(err)
                                continue
                            if plane_traces:
                                line_profile_plane_traces[lines_id] = plane_traces
                            else:
                                print(f"Warning: plane traces for record id {lines_id} is {plane_traces}")

                    else:

                        plane_orientation, rec_id_lines = unpacked_data

                        plane_traces, err = line_profiler.intersect_lines_with_attitude(
                            lines=rec_id_lines,
                            plane_orientation=plane_orientation)
                        if err:
                            repr(err)
                            continue
                        if plane_traces:
                            line_profile_plane_traces[lines_id] = plane_traces
                        else:
                            print(f"Warning: plane traces for record id {lines_id} is {plane_traces}")

                profiles_plane_traces.append(line_profile_plane_traces)

            return profiles_plane_traces, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def intersect_polygons(self,
                           polygons: Dict[Category, List[Polygon]]
                           ) -> List[Dict[Category, List[Segment]]]:
        """
        Calculates the profilers intersections with a set of polygon/multipolygon.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param polygons: the set of polygon/multipolygon to intersect profile with
        :return: the possible intersections
        """

        intersections = []

        for line_profiler in self:
            intersections.append(line_profiler.intersect_polygons(polygons))

        return intersections

    def project_points(
            self,
            points: List[Tuple[Category, Point]],
            max_profile_distance: numbers.Real,
            projection_method: ProjectionMethod = ProjectionMethod.NEAREST,
            **kwargs
    ) -> Tuple[Union[type(None), List[Dict[Category, List[PointTrace]]]], Error]:
        """
        Projects a set of points onto the section profile.

        :param points: the set of points to be plotted onto the section.
        :param max_profile_distance: the maximum allowed projection distance between the individual point and the profile
        :param projection_method: the method to project the points to the section.
        :param kwargs: the keyword arguments.
        :return: the parsed point traces and an error status.
        """

        try:

            point_traces = []

            for ndx, line_profiler in enumerate(self):
                #print(f"Processing profile {ndx}")
                profile_points, err = line_profiler.project_points(
                    points=points,
                    max_profile_distance=max_profile_distance,
                    projection_method=projection_method,
                    **kwargs
                )
                if err:
                    return None, err

                point_traces.append(profile_points)

            return point_traces, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def project_attitudes(
        self,
        attitudes: List[Tuple[Category, Point, Plane]],
        max_profile_distance: numbers.Real,
        projection_method: ProjectionMethod = ProjectionMethod.NEAREST,
    ) -> Tuple[Union[type(None), List[Dict[Category, PlaneTrace]]], Error]:
        """
        Projects a set of georeferenced space3d attitudes onto the section profile.

        :param attitudes: the set of georeferenced space3d attitudes to plot on the section.
        :param projection_method: the method to map the attitudes to the section.
        :param max_profile_distance: the maximum projection distance between the plane_attitude and the profile
        :return: an attitudes set and an error status.
        """

        try:

            plane_traces = []

            for line_profiler in self:

                profile_attitudes, err = line_profiler.project_attitudes(
                    attitudes=attitudes,
                    projection_method=projection_method,
                    max_profile_distance=max_profile_distance
                )
                if err:
                    return None, err

                plane_traces.append(profile_attitudes)

            return plane_traces, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def parse_multipoints_intersections(
            self,
            intersections_list: List[Dict[Category, List[UnionPtSegment2D]]]
    ) -> Optional[List[List[IdentifiedArrays]]]:
        """
        Parse the profile intersections for incorporation
        as elements in a geoprofile.

        :param intersections_list: the intersections for the various parallel profiles
        :return: the optional list of resulting along-profile distances.
        """

        array_lists = []

        if len(self) != len(intersections_list):
            return None

        for line_profiler, intersections in zip(self, intersections_list):
            array_lists.append(line_profiler.parse_multipoints_intersections(intersections))

        return array_lists


