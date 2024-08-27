import os
from typing import Optional, Any
import json
import threading
from functools import wraps

from .rpc.rpc import call_rpc
from .utils import create_data


def call(url: str, workspace_api_key: Optional[str] = None, data: Optional[dict] = None, callback: Optional[Any] = None,
         inputs: Optional[dict] = None, is_batch: Optional[bool] = False):
    """
    Call Inferless API
    :param url: Inferless Model API URL
    :param workspace_api_key: Inferless Workspace API Key
    :param data: Model Input Data as a dictionary, example: {"question": "What is the capital of France?", "context": "Paris is the capital of France."}
    :param callback: Callback function to be called after the response is received
    :param inputs: Model Input Data in inferless format
    :param is_batch: Whether the input is a batch of inputs, default is False
    :return: Response from the API call
    """
    try:
        if inputs is not None and data is not None:
            raise Exception("Cannot provide both data and inputs")

        if data is not None:
            inputs = create_data(data, is_batch)

        import requests
        if workspace_api_key is None:
            workspace_api_key = os.environ.get("INFERLESS_API_KEY")
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {workspace_api_key}"}
        if inputs is None:
            inputs = {}
        response = requests.post(url, data=json.dumps(inputs), headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Failed to call {url} with status code {response.status_code} and response {response.text}")
        if callback is not None:
            callback(None, response.json())
        return response.json()
    except Exception as e:
        if callback is not None:
            callback(e, None)
        else:
            raise e


def call_async(url: str, workspace_api_key: Optional[str] = None, data: Optional[dict] = None,
               callback: Any = None, inputs: Optional[dict] = None, is_batch: Optional[bool] = False):
    """
    Call Inferless API
    :param url: Inferless Model API URL
    :param workspace_api_key: Inferless Workspace API Key
    :param data: Model Input Data as a dictionary, example: {"question": "What is the capital of France?", "context": "Paris is the capital of France."}
    :param callback: Callback function to be called after the response is received
    :param inputs: Model Input Data in inferless format
    :param is_batch: Whether the input is a batch of inputs, default is False
    :return: Response from the API call
    """
    thread = threading.Thread(target=call, args=(url, workspace_api_key, data, callback, inputs, is_batch))
    thread.start()
    return thread


def method(gpu: str = None):
    if gpu is None:
        raise Exception("Please provide the GPU name")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import sys
            sys_args = sys.argv
            entry_point = sys_args[0]
            if sys_args[1].endswith("yaml"):
                config_path = sys_args[1]
            else:
                raise Exception("Please provide the path to the configuration file in yaml format")

            if len(sys_args) == 3:
                ignore_file = sys_args[2]
            else:
                ignore_file = None

            data = {
                "func": func,
                "args": args,
                "kwargs": kwargs,
                "type": "method"
            }
            return call_rpc(data, entry_point, config_path, ignore_file, gpu)

        return wrapper

    return decorator


class Cls:
    def __init__(self, gpu: str = None):
        self.gpu = gpu
        if gpu is None:
            raise Exception("Please provide the GPU name")

    @staticmethod
    def load(func):
        """Decorator to mark the loader method."""
        func._is_loader = True
        return func

    def infer(self, func):
        """Decorator to mark the inference method."""
        func._is_infer = True
        import sys
        sys_args = sys.argv
        entry_point = sys_args[0]
        if sys_args[1].endswith("yaml"):
            config_path = sys_args[1]
        else:
            raise Exception("Please provide the path to the configuration file in yaml format")

        if len(sys_args) == 3:
            ignore_file = sys_args[2]
        else:
            ignore_file = None

        gpu = self.gpu

        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            # Check if the function is being called for the first time (before serialization)
            if not getattr(instance, '_is_deserialized', False):
                # Serialize the class instance and the call parameters
                data = {
                    "instance": instance,
                    "args": args,
                    "kwargs": kwargs,
                    "type": "class"
                }
                return call_rpc(data, entry_point, config_path, ignore_file, gpu)
            else:
                # If it's after deserialization, run the original function logic
                return func(instance, *args, **kwargs)

        return wrapper
