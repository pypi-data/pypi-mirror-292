
from typing import Optional, Union


class Error:
    """
    Class to manage errors Go-style.
    """

    def __init__(self,
                 error: bool = False,
                 caller: Optional[Union[type(None), str]] = None,
                 exception: Optional[Union[type(None), Exception]] = None,
                 traceback_infos: Union[type(None), str] = None
    ):
        """
        Examples:
        >>> bool(Error())
        False
        >>> err = Error(True, "my_function", Exception("sample exception"))
        >>> bool(err)
        True
        >>> print(err)
        sample exception
        """

        self.error = error
        self.caller = caller
        self.exception = exception
        self.traceback_infos = traceback_infos

    def __bool__(self):

        return self.error

    def __repr__(self):

        if self.error:
            return f"Exception with {self.caller}: {self.exception}\nExtended infos: {self.traceback_infos}"
        else:
            return ''

    def __str__(self):

        if self.error:
            return f"{self.exception}"
        else:
            return ''

if __name__ == "__main__":

    import doctest

    doctest.testmod()
