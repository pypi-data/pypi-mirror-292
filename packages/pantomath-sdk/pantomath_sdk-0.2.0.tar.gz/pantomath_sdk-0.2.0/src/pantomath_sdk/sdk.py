from pantomath_sdk.model.job_run.job_run import JobRun
from pantomath_sdk.client.pantomath_api_client import PantomathApiClient


class PantomathSDK:
    """PantomathSDK's PantomathSDK Class used for creating new job runs
    :param api_base_url: Pantomath's api base URL,black
    which defaults to os.environ["PANTOMATH_API_BASE_URL"]
    :type api_base_url: str, optional
    :param api_key: Pantomath's provided API key,
    which defaults to os.environ["PANTOMATH_API_KEY"]
    :type api_key: str, optional
    ...
    """

    def __init__(self, api_base_url, api_key):
        """Constructor method"""
        self._api_base_url = api_base_url
        self._api_key = api_key

    def new_job_run(
        self,
        job,
        name=None,
        next_run_at=None,
        source_data_sets=None,
        target_data_sets=None,
    ):
        """Creates a new Job Run to store all events to be sent to Pantomath
        :param job: Job Run to be tracked
        :type job: Job,
        :param name: Name of the Job Run
        :type name: str, optional
        :param next_run_at: The type of trigger for when the job will run again
        :type next_run_at: JobDidNotRunAtMethods, optional
        :param source_data_sets: Source Dataset for the job
        :type source_data_sets: Dataset, optional
        :param target_data_sets: Target Dataset for the job
        :type target_data_sets: Dataset, optional
        ...
        :return: The JobRun to be tracked
        :rtype: JobRun
        """
        client = PantomathApiClient(
            api_base_url=self._api_base_url,
            api_key=self._api_key,
        )
        job_run = JobRun(
            job=job,
            name=name,
            next_run_at=next_run_at,
            source_data_sets=source_data_sets,
            target_data_sets=target_data_sets,
            pantomath_api_client=client,
        )
        return job_run
