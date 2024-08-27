import os
from pathlib import Path
import re
import inspect

from tempfile import TemporaryDirectory
from contextlib import contextmanager

from abc import ABCMeta
from typing import Optional, Type, Set, Union
from pydantic import BaseModel

from finter import BasePortfolio, BaseAlpha
from finter.data import ContentFactory, ModelData
from finter.settings import logger
from finter.framework_model.submission.helper_submission import submit_model

import pandas as pd

from finter.framework_model.submission.config import (
    ModelTypeConfig,
    ModelUniverseConfig,
)


def _datestr(date_int: int):
    date_str = str(date_int)
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"


class ModelClassMeta(ABCMeta):
    def __new__(cls, name, bases, dct) -> Union[
        Type["BaseMetaAlpha"],
        Type["BaseMetaPortfolio"],
    ]:
        # workaround typing fix. (instead of Type["BaseMetaModel"])
        # BaseMetaModel can't represent BaseAlpha, BasePortfolio
        # because there is no base parent base model of BaseAlpha, BasePortfolio)

        return super().__new__(cls, name, bases, dct)


class BaseParameters(BaseModel):
    universe: ModelUniverseConfig


class BaseMetaModel(metaclass=ModelClassMeta):
    _param: Optional[BaseParameters] = None
    _model_type: ModelTypeConfig = (
        ModelTypeConfig.ALPHA
    )  # 기본 model type은 ALPHA. PORTFOLIO, FUND는 변경해서 사용해야 함

    class Parameters(BaseParameters): ...

    universe: ModelUniverseConfig = ModelUniverseConfig.KR_STOCK

    @staticmethod
    def cleanup_position(position: pd.DataFrame):
        df_cleaned = position.loc[:, ~((position == 0) | (position.isna())).all(axis=0)]
        df_cleaned = df_cleaned.fillna(0)
        return df_cleaned

    @classmethod
    def get_model_info(cls):
        if cls._model_type is None:
            raise ValueError(f"metamodel's model type is unknown")
        return cls.universe.get_config(cls._model_type)

    @classmethod
    def create(cls, params: BaseParameters):
        dct = params.dict()
        dct["_param"] = params

        model_cls_name = cls._model_type.class_name
        clz = ModelClassMeta(model_cls_name, (cls,), dct)
        return clz

    # @classmethod
    # def generate_model_submit_zip_file(cls, temporary=T) -> str:

    @classmethod
    def submit(
        cls,
        model_name: str,
        staging: bool = False,
        outdir: Optional[str] = None,
        **kwargs,
    ):
        """
        Submits the model to the Finter platform.

        :param docker_submit: Whether to submit the model using Docker.
        :param outdir: if not null, submitted code and json file are saved.
        :return: The result of the submission if successful, None otherwise.
        """

        @contextmanager
        def nullcontext():
            yield outdir

        context = TemporaryDirectory() if outdir is None else nullcontext()

        with context as odir:
            assert odir is not None

            source = cls.get_submit_code()

            modeldir = Path(odir) / model_name

            os.makedirs(modeldir, exist_ok=True)
            with open(
                modeldir / cls._model_type.file_name, "w", encoding="utf-8"
            ) as fd:
                fd.write(source)

            model_info = cls.get_model_info()

            if "insample" in kwargs:
                insample = kwargs.pop("insample")

                if not re.match(r"^\d+ days$", insample):
                    raise ValueError("insample should be like '100 days'")

                model_info["insample"] = insample

            if kwargs:
                logger.warn(f"Unused parameters: {kwargs}")

            res = submit_model(
                model_info, str(modeldir), docker_submit=False, staging=staging
            )

        return res

    @classmethod
    def get_source_code(cls):
        return inspect.getsource(cls.__bases__[0])

    @classmethod
    def get_submit_code(cls):
        meta_model = cls.__bases__[0]
        module_path = meta_model.__module__
        param = cls._param
        jsonstr = param.json()
        model_cls_name = cls._model_type.class_name

        return f"""
from {module_path} import {meta_model.__name__}

param_json = r'{jsonstr}'
params = {meta_model.__name__}.Parameters.parse_raw(param_json)
{model_cls_name} = {meta_model.__name__}.create(params)
"""


class BaseMetaAlpha(BaseAlpha, BaseMetaModel):
    _model_type: ModelTypeConfig = ModelTypeConfig.ALPHA


class BaseMetaPortfolio(BasePortfolio, BaseMetaModel):
    _model_type: ModelTypeConfig = ModelTypeConfig.PORTFOLIO

    alpha_set: Set[str] = set()

    class Parameters(BaseParameters):
        alpha_set: Set[str]

    class AlphaLoader:
        """to support legacy portfolio"""

        def __init__(self, start: int, end: int):
            self.start = _datestr(start)
            self.end = _datestr(end)

        def get_alpha(self, alpha):
            return ModelData.load("alpha." + alpha).loc[self.start : self.end]

    def alpha_loader(self, start: int, end: int):
        return BaseMetaPortfolio.AlphaLoader(start, end)
