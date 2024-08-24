from typing import assert_never

from uncountable.integration.executors.generic_upload_executor import GenericUploadJob
from uncountable.integration.executors.script_executor import resolve_script_executor
from uncountable.integration.job import Job
from uncountable.types import job_definition_t


def resolve_executor(
    job_executor: job_definition_t.JobExecutor,
    profile_metadata: job_definition_t.ProfileMetadata,
) -> Job:
    match job_executor:
        case job_definition_t.JobExecutorScript():
            return resolve_script_executor(
                job_executor, profile_metadata=profile_metadata
            )
        case job_definition_t.JobExecutorGenericUpload():
            return GenericUploadJob(
                remote_directories=job_executor.remote_directories,
                upload_strategy=job_executor.upload_strategy,
                data_source=job_executor.data_source,
            )
    assert_never(job_executor)
