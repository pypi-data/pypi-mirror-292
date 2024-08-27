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
import logging
import pprint
import time
from typing import Optional

from airflow_tecton.hooks.tecton_hook import TectonHook


def wait_until_completion(hook: TectonHook,
                          workspace: str,
                          feature_view: str,
                          job_id: str):
    """
    Wait for materialization job to finish successfully.
    If the job fails, throw an exception.
    """
    job_result = hook.get_materialization_job(
        workspace, feature_view, job_id
    )["job"]
    while job_result.get("state", "").upper().endswith("RUNNING"):
        if len(job_result.get("attempts", [])) > 0:
            attempts = job_result["attempts"]
            latest_attempt = attempts[-1]
            logging.info(
                f"Latest attempt #{len(attempts)} in state {latest_attempt['state']} with URL {latest_attempt['run_url']}"
            )
        else:
            logging.info(f"No attempt launched yet")
        time.sleep(60)
        job_result = hook.get_materialization_job(
            workspace, feature_view, job_id
        )["job"]
    if job_result["state"].upper().endswith("SUCCESS"):
        return
    else:
        raise Exception(
            f"Final job state was {job_result['state']}. Final response:\n {job_result}"
        )


def kill_job(hook: TectonHook,
             workspace: str,
             feature_view: str,
             job_id: Optional[str]):
    """
    kill job with job_id when job_id is available.
    """
    if job_id:
        logging.info(f"Attempting to kill job {job_id}")
        hook.cancel_materialization_job(
            workspace, feature_view, job_id
        )
        logging.info(f"Successfully killed job {job_id}")
    else:
        logging.debug(f"No job started; none to kill")
