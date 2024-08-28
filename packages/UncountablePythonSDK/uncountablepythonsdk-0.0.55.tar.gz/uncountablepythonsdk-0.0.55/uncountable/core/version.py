import functools
from importlib.metadata import PackageNotFoundError, version


@functools.cache
def get_version() -> str:
    try:
        version_str = version("UncountablePythonSDK")
    except PackageNotFoundError:
        version_str = "unknown"
    return version_str
