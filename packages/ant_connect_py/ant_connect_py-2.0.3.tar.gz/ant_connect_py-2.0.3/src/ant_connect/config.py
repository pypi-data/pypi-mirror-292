"""Configuration file for the whole antconnect v2 python package.
"""

import inspect
from pathlib import Path


model_base_class_name = "ModelBaseClass"
empty_default = inspect._empty


class HostUrlConfig:
    """Configuration for the host URL."""
    host: str = "https://api.antcde.io"
    data_model: str = "https://api.antcde.io/docs/2.0/api-docs-v2.json"
    type: str = "api"
    version: str = "2.0"
    documentation: str = "https://api.antcde.io/api/2.0/documentation"


class AlphaHostUrl:
    """Configuration for the alpha host URL."""
    host: str = "https://api.alpha.antcde.io"
    data_model: str = "https://api-alpha.antcde.io/docs/2.0/api-docs-v2.json"
    type: str = "api"
    version: str = "2.0"
    documentation: str = "https://api-alpha.antcde.io/api/2.0/documentation"


class TokenConfig:
    """Configuration for the token URL."""
    endpoint: str = "oauth/token"


class RequestsConfig:
    """Configuration for the requests made to the API."""
    verify: bool = True
    headers: dict = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "access_token_placeholder",
    }
    _placeholder_string: str = "Bearer {}"


class ThrottleConfig:
    """Configuration for the throttle settings."""
    amount: int = 120
    time_frame: int = 60


class Directories:
    """Configuration for the directories used in the package."""
    ROOT: Path = Path(__file__).parent.parent.parent
    DEV: Path = ROOT / "dev"
    TEST_DOCS: Path = DEV / "testing"
    PROJECT_SRC: Path = ROOT / "src" / "ant_connect"


class ProjectPaths:
    """Configuration for the project paths used in the package."""
    MODELS: Path = Directories.PROJECT_SRC / "models.py"
    LOCAL_DATA_MODEL: Path = Directories.DEV / "testing" / "api-docs-v2.15.json"
    MANUAL_FUNCTIONS: Path = Directories.PROJECT_SRC / "utils" / "manual_functions.py"
