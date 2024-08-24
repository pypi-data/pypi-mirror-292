
from typing import Tuple, List, Union
import traceback
import os

from geogst.core.inspections.errors import *
from geogst.core.inspections.functions import *


def find_filenames_in_folder(
    folder_path: str
) -> Tuple[List[str], Error]:

    try:

        filenames = sorted(filter(lambda fl: os.path.isfile, os.listdir(folder_path)))
        return filenames, Error()

    except Exception as e:

        return [], Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def find_filepaths_in_folder(
    folder_path: str
) -> Tuple[List[str], Error]:

    try:

        filenames = sorted(filter(lambda fl: os.path.isfile, os.listdir(folder_path)))
        filepaths = list(map(lambda filename: os.path.join(folder_path, filename), filenames))
        return filepaths, Error()

    except Exception as e:

        return [], Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def try_find_files_in_folder(
        folder_path: str
) -> Tuple[bool, Union[str, List[str]]]:
    """
    Deprecated: use 'find_filenames_in_folder'.
    """

    try:

        file_paths = sorted(filter(lambda fl: os.path.isfile, os.listdir(folder_path)))
        return True, file_paths

    except Exception as e:

        return False, f"{e!r}"


def try_find_tif_files_in_folder(
    folder_path: str
) -> Tuple[bool, Union[str, List[str]]]:
    """
    Returns sorted paths of tif files in folder
    """

    try:

        success, result = try_find_files_in_folder(folder_path)
        if not success:
            msg = result
            return False, msg

        tif_file_paths = sorted(filter(lambda fl: fl.lower().endswith(".tif"), result))

        return True, tif_file_paths

    except Exception as e:

        return False, f"{e!r}"


def find_filenames_with_extension_in_folder(
    folder_path: str,
    extension: str,
) -> Tuple[List[str], Error]:
    """
    Returns sorted paths of files with provided extension in folder
    """

    try:

        result, err = find_filenames_in_folder(folder_path)
        if err:
            return [], err

        filenames_with_extension = sorted(filter(lambda fl: fl.lower().endswith(extension), result))

        return filenames_with_extension, Error()

    except Exception as e:

        return [], Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def find_filepaths_with_extension_in_folder(
    folder_path: str,
    extension: str,
) -> Tuple[List[str], Error]:
    """
    Returns sorted paths of files with provided extension in folder
    """

    try:

        result, err = find_filenames_in_folder(folder_path)
        if err:
            return [], err

        filenames_with_extension = sorted(filter(lambda fl: fl.lower().endswith(extension), result))
        filepaths_with_extension = list(map(lambda filename: os.path.join(folder_path, filename), filenames_with_extension))
        return filepaths_with_extension, Error()

    except Exception as e:

        return [], Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )

if __name__ == '__main__':

    pass

