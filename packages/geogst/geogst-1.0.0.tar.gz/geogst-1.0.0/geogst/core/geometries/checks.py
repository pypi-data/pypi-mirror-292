
from geogst.core.geometries.shape import *


def check_equal_dimension(
        first: Shape,
        second: Shape):
    """Check that the two shapes have equal dimension."""

    return first.embedding_space == second.embedding_space



if __name__ == "__main__":
    import doctest

    doctest.testmod()

