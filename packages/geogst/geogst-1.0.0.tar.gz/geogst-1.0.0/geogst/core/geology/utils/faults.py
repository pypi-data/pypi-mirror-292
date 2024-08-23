
import numbers
from typing import Tuple

from geogst.core.inspections.errors import *
from geogst.core.inspections.errors import Error
from geogst.core.orientations.orientations import Plane


def opposite_rake(rake: numbers.Real) -> numbers.Real:
    """
    Calculate opposite rake (i.e., with inverted movement sense).

    Examples:
    >>> opposite_rake(0)
    180.0
    >>> opposite_rake(45)
    -135.0
    >>> opposite_rake(90)
    -90.0
    >>> opposite_rake(135)
    -45.0
    >>> opposite_rake(180)
    0.0
    >>> opposite_rake(-180)
    0.0
    >>> opposite_rake(-90)
    90.0
    >>> opposite_rake(-45)
    135.0
    """

    rake = (rake + 180.0) % 360.0
    if rake > 180.0:
        rake = rake - 360.0

    return rake


if __name__ == "__main__":

    import doctest
    doctest.testmod()


def downaxis_from_rake(
        dipdir,
        dipang,
        rk
) -> Union[Error, Tuple[numbers.Real, numbers.Real]]:

    dir, err = Plane(dipdir, dipang).rake_to_direct(float(rk))
    if err:
        return err

    return dir.downward().d
