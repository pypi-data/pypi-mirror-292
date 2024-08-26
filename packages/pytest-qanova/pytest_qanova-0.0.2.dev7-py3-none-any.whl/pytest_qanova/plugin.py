"""This module contains changed pytest for QaNova."""

import logging
import time
from Interface.QaNovaAgent import AgentConfig
import dill as pickle
import pytest
import requests
from Interface.PyTestService import PyTestServiceClass

log = logging.getLogger(__name__)


@pytest.hookimpl(optionalhook=True)
def pytest_configure_node(node):
    """Configure xdist node controller.

    :param node: Object of the xdist WorkerController class
    """
    if not node.config.qn_enabled:
        # Stop now if the plugin is not properly configured
        return
    node.workerinput['py_test_service'] = pickle.dumps(node.config.py_test_service)


def is_control(config):
    """Validate workerinput attribute of the Config object.

    True if the code, running the given pytest.config object,
    is running as the xdist control node or not running xdist at all.
    """  # noqa
    return not hasattr(config, 'workerinput') # noqa


def wait_launch(rp_client):
    """Wait for the launch startup.

    :param rp_client: Instance of the ReportPortalService class
    """
    timeout = time.time()
    while not rp_client.launch_id:
        if time.time() > timeout:
            return False
        time.sleep(1)
    return True


def pytest_sessionstart(session): # noqa
    """Start Report Portal launch.

    This method is called every time on control or worker process start, it
    analyses from which process it is called and starts a Report Portal launch
    if it's a control process.
    :param session: Object of the pytest Session class
    """
    config = session.config
    if not config.qn_enabled:
        return

    if is_control(config):
        try:
            config = config.py_test_service.start_session(config)
        except Exception as response_error:
            log.warning('Failed to initialize QaNova client service. Reporting is disabled.')
            log.debug(str(response_error))
            config.qn_enabled = False
            return
        

def pytest_sessionfinish(session): # noqa
    """Finish current test session.

    :param session: Object of the pytest Session class
    """
    config = session.config
    if not config.qn_enabled:
        # Stop now if the plugin is not properly configured
        return


def register_markers(config):
    """Register plugin's markers, to avoid declaring them in `pytest.ini`.

    :param config: Object of the pytest Config class
    """
    config.addinivalue_line(
        "markers", "issue(issue_id, reason, issue_type, url): mark test with "
                   "information about skipped or failed result"
        )
    config.addinivalue_line(
        "markers", "tc_id(id, parameterized, params): report the test"
                   "case with a custom Test Case ID. Parameters: \n"
                   "parameterized [True / False] - use parameter values in "
                   "Test Case ID generation \n"
                   "params [parameter names as list] - use only specified"
                   "parameters"
        )


def check_connection(agent_config: AgentConfig) -> bool:
    """Check connection to RP using provided options.

    If connection is successful returns True either False.
    :param agent_config: Instance of the AgentConfig class
    :return True on successful connection check, either False
    """
    url = '{0}check-connection/'.format(agent_config.qn_endpoint)
    headers = {'QaNovaToken': f'{agent_config.qn_token}'}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def pytest_configure(config):
    """Update Config object with attributes required for reporting to RP.

    :param config: Object of the pytest Config class
    """
    register_markers(config)
    if bool(config.option.token and config.option.endpoint):
        config.qn_enabled = True
    if not config.qn_enabled:
        return

    qa_nova_config = AgentConfig(config)

    cond = (qa_nova_config.qn_token, qa_nova_config.qn_enabled)
    config.qn_enabled = all(cond)

    if qa_nova_config:
        config.qn_enabled = check_connection(qa_nova_config)

    if not config.qn_enabled:
        return

    config.qa_nova_config = qa_nova_config

    if is_control(config):
        config.py_test_service = PyTestServiceClass(qa_nova_config)
    else:
        config.py_test_service = pickle.loads(config.workerinput['py_test_service'])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa
    """
        Change runtest_makereport function.

    :param item: pytest.Item
    :return: None
    """# noqa
    config = item.config
    if not config.qn_enabled:
        return
    yield
    config.py_test_service.update_test_case(item, call)
    

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    config = item.config
    if not config.qn_enabled:
        return
    config.py_test_service.create_empty_result(item)
    """
    Hook called before the execution of each test function.
    This is a good place to perform setup actions or logging.

    :param item: The test item that is about to be executed.
    """
    # Print the name of the test function before it runs
    print(f"Setting up for test: {item.name}")
    

def pytest_addoption(parser): # noqa
    """Add support for the RP-related options.

    :param parser: Object of the Parser class
    """
    group = parser.getgroup('QaNova')

    def add_shared_option(name, help_str, default=None, action='store'):
        """
        Add an option to both the command line and the .ini file.

        This function modifies `parser` and `group` from the outer scope.

        :param name:     name of the option
        :param help_str: help message
        :param default:  default value
        :param action:   `group.addoption` action
        """ # noqa
        parser.addini(
            name=name,
            default=default,
            help=help_str,
            )
        group.addoption(
            '--{0}'.format(name.replace('_', '-')),
            action=action,
            dest=name,
            help='{help} (overrides {name} config option)'.format(
                help=help_str,
                name=name,
                ),
            )

    group.addoption(
        '--qanova', # noqa
        action='store_true',
        dest='qn_enabled',
        default=False,
        help='Enable QaNova Plugin'
        )
    add_shared_option(
        name='token',
        help_str='Authentication token',
        default='',
        )
    add_shared_option(
        name='endpoint',
        help_str='Base Endpoint to QaNova application.',
        default='',
        )
