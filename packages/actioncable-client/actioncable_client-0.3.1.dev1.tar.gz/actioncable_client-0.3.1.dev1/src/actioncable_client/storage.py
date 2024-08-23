# Copyright 2024 Liant SASU
#
# License: MIT
# See: LICENSE file at root of the repository
#
# Author: Roland Laurès <roland@liant.dev>
"""
ActionCable local storage facility.
"""

from typing import Union, Optional, Any
from pathlib import Path
from bson import dumps, loads # type: ignore


class Storage:
    """
    The connection to a ActionCable capable server.

    You can use the #save(obj, file) method and implement a #from_file(file)
    in your Object to make it persist or getting back it's value.
    """
    def __init__(self, location: Path = Path.home() / f'.{__package__}'):
        """
        :param location: Where to store the things that will be asked to be
          stored. It will be resolve as absolute if it is not already
        """
        self._location = location.absolute()
        if not self._location.exists():
            self._location.mkdir()

    def get_location(self) -> Path:
        """Getter function for 'location' property."""
        return self._location

    location = property(get_location, doc='Base folder for the saved files')

    def save(self, obj: dict, filedest: Optional[Union[Path, str]] = None):
        """
        Save :obj to :filedest. If not specified, the object will be stored
          in `obj.__class__.__name__.lower()` and then will be storethen be warn
          that several object of the same class will be overwritten.

          :param obj: The object to save.
          :param filedest: (Optional) The Path to save the object.
            If absolute, the file will be written to the specified location.
            If not set, it will be stored in `self.location`.
        """
        filedest = Path(obj.__class__.__name__) if filedest is None else Path(filedest)

        if filedest.is_absolute():
            filedest = filedest.with_suffix('.bin')
        else:
            filedest = self._location / filedest.with_suffix('.bin')
        with filedest.open('bw') as f:
            f.write(dumps(obj))

    def load(self, filesource: Union[Path, str]) -> Union[Any, dict, list[dict]]:
        """
        Load :filesource when it has been saved by pickle (or with Storage#save
          method).

          :param filesource: The Path from which to load the object (you can
            omit the '.bin' extension). If relative, it will be loaded from
            the `self._location` directory
        """

        # coerce type from str|Path to Path and add '.bin' extension
        filesource = Path(filesource).with_suffix('.bin')
        filesource = self._location / filesource if not filesource.is_absolute() else filesource
        with filesource.open('b+r') as f:
            return loads(f.read())
