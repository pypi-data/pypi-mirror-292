from .db_manager import Connection
import pkg_resources

__version__ = pkg_resources.get_distribution('bugpy').version
print(f"Loaded bugpy version v{__version__}")