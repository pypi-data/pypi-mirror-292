__version__ = "0.1.3"

def version()->str:
    """Return the version of the lib

    Parameters
    ----------
    
    Returns
    -------
    str
        The string with version
    """
    return __version__

# str functions
from .file import FileUtils, TFileError

__all__ = [version, FileUtils, TFileError]