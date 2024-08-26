from typing import Optional
from .QaNovaAgent import AgentConfig
from pytest import Item, Config, CallInfo
from functools import wraps
from .ApiClient import ApiClient
from .PathReader import collect_and_share_test_data
import traceback


empty_result = {
                        'setup': {
                                'outcome': None,
                                'duration': None,
                                'longrepr': None, # noqa
                                'error_type': None,
                                'error_message': None
                                },
                        'call': {
                                    'outcome': None,
                                    'duration': None,
                                    'longrepr': None, # noqa
                                    'error_type': None,
                                    'error_message': None
                                    },
                        'teardown': {
                                'outcome': None,
                                'duration': None,
                                'longrepr': None, # noqa
                                'error_type': None,
                                'error_message': None
                                }
    }


def check_qn_enabled(func):
    """Verify is qn_enabled is enabled in config."""

    @wraps(func)
    def wrap(*args, **kwargs):
        if args and isinstance(args[0], PyTestServiceClass):
            if not args[0].qn_enabled:
                return
        return func(*args, **kwargs)

    return wrap


class PyTestServiceClass(ApiClient):
    """Pytest service class for reporting test results to the QaNova application."""

    # config: AgentConfig
    # session_id: Optional[str]
    # agent_name: str
    # agent_version: str

    def __init__(self, agent_config: AgentConfig) -> None:
        """Initialize instance attributes."""
        self.config = agent_config
        self.qn_enabled = self.config.qn_enabled
        self._token = self.config.qn_token
        super().__init__(self.config.qn_endpoint, self._token)
        self.session_id: Optional[str] = None
        self.agent_name = 'pytest-qanova' # noqa
        self.agent_version = '1.1'  # get_package_version(self.agent_name)
        self.session_started = False
        self.collection_started = False
        self.tests = dict()
    
    @check_qn_enabled
    def start_session(self, pytest_config: Config) -> Config:
        self.session_started = True
        rootdir = None
        inifile = None
        command_line = ' '.join(pytest_config.invocation_params.args)
        if hasattr(pytest_config, 'rootdir'):
            rootdir = str(pytest_config.rootdir) if pytest_config.rootdir else None
        if hasattr(pytest_config, 'inifile'):
            inifile = str(pytest_config.inifile) if pytest_config.inifile else None
        args = pytest_config.args
        options = {key: value for key, value in vars(pytest_config.option).items()}
        
        # Prepare session info
        pytest_config.session_info = {
            'state': 1,
            'command_line': command_line,
            'rootdir': rootdir,
            'inifile': inifile,
            'args': args,
            'options': options
            }
        
        """Start a new session."""
        endpoint = '/session/'
        # Share session_id with all workers
        
        response = self.sync.post(endpoint, pytest_config.session_info)
        self.session_id = response['id']
        return pytest_config
    
    @check_qn_enabled
    def end_session(self, session_id) -> dict:
        """End a session."""
        endpoint = f'/sessions/{session_id}/end'
        return self.sync.post(endpoint, {})
    
    @check_qn_enabled
    def _create_test_case(self, test_case_data) -> dict:
        """Create a new test case."""
        endpoint = '/ml/testcases/'
        return self.sync.post(endpoint, test_case_data)
    
    @check_qn_enabled
    def _create_test_case_result(self, test_case_data) -> dict:
        """Update an existing test case."""
        endpoint = f'/ml/results/'
        return self.sync.post(endpoint, test_case_data)
    
    @check_qn_enabled
    def create_empty_result(self, item):
        nodeid = item.nodeid  # noqa
        item.results = {
            'session': self.session_id,
            'status': 1,  # 'collected'
            'test_case': None,
            'result_data': empty_result
            }
        
        # Collect information about the test case
        test_info = collect_and_share_test_data(nodeid)
        markers = [{marker.name: marker.kwargs if marker.kwargs else None} for marker in item.iter_markers()]
        test_info['markers'] = markers
        test_info['session'] = self.session_id
        
        test_response = self._create_test_case(test_info)
        item.results['test_case'] = test_response['id']
        result = self._create_test_case_result(item.results)
        item.result_id = result['id']
    
    @check_qn_enabled
    def update_test_case(self, item: Item, call: CallInfo) -> dict:
        phase = call.when
        # Change local status
        if hasattr(item, 'results'):
            if 'skip' in [a.name for a in item.own_markers]:
                item.results['status'] = 5  # skip
            if item.results['status'] != 4 and item.results['status'] != 5:
                item.results['status'] = 2  # running
        
            # Determine the outcome based on excinfo # noqa
            if call.excinfo is None:
                outcome = 'passed'
            else:
                outcome = 'failed'
            
            # Record the outcome and duration for the current phase
            item.results['result_data'][phase]['outcome'] = outcome
            item.results['result_data'][phase]['duration'] = call.duration
            
            if outcome == 'failed':  # The test phase failed
                exception_info = call.excinfo
                error_type = exception_info.type.__name__
                error_message = traceback.format_exception_only(exception_info.type, exception_info.value)
                
                # Use format_exception to get the full traceback as a string
                traceback_text = str(
                    call.excinfo.getrepr(funcargs=True, showlocals=True, truncate_locals=True).reprtraceback)
                
                item.results['status'] = 4  # 'failed'
                item.results['result_data'][phase]['longrepr'] = traceback_text  # The traceback information # noqa
                item.results['result_data'][phase]['error_type'] = error_type
                item.results['result_data'][phase]['error_message'] = error_message
            """Asynchronously update an existing test case."""
            if call.when == 'teardown':
                if item.results['status'] != 4 and item.results['status'] != 5:
                    item.results['status'] = 3
            data = {
                'status': item.results['status'],
                'result_data': item.results['result_data']
                }
            if hasattr(item, 'result_id'):
                test_result_id = item.result_id
                endpoint = f'/ml/results/{test_result_id}/'
                response = self.sync.put(endpoint, data)
                return response
    
    
