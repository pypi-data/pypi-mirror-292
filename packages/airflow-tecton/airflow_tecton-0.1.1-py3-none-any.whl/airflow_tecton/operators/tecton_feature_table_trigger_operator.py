# Copyright 2022 Tecton, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime
import logging
import pandas
from typing import Any, Callable, Collection, List, Mapping, Sequence, Union

from airflow.models import BaseOperator

from airflow_tecton.hooks.tecton_hook import TectonHook
from airflow_tecton.operators.df_utils import ingest_feature_table_with_pandas_df


class TectonFeatureTableTriggerOperator(BaseOperator):
    """
    An Airflow operator that kicks off a Tecton Feature Table ingestion job,
    and does not wait for its completion.

    Note that this will use Tecton managed retries.

    Use this if you have unpredictably arriving data but want Tecton
    to manage retries of jobs.
    """

    template_fields: Sequence[str] = ("templates_dict", "op_args", "op_kwargs")
    template_fields_renderers = {"templates_dict": "json", "op_args": "py", "op_kwargs": "py"}

    def __init__(
        self,
        *,
        conn_id: str = "tecton_default",
        workspace: str,
        feature_view: str,
        online: bool,
        offline: bool,
        df_generator: Callable[..., pandas.DataFrame] = None,
        op_args: Union[Collection[Any], None] = None,
        op_kwargs: Union[Mapping[str, Any], None] = None,
        templates_dict: Union[dict, None] = None,
        templates_exts: Union[list[str], None] = None,
        **kwargs,
    ):
        """

        :param conn_id: Airflow connection ID for Tecton connection
        :param workspace: Workspace of FeatureView
        :param feature_view: FeatureView name
        :param online: Whether job writes to online store
        :param offline: Whether job writes to offline store
        :param df_generator: A reference to an object that is callable and returns pandas.DataFrame
        :param op_args: a list of positional arguments that will get unpacked when
            calling df_generator
        :param op_kwargs: a dictionary of keyword arguments that will get unpacked
            in df_generator
        :param templates_dict: a dictionary where the values are templates that
            will get templated by the Airflow engine sometime between
            ``__init__`` and ``execute`` takes place and are made available
            in df generator's context after the template has been applied. (templated)
        :param templates_exts: a list of file extensions to resolve while
            processing templated fields, for examples ``['.sql', '.hql']``
        :param kwargs: Airflow base kwargs passed to BaseOperator
        """
        super().__init__(**kwargs)
        self.workspace = workspace
        self.feature_view = feature_view
        self.online = online
        self.offline = offline
        self.conn_id = conn_id
        if df_generator and not callable(df_generator):
            raise Exception("`df_generator` param must be callable")
        self.df_generator = df_generator
        self.op_args = op_args or ()
        self.op_kwargs = op_kwargs or {}
        self.templates_dict = templates_dict
        if templates_exts:
            self.template_ext = templates_exts

    def execute(self, context) -> List[str]:
        hook = TectonHook.create(self.conn_id)

        resp = ingest_feature_table_with_pandas_df(hook, self.workspace, self.feature_view, context,
                                                   self.df_generator, self.op_args, self.op_kwargs,
                                                   self.templates_dict, True)

        new_job_id = resp["job"]["id"]
        logging.info(f"Launched job with id {new_job_id}")
        return [new_job_id]
