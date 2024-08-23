
from geogst.core.profiles.profilers import *
#from geogst.core.profiles.profiletraces import *
from geogst.core.profiles.methods import *
from geogst.core.profiles.profiletraces import *
from geogst.core.utils.arrays import *


class GeoProfile:
    """
    Class representing the topographic and geological elements
    representing a single geological profile.
    """

    def __init__(
        self,
        topo_profile: Union[type(None), ZTrace] = None,
        points_projections: Union[
         type(None),
         Dict[
             Category,
             Union[
                  Dict[Category, PointTrace],
                  Dict[Category, PlaneTrace],
                  Dict[Category, Fault]
             ]
         ]
        ] = None,
        lines_intersections: Union[
         type(None),
         List[
             List[
                 Tuple[
                     Category, Optional[List[UnionPtSegment2D]]]
             ]
         ]
        ] = None,
        lines_intersections_with_attitudes: Union[
         type(None),
         List[
             Dict[
                 Category,
                 List[PlaneTrace]
             ]
         ]
        ] = None,
        polygons_intersections: Union[
         type(None),
         List[
             List[
                 Tuple[
                     Category,
                     Optional[
                         List[UnionPtSegment2D]
                     ]
                 ]
             ]
         ]
        ] = None,
    ):

        if topo_profile:
            check_type(topo_profile, "Topographic profile", ZTrace)

        self._topo_profile = topo_profile
        self._points_projections = points_projections
        self._lines_intersections = lines_intersections
        self._lines_intersections_with_attitudes = lines_intersections_with_attitudes
        self._polygons_intersections = polygons_intersections

    @property
    def points_projections(self):
        return self._points_projections

    @points_projections.setter
    def points_projections(self, value):
        self._points_projections = value

    @property
    def lines_intersections(self):
        return self._lines_intersections

    @lines_intersections.setter
    def lines_intersections(self, value):
        self._lines_intersections = value

    @property
    def lines_intersections_with_attitudes(self):
        return self._lines_intersections_with_attitudes

    @lines_intersections_with_attitudes.setter
    def lines_intersections_with_attitudes(self, value):
        self._lines_intersections_with_attitudes = value

    @property
    def polygons_intersections(self):
        return self._polygons_intersections

    @polygons_intersections.setter
    def polygons_intersections(self, value):
        self._polygons_intersections = value

    def has_topography(self) -> bool:
        """
        Check if geoprofile has topography set.
        """

        return self._topo_profile is not None

    def clear_topo_profile(self):
        """

        :return:
        """

        self._topo_profile = None

    def s_min(self):
        """

        :return:
        """

        return self._topo_profile.x_min()

    def s_max(self):
        """

        :return:
        """

        return self._topo_profile.x_max()

    def z_min(self):
        """

        :return:
        """

        return self._topo_profile.y_min()

    def z_max(self):
        """

        :return:
        """

        return self._topo_profile.y_max()

    def length_2d(self) -> numbers.Real:
        """
        Returns the 2D length of the profile.

        :return: the 2D profile length.
        :rtype: numbers.Real.
        """

        return self._topo_profile.x_length()


