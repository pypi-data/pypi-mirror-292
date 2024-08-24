# flake8: noqa: I005
from typing import Any, Callable, Dict, List, Optional, Union, \
    Iterable
from azure.functions.decorators.core import  DataType
from azure.functions.decorators.core import DataType, InputBinding
import azure
from pydoc import locate
from collections import namedtuple
import json
from enum import IntEnum 
from azure.functions import HttpResponse
from .fabric_class import UserDataFunctionContext

class UserDataFunctionContextInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return 'UserDataFunctionContext'
    
    def __init__(self,
                name: str,
                **kwargs):
        super().__init__(name)


# The input converter that automatically gets registered in the function app.
class UserDataFunctionContextConverter(azure.functions.meta.InConverter, binding='UserDataFunctionContext'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return pytype == UserDataFunctionContext

    @classmethod
    def decode(cls, data, *,
               trigger_metadata) -> Any:
        
        if data is not None and data.type == 'string' and data.value is not None: 
            body = json.loads(data.value) 
        else:
            raise NotImplementedError(
                f'unable to load data successfully for user Data Function Context')
         
        body = json.loads(data.value) 

        return cls.parseType(body)
    
    @classmethod
    def parseType(self, body: json):

        return UserDataFunctionContext(
                invocationId=body['InvocationId'],
                executingUser=body['ExecutingUser'])    
