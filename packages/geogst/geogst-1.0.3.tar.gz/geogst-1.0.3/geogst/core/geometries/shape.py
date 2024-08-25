import abc

from geogst.core.deformations.space3d.rotations import *


class Shape(object, metaclass=abc.ABCMeta):

    proper_space: int
    embedding_space: int

    @abc.abstractmethod
    def area(self):
        """Calculate shape area"""

    @abc.abstractmethod
    def length(self):
        """Calculate shape length"""

    @abc.abstractmethod
    def clone(self) -> 'Shape':
        """
        Clone a shape."""

    @property
    def dimension(self) -> numbers.Integral:
        """The embedding space dimension of the shape instance"""
        return type(self).embedding_space


Category = Union[str, numbers.Integral]


if __name__ == "__main__":
    import doctest

    doctest.testmod()