class GeoProfiles:
    """
    Represents an ensemble of Geoprofile elements, stored as a list.
    It is related to parallel profiles products.
    """

    def __init__(self, profilers: Profilers):

        self._profilers = profilers
        self._topo_profiles = None  # ZTraces, to be possibly converted to List of ZTraces
        self._points_projections = {}
        self._lines_intersections = None
        self._lines_with_attitudes_intersections = None
        self._polygons_intersections = None

    def set_topo_profiles_from_grid(self,
                                    grid: Grid,
                                    sampling_distance: Optional[numbers.Real] = None
                                    ) -> Error:
        """
        Set profile from a grid.

        :param grid: the source grid.
        :param sampling_distance: the grid sampling distance.
        :return: an error status.
        """

        try:

            result, err = self._profilers.profile_grid_as_ztraces(
                grid=grid,
                sampling_distance=sampling_distance)

            if err:
                return err

            self._topo_profiles = result

            return Error()

        except Exception as e:

            return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def intersect_lines(self,
                        lines: Dict[Category, List[Ln]]
                        ) -> Error:
        """
        Calculates the profiles intersections with a set of lines.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param lines: the lines to intersect profile with
        :return: the error status.
        """

        try:

            intersections = self._profilers.intersect_lines(
                lines=lines
            )

            self._lines_intersections = self._profilers.parse_multipoints_intersections(intersections)

            return Error()

        except Exception as e:

            return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def intersect_lines_with_attitudes(self,
        lines: Dict[Category, List[Tuple[Plane, List[Ln]]]]
    ) -> Error:
        """
        Calculates the profiles intersections with a set of lines.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param lines: the lines to intersect profile with
        :return: the error status.
        """

        try:

            intersections, err = self._profilers.intersect_lines_with_attitudes(
                lines=lines
            )

            if err:
                return err

            self._lines_with_attitudes_intersections = intersections

            return Error()

        except Exception as e:

            return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def intersect_polygons(self,
        polygons: Dict[Category, List[Polygon]]
    ) -> Error:
        """
        Calculates the profiles intersections with a set of polygon.
        Note: the intersections are intended flat (in a 2D plane, not 3D).

        :param polygons: the list of polygons to intersect with profile
        :return: the error status.
        """

        try:

            poly_intersections = self._profilers.intersect_polygons(
                polygons=polygons
            )

            parsed_intersections = []

            for prof_intersections in poly_intersections:
                parsed_dict = defaultdict(list)
                for cat_id, segments in prof_intersections.items():
                    if segments:
                        parsed_dict[cat_id] = segments #lines_to_points_segments(lines=lines)
                parsed_intersections.append(parsed_dict)

            self._polygons_intersections = self._profilers.parse_multipoints_intersections(parsed_intersections)
            # -> List[List[IdentifiedArrays]]

            return Error()

        except Exception as e:

            return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def project_points(self,
        data: List,
        max_profile_distance: numbers.Real,
        projection_method: ProjectionMethod = ProjectionMethod.NEAREST,
        input_type: PointsInput = PointsInput.POINTS,
        cat_key: str = "points",
        **kargs
    ) -> Error:
        """
        Proiect points onto the geoprofiles.

        :param data: a list of point dataset.
        :param max_profile_distance: the maximum point distance from the profile.
        :param projection_method: the projection method to use for the points.
        :param input_type: the type of the input dataset. Default is points.
        :param cat_key: the category name of the point dataset.
        :return: the error status.
        """

        try:

            if input_type == PointsInput.POINTS:
                parsed_dataset, err = self._profilers.project_points(
                    points=data,
                    max_profile_distance=max_profile_distance,
                    projection_method=projection_method,
                    **kargs
                )
            elif input_type == PointsInput.ATTITUDES:
                parsed_dataset, err = self._profilers.project_attitudes(
                    attitudes=data,
                    max_profile_distance=max_profile_distance,
                    projection_method=projection_method
                )
            elif input_type == PointsInput.FAULTS:
                parsed_dataset, err = None, Error(
                    True,
                    caller_name(),
                    Exception(f"Faults not implemented"),
                    traceback.format_exc())
            elif input_type == PointsInput.FOCAL_MECHANISMS:
                parsed_dataset, err = None, Error(
                    True,
                    caller_name(),
                    Exception(f"Focal mechanisms not implemented"),
                    traceback.format_exc())
            else:
                parsed_dataset, err = None, Error(
                    True,
                    caller_name(),
                    Exception(f"Got not implemented point input type: {input_type}"),
                    traceback.format_exc())

            if err:
                return err

            self._points_projections[cat_key] = parsed_dataset

            return Error()

        except Exception as e:

            return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def __len__(self) -> numbers.Integral:
        """
        Return the number of geoprofiles.
        """

        return self.num_profiles()

    def __getitem__(self,
        ndx: numbers.Integral
    ) -> GeoProfile:
        """
        Return the GeoProfile associated to the provided index.

        :param ndx: the index of the geoprofile to extract.
        :return: the geoprofile associated to the provided index.
        """

        # parse points projections
        if self._points_projections is None:
            profile_point_projections = None
        else:
            profile_point_projections = {}
            for point_dataset_key in self._points_projections.keys():
                point_dataset_profile_dict = self._points_projections[point_dataset_key][ndx]
                profile_point_projections[point_dataset_key] = point_dataset_profile_dict

        return GeoProfile(
            topo_profile=self._topo_profiles[ndx] if self._topo_profiles and ndx < self._topo_profiles.num_profiles() else None,
            points_projections=profile_point_projections,
            lines_intersections=self._lines_intersections[ndx] if self._lines_intersections and ndx < len(self._lines_intersections) else None,
            lines_intersections_with_attitudes=self._lines_with_attitudes_intersections[ndx] if self._lines_with_attitudes_intersections and ndx < len(self._lines_with_attitudes_intersections) else None,
            polygons_intersections=self._polygons_intersections[ndx] if self._polygons_intersections and ndx < len(self._polygons_intersections) else None
        )

    def __iter__(self):
        """
        Iter the Geoprofiles instance.
        """

        return (self[ndx] for ndx in range(len(self)))

    def have_topographies(self) -> bool:
        """
        Check if topographies defined.
        """

        return self._topo_profiles is not None

    def num_profiles(self) -> numbers.Integral:
        """
        Returns the number of profiles in the geoprofile set.

        :return: number of profiles in the geoprofile set.
        :rtype: numbers.Integral.
        """

        return 0 if self._topo_profiles is None else self._topo_profiles.num_profiles()

    '''
    def extract_geoprofile(
            self,
            ndx: numbers.Integral
    ) -> GeoProfile:
        """
        Returns a geoprofile referencing slices of stored data.

        :param ndx: the index of the geoprofile.
        :return: the extracted Geoprofile or None.
        :raise: Exception.
        """

        if ndx not in range(self.num_profiles()):
            raise Exception("Geoprofile set range is in 0-{} but {} got".format(self.num_profiles() - 1, ndx))

        return GeoProfile(
            topo_profile=self._topo_profiles[ndx] if self._topo_profiles and ndx < self._topo_profiles.num_profiles() else None,
            profile_attitudes=self.attitudes[ndx] if self.attitudes and ndx < len(self.attitudes) else None,
            points=self._points_projections[ndx] if self._points_projections and ndx < len(self._points_projections) else None,
            lines_intersections=self._lines_intersections[ndx] if self._lines_intersections and ndx < len(self._lines_intersections) else None,
            polygons_intersections=self._polygons_intersections[ndx] if self._polygons_intersections and ndx < len(self._polygons_intersections) else None
        )
    '''

    def s_min(self):
        """

        :return:
        """

        return self._topo_profiles.s_min()

    def s_max(self):
        """

        :return:
        """

        return self._topo_profiles.s_max()

    def z_min(self):
        """

        :return:
        """

        return self._topo_profiles.z_min()

    def z_max(self):
        """

        :return:
        """

        return self._topo_profiles.z_max()

    def profiles_lengths_2d(self) -> List[numbers.Real]:
        """
        Returns the 2D lengths of the profiles.

        :return: the 2D profiles lengths.
        :rtype: list of numbers.Real values.
        """

        return [topoprofile.profile_length_2d() for topoprofile in self._topo_profiles]

    def profiles_lengths_3d(self) -> List[numbers.Real]:
        """
        Returns the 3D lengths of the profiles.

        :return: the 3D profiles lengths.
        :rtype: list of numbers.Real values.
        """

        return [topoprofile.profile_length_3d() for topoprofile in self._topo_profiles]

    def max_length_2d(self) -> Optional[numbers.Real]:
        """
        Returns the maximum 2D length of profiles.

        :return: the maximum profiles lengths.
        :rtype: an optional numbers.Real value.
        """

        lengths = self.profiles_lengths_2d()

        if lengths:
            return np.nanmax(lengths)
        else:
            return None

    def sample_grid(self,
                    grid: Grid,
                    sampling_distance: Optional[numbers.Real] = None
                    ) -> Error:
        """
        Create profiles from a grid.

        :param grid: the source grid.
        :param sampling_distance: the grid sampling distance.
        :return: an error status.
        """

        try:

            result, err = self._profilers.profile_grid_as_ztraces(
                grid=grid,
                sampling_distance=sampling_distance)

            if err:
                return err

            self._topo_profiles = result

        except Exception as e:

            return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())


