import inspect
import json
from functools import wraps
from http import HTTPStatus
from typing import Type

from django.http import JsonResponse
from pydantic import ValidationError

from .utils import MaybeModel, get_maybe_model


class NoData:
    """An empty class to signal that there is no data from which to build models"""


def pactio(fn):

    signature = inspect.signature(fn)

    model_map: dict[str, MaybeModel] = {
        arg: maybe_model
        for arg, maybe_model in [(a, get_maybe_model(parameter)) for a, parameter in signature.parameters.items()]
        if maybe_model
    }

    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        content_type = request.headers.get("content-type", "")
        data: dict | Type[NoData]

        try:
            data = {
                "application/json": lambda: json.loads(request.body),
                # "application/x-www-form-urlencoded": lambda: request.form,  # TODO: django-ify
            }[content_type]()
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "bad request"},
                status=HTTPStatus.BAD_REQUEST,
            )
        except KeyError:
            data = NoData

        if data is NoData:
            return fn(request, *args, **kwargs)

        for arg, maybe_model in model_map.items():
            cls, optional = maybe_model.cls, maybe_model.optional
            if optional and data is None:
                kwargs[arg] = None
            else:
                try:
                    kwargs[arg] = cls.model_validate(data)
                except ValidationError:
                    return JsonResponse(
                        {"message": "bad request"},
                        status=HTTPStatus.BAD_REQUEST,
                    )

        return fn(request, *args, **kwargs)

    return wrapper
