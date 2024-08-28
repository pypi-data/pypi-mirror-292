import os
import requests
import json

PANTOMATH_SDK_POST_JOB_LOGS_PAGE_SIZE = (
    os.environ["PANTOMATH_SDK_POST_JOB_LOGS_PAGE_SIZE"]
    if "PANTOMATH_SDK_POST_JOB_LOGS_PAGE_SIZE" in os.environ
    else "500"
)
PANTOMATH_API_BASE_URL = (
    os.environ["PANTOMATH_API_BASE_URL"]
    if "PANTOMATH_API_BASE_URL" in os.environ
    else "https://api.dev-pantomath.org/v1"
)
PANTOMATH_API_KEY = (
    os.environ["PANTOMATH_API_KEY"] if "PANTOMATH_API_KEY" in os.environ else ""
)


class PantomathApiClient:
    """This class is used to send the logs to Pantomath API.
    :param api_base_url: Pantomath's api base URL,
    which defaults to os.environ["PANTOMATH_API_BASE_URL"]
    :type api_base_url: str, optional
    :param api_key: Pantomath's provided API key,
    which defaults to os.environ["PANTOMATH_API_KEY"]
    :type api_key: str, optional
    :param job_logs_request_page_size: number of logs
    which can be sent in a since request, defaults to 500
    :type job_logs_request_page_size: str, optional
    """

    def __init__(
        self,
        api_base_url=PANTOMATH_API_BASE_URL,
        api_key=PANTOMATH_API_KEY,
        job_logs_request_page_size=PANTOMATH_SDK_POST_JOB_LOGS_PAGE_SIZE,
    ):
        """Constructor method"""
        self._api_base_url = api_base_url
        self._api_key = api_key
        self._job_logs_request_page_size = job_logs_request_page_size

    def post_job_run_logs(self, jobRunLogs):
        """Method used to validate the run logs,
        separate the run logs into chunks, and sending each chunk to Pantomath
        :param jobRunLogs: list of run logs
        :type jobRunLogs: list of JobRun
        """

        if isinstance(jobRunLogs, list):
            job_run_logs = jobRunLogs
            for log in job_run_logs:
                if not self.validate_log_data(log):
                    raise TypeError("Validation of the requested job runs logs failed.")
            chunk_size = (
                int(self._job_logs_request_page_size)
                if int(self._job_logs_request_page_size) < len(job_run_logs)
                else len(job_run_logs)
            )
            while job_run_logs:
                chunk, job_run_logs = (
                    job_run_logs[:chunk_size],
                    job_run_logs[chunk_size:],
                )
                self._send_logs(chunk)

    def _send_logs(self, logs):
        """Method send run logs to Pantomath
        :param logs: list of run logs
        :type logs: list of JobRun
        ...
        :return: The response of the API
        :rtype: Response. None
        """

        if logs:
            url = self._api_base_url + "/job-run-logs"
            headers = {
                "x-api-key": self._api_key,
                "x-sdk-type": "Python",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            data = json.dumps({"jobRunLogs": logs})
            return requests.post(url, headers=headers, data=data)
        return None

    def _validate_dataset(self, dataset):
        """Method used to validate the datasets
        :param dataset: dataset to be checked.
        :type dataset: Job, Dataset
        ...
        :return: If the inputed dataset is valid or not valid for sending to the Pantomath API
        :rtype: Boolean
        """
        return (
            isinstance(dataset["objectName"], str)
            and isinstance(dataset["objectType"], str)
            and isinstance(dataset["fullyQualifiedObjectName"], str)
        )

    def validate_log_data(self, log):
        """Method used to validate the run logs
        :param log: single log to validate
        :type log: JobRun
        ...
        :return: If the inputed log is valid or not valid for sending to the Pantomath API
        :rtype: Boolean
        """
        if not log:
            return False
        try:
            valid_required_args = (
                isinstance(log["jobRunId"], str)
                and isinstance(log["objectName"], str)
                and isinstance(log["objectType"], str)
                and isinstance(log["fullyQualifiedObjectName"], str)
                and isinstance(log["status"], str)
                and isinstance(log["message"], str)
                and isinstance(log["isoTimestamp"], str)
            )
            valid_optional_args = (
                ("recordsEffected" in log and isinstance(log["recordsEffected"], int))
                or not ("recordsEffected" in log)
                or log["recordsEffected"] is None
            )
            valid_source_dataset = "sourceDataSets" in log
            if valid_source_dataset:
                for sdataset in log["sourceDataSets"]:
                    valid_source_dataset = (
                        valid_source_dataset and self._validate_dataset(sdataset)
                    )
            else:
                valid_source_dataset = True
            valid_target_dataset = "targetDataSets" in log
            if valid_target_dataset:
                for tdataset in log["targetDataSets"]:
                    valid_target_dataset = (
                        valid_target_dataset and self._validate_dataset(tdataset)
                    )
            else:
                valid_target_dataset = True
            return (
                valid_required_args
                and valid_optional_args
                and valid_source_dataset
                and valid_target_dataset
            )
        except Exception:
            return False