class MultiGridsProfiles:
    """
    Class storing multi grids profiles along a single spatial trace.
    """

    def __init__(self, profiler: LineProfiler):

        self._profiler = profiler

        self._zarray = ZArray()

    def add_profile_from_grid(self,
        grid: Grid,
        sampling_distance: Optional[numbers.Real] = None,
        name: str = "undefined"
    ) -> Error:
        """
        Set profile from a grid.

        :param grid: the source grid.
        :param sampling_distance: the grid sampling distance.
        :return: an error status.
        """

        try:

            result, err = self._profiler.profile_grid_as_ztrace(
                grid=grid,
                sampling_distance=sampling_distance)

            if err:
                return err

            z_trace = result

            self._zarray.add_profile(
                z_trace=z_trace,
                name=name)

            return Error()

        except Exception as e:

            return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def clear_profiles(self):
        """

        :return:
        """

        self._zarray = ZArray()

    def __getitem__(self,
        ndx: numbers.Integral
    ) -> GeoProfile:
        """
        Return the GeoProfile associated to the provided index.

        :param ndx: the index of the geoprofile to extract.
        :return: the geoprofile associated to the provided index.
        """

        return GeoProfile(
            topo_profile=self._zarray[ndx] if 0 <= ndx < self._zarray.num_profiles() else None,
        )

    def num_profiles(self) -> numbers.Integral:
        """
        Returns the number of profiles in the MultiGridsProfiles instance.

        :return: number of profiles in the MultiGridsProfiles instance.
        :rtype: numbers.Integral.
        """

        return 0 if self._zarray is None else self._zarray.num_profiles()

    def __len__(self) -> numbers.Integral:
        """
        Return the number of profiles in the MultiGridsProfiles instance.
        """

        return self.num_profiles()

    def __iter__(self):
        """
        Iter the Geoprofiles instance.
        """

        return (self[ndx] for ndx in range(len(self)))

    def s_min(self):
        """

        :return:
        """

        return self._zarray.s_min()

    def s_max(self):
        """

        :return:
        """

        return self._zarray.s_max()

    def z_min(self):
        """

        :return:
        """

        return self._zarray.z_min()

    def z_max(self):
        """

        :return:
        """

        return self._zarray.z_max()

    def length_2d(self) -> numbers.Real:
        """
        Returns the 2D length of the profile.

        :return: the 2D profile length.
        :rtype: numbers.Real.
        """

        return self.s_max()

