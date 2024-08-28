import os
import json
import requests

"""from .exceptions import (
    AuthenticationFailedError,
    DuplicateDocumentContentError,
    DuplicateKnowledgeBaseError,
    DocumentLengthError,
    InternalServerError,
    InvalidRequestError,
    NotFoundError,
)"""


_BASE_URL = "http://0.0.0.0:8000"

def set_base_url(url: str):
    global _BASE_URL
    _BASE_URL = url

def get_base_url():
    return _BASE_URL


################## ERROR HANDLING ##################
"""def read_errors():
    module_path = os.path.abspath(__file__)
    module_dir = os.path.dirname(module_path)
    errors_path = os.path.join(module_dir, 'errors.json')
    
    with open(errors_path) as file:
        errors_data = json.load(file)
    
    return errors_data


ERRORS = {e['code']: e for e in read_errors()}"""


def make_api_call(args: dict) -> dict:
    """exception_classes = {
        "AuthenticationFailedError": AuthenticationFailedError,
        "DuplicateDocumentContentError": DuplicateDocumentContentError,
        "DocumentLengthError": DocumentLengthError,
        "InternalServerError": InternalServerError,
        "InvalidRequestError": InvalidRequestError,
        "NotFoundError": NotFoundError,
        "TimeoutError": TimeoutError,
        "DuplicateKnowledgeBaseError": DuplicateKnowledgeBaseError
    }"""

    resp = requests.request(**args)
    headers = resp.headers
    if resp.ok and args['method'] == 'DELETE':
        return True
    elif not resp.ok and args['method'] == 'DELETE':
        resp_json = {}
    else:
        resp_json = resp.json()
    if headers.get('error_code'):
        # error_code = int(headers['error_code'])
        raise Exception(resp_json, resp.status_code)
        """if error_code in ERRORS:
            try:
                _exp = exception_classes[ERRORS[error_code]['python_sdk_exception']]
                raise _exp(resp_json, resp.status_code)
            except KeyError:
                raise Exception(resp_json, resp.status_code)
        else:
            raise Exception(resp_json, resp.status_code)"""
    elif not resp.ok:
        raise Exception(resp_json, resp.status_code)
    else:
        return resp_json