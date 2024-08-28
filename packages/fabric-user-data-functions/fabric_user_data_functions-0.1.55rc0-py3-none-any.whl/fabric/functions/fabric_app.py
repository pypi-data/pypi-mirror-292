# flake8: noqa: I005
from typing import Any, Callable, Dict, List, Optional, Union, \
    Iterable
from azure.functions.decorators.http import HttpTrigger, HttpOutput, \
    HttpMethod
from azure.functions.decorators.core import DataType, \
    AuthLevel, InputBinding
from azure.functions.decorators.utils import parse_singular_param_to_enum, \
    parse_iterable_param_to_enums
from azure.functions import FunctionApp, HttpResponse
from azure.functions.decorators.core import DataType
from pydoc import locate
from .middleware import RemoveReqExtension, InvocationIdMidleware
import json
import azure
import inspect

from .udf_binding import UdfPropertyInput, UdfResponse
from .fabric_class import FabricSqlConnection, FabricLakeHouseFilesClient, FabricLakehouseClient, UserDataFunctionContext
from .item_binding import FabricItemInput, ItemType
from .user_data_function_context_binding import UserDataFunctionContextInput
from functools import wraps
from typing import Callable, TypeVar
T = TypeVar('T')

class FabricApp(FunctionApp):

    def __init__(self):
        super().__init__(AuthLevel.ANONYMOUS)

    def function(self, name=None):
        @self._configure_function_builder_with_func
        def wrap(fb, user_func):
            # Add HTTP Trigger
            fb.add_trigger(trigger=HttpTrigger(
                        name='req',
                        methods=[HttpMethod.POST],
                        auth_level=AuthLevel.ANONYMOUS,
                        route=name))
            fb.add_binding(binding=HttpOutput(name='$return'))

            # Add Custom UDF Bindings
            sig = inspect.signature(user_func)
            for param in sig.parameters.values():
                if self._is_typeof_fabricitem_input(param.annotation):
                    continue
                if(param.name == 'req'):
                    continue
                if self._is_typeof_userdatafunctioncontext_input(param.annotation):
                    # fb.add_binding(binding=UserDataFunctionContext())
                    continue

                # Add custom bindings
                fb.add_binding(binding=UdfPropertyInput(
                    name=param.name, parameterName=param.name, typeName=self._get_cleaned_type(param).__name__)
                )

            return fb
        return wrap

    def _is_typeof_fabricitem_input(self, obj):
        # Check to see if parameter is anything we might return from a fabric binding
        return obj == FabricSqlConnection or obj == FabricLakeHouseFilesClient or obj == FabricLakehouseClient
    
    def _is_typeof_userdatafunctioncontext_input(self, obj):
        # Check to see if parameter is anything we might return from a fabric binding
        return obj == UserDataFunctionContext

    # If this is a data type with a nested type (e.g., list[int], dict[str, int]), we return the outermost type, e.g., list, dict
    # Otherwise, Azure Functions will say something like:
    #   Exception: FunctionLoadError: cannot load the hello_fabric2 function: binding intStrDict has invalid non-type annotation dict[int, str]
    def _get_cleaned_type(self, param):
        if(hasattr(param.annotation,'__origin__')): 
            return param.annotation.__origin__
        else:
            return param.annotation

    def _ensure_http_returntype(self, func: Callable[..., T]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            if type(resp) is HttpResponse or issubclass(type(resp), HttpResponse):
                return resp
            
            return HttpResponse(str(resp))
        return wrapper

    def _configure_function_builder_with_func(self, wrap) -> Callable[..., Any]:   
        def decorator(func):
            sig = inspect.signature(func)

            # Update function parameters to include a request object for validation
            params = []
            params.append(inspect.Parameter('req', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=azure.functions.HttpRequest))

            for param in sig.parameters.values():
                if param.name != 'req':
                    params.append(inspect.Parameter(param.name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=self._get_cleaned_type(param)))

            sig = sig.replace(parameters=tuple(params)).replace(return_annotation=str)
            func.__signature__ = sig

            annotations = {}
            # Update annotations to ensure it uses the cleaned type
            for param in params:
                annotations[param.name] = param.annotation

            # Update return annotation of func to be HttpResponse
            annotations['old_return'] = func.__annotations__['return']
            annotations['return'] = HttpResponse

            func.__annotations__ = annotations

            # Add wrapper for function to handle ensure all return values are parsed to HttpResponse
            user_func = self._ensure_http_returntype(func)

            fb = self._validate_type(user_func)
            self._function_builders.append(fb)

            return wrap(fb, user_func)

        return decorator
    # The decorator that will be used to tell the function we want a fabric item
    def fabric_item_input(self,
                        argName,
                        alias: str,
                        item_type: Optional[ItemType] = ItemType.SQL,
                        default_item_name: Optional[str] = None,
                        default_workspace_name: Optional[str] = None,
                        data_type : Optional[DataType] = DataType.STRING,
                        **kwargs) \
            -> Callable[..., Any]:

        @self._configure_function_builder
        def wrap(fb):
                
            fb.add_binding(
                binding=FabricItemInput(
                    name=argName,
                    alias=alias,
                    itemType=item_type,
                    defaultItemName=default_item_name,
                    defaultWorkspaceName=default_workspace_name,
                    data_type=parse_singular_param_to_enum(data_type,
                                                        DataType),
                    **kwargs))
            return fb
        
        return wrap
    
    def user_data_function_context_input(self,
                        argName,
                        **kwargs) \
            -> Callable[..., Any]:

        @self._configure_function_builder
        def wrap(fb):
            fb.add_binding(
                binding=UserDataFunctionContextInput(
                    name=argName,
                    **kwargs))
            return fb
        
        return wrap