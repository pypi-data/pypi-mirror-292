"""This module contains class that stores QaNova agent configuration data."""

from typing import Any

from _pytest.config import Config


class AgentConfig:
    """Storage for the QaNova agent initialization attributes."""

    qn_enabled = False
    qn_token = None
    qn_endpoint = None
    qn_collection_started = None

    def __init__(self, pytest_config: Config) -> None:
        """Initialize required attributes."""
        self.qn_enabled = pytest_config.qn_enabled if hasattr(pytest_config, "qn_enabled") else False
        self.qn_token = self.find_option(pytest_config, 'token')
        self.qn_endpoint = self.find_option(pytest_config, 'endpoint')

    def find_option(self, pytest_config: Config, option_name: str, default: Any = None) -> Any:
        """
        Find a single configuration setting from multiple places.

        The value is retrieved in the following places in priority order:

        1. From `self.pconfig.option.[option_name]`.
        2. From `self.pconfig.getini(option_name)`.

        :param pytest_config: config object of PyTest
        :param option_name:   name of the option
        :param default:       value to be returned if not found
        :return: option value
        """ # noqa
        value = (
                getattr(pytest_config.option, option_name, None) or
                pytest_config.getini(option_name)
            )
        if isinstance(value, bool):
            return value
        return value or default
    