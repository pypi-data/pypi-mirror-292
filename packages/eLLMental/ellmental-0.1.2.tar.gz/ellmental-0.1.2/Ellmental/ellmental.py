import requests

class EllmentalError(Exception):
    """Custom exception for eLLMental errors."""
    pass

class Ellmental:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.test_suite_id = None
        self.test_execution_id = None
        self.pipelines_config = self._fetch_pipelines_config()

    def set_evaluation_context(self, test_suite_id):
        self.test_suite_id = test_suite_id

    def search_pipeline_query(self, pipeline_id, **params):
        pipeline_config = self._get_pipeline_config(pipeline_id)
        self._validate_params(pipeline_config, params)
        method = pipeline_config["input_config"]["method"]
        slug = pipeline_config["slug"]
        url = f"{self.base_url}/api/{self.pipelines_config['base_path']}/{slug}"
        headers = self._get_headers()

        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=params)
        else:
            raise EllmentalError(f"Unsupported HTTP method: {method}")
        
        return self._handle_response(response)

    def list_search_pipelines(self):
        return self.pipelines_config["pipelines"]

    def start_evaluation_execution(self):
        if not self.test_suite_id:
            raise ValueError("You need to set the evaluation context before starting a test execution")
        
        url = f"{self.base_url}/api/test_suites/{self.test_suite_id}/test_executions"
        headers = self._get_headers()
        response = requests.post(url, headers=headers)
        execution = self._handle_response(response)
        self.test_execution_id = execution["id"]

    def push_evaluation_result(self, test_case_id, test_result, status, metadata=None):
        if not self.test_suite_id or not self.test_execution_id:
            raise ValueError("You need to start a test execution before creating a test result")
        
        url = f"{self.base_url}/api/test_suites/{self.test_suite_id}/test_executions/{self.test_execution_id}/test_results"
        data = {
            "test_suite_id": self.test_suite_id,
            "test_case_id": test_case_id,
            "test_result": str(test_result),
            "user_metadata": metadata or {},
            "status": status
        }
        headers = self._get_headers()
        response = requests.post(url, json=data, headers=headers)
        return self._handle_response(response)

    def finish_evaluation_execution(self):
        if not self.test_suite_id or not self.test_execution_id:
            raise ValueError("You need to start a test execution before creating a test result")
        
        url = f"{self.base_url}/api/test_suites/{self.test_suite_id}/test_executions/{self.test_execution_id}/finish"
        headers = self._get_headers()
        response = requests.post(url, headers=headers)
        return self._handle_response(response)

    def list_evaluation_cases(self):
        if not self.test_suite_id:
            raise ValueError("You need to set the evaluation context before starting a test execution")
        url = f"{self.base_url}/api/test_suites/{self.test_suite_id}/test_cases"
        headers = self._get_headers()
        response = requests.get(url, headers=headers)
        return self._handle_response(response)
    
    def _fetch_pipelines_config(self):
        url = f"{self.base_url}/api/pipelines/configuration"
        headers = self._get_headers()
        response = requests.get(url, headers=headers)
        config = self._handle_response(response)
        return config

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _handle_response(self, response):
        if response.status_code not in [200, 201]:
            raise EllmentalError(f"Error {response.status_code}: {response.text}")
        return response.json()

    def _get_pipeline_config(self, pipeline_name):
        for pipeline in self.pipelines_config["pipelines"]:
            if pipeline["name"] == pipeline_name:
                return pipeline
        raise EllmentalError(f"Pipeline ID {pipeline_name} not found in configuration")

    def _validate_params(self, pipeline_config, params):
        expected_params = {param["name"]: param["type"] for param in pipeline_config["input_config"]["parameters"]}
        for param, value in params.items():
            if param not in expected_params:
                print(param)
                raise EllmentalError(f"Unexpected parameter: {param}")
            if not isinstance(value, str) and expected_params[param] == "text":
                raise EllmentalError(f"Parameter {param} should be of type {expected_params[param]}")
        for expected_param in expected_params.keys():
            if expected_param not in params:
                raise EllmentalError(f"Missing required parameter: {expected_param}")
