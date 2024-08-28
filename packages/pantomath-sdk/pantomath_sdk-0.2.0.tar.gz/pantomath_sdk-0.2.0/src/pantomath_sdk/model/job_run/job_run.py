from pantomath_sdk.enums.job_run_log_status import JobRunLogStatuses
from pantomath_sdk.model.job_run.job_run_log import JobRunLog
from pantomath_sdk.model.job.job import Job
import datetime
import uuid


class JobRun(Job):
    """JobRun's Job Class used for getting the required information for Pantomath
    :param pantomath_api_client: The Pantomath API Client Object
    :type pantomath_api_client: PantomathApiClient
    :param job: Job which will be tracked
    :type job: Job
    :param name: Name of the Job Run
    :type name: str
    :param next_run_at: The type of trigger for when the job will run again
    :type next_run_at: JobDidNotRunAtMethods
    :param source_data_sets: Source Dataset for the job
    :type source_data_sets: Dataset
    :param target_data_sets: Target Dataset for the job
    :type target_data_sets: Dataset
    ...
    """

    def __init__(
        self,
        pantomath_api_client,
        job,
        name=None,
        next_run_at=None,
        source_data_sets=None,
        target_data_sets=None,
    ):
        """Constructor method"""
        self._job = job
        self._id = uuid.uuid4()
        self._name = name
        self._source_data_sets = (
            source_data_sets if source_data_sets is not None else []
        )
        self._target_data_sets = (
            target_data_sets if target_data_sets is not None else []
        )
        self._next_run_at = next_run_at
        self._pantomath_api_client = pantomath_api_client
        self._log_buffer = []
        self._pushing_logs = False
        self._reported_start = False
        self._reported_success = False
        self._reported_failure = False

    @staticmethod
    def create(
        pantomath_api_client, job, name, next_run_at, source_data_sets, target_data_sets
    ):
        """Static method for obtaining JobRun's DataSet Class
        used for getting the required infomation for Pantomath
        :param pantomath_api_client: The Pantomath API Client Object
        :type pantomath_api_client: PantomathApiClient
        :param job: Job which will be tracked
        :type job: Job
        :param name: Name of the Job Run
        :type name: str
        :param next_run_at: The type of trigger for when the job will run again
        :type next_run_at: JobDidNotRunAtMethods
        :param source_data_sets: Source Dataset for the job
        :type source_data_sets: Dataset
        :param target_data_sets: Target Dataset for the job
        :type target_data_sets: Dataset
        ...
        :return: JobRun class object
        :rtype: JobRun
        """
        return JobRun(
            pantomath_api_client,
            job,
            name,
            next_run_at,
            source_data_sets,
            target_data_sets,
        )

    def _get_normalized_message(self, message):
        """Processed the message to be into a normalized format for Pantomath
        :param message: message for the run
        :type message: str
        ...
        :return: Processed message
        :rtype: str
        """
        lengthCappedMessage = message[:1000]
        jobRunNamePrefix = (self._name + " running in ") if self._name else ""
        jobName = self._job.get_name()
        rtnMsg = jobRunNamePrefix + jobName + ": " + lengthCappedMessage
        return rtnMsg

    def get_job(self):
        """Returns the Job
        ...
        :return: Returns the Job
        :rtype: Job
        """
        return self._job

    def get_job_run_id(self):
        """Returns the Job run id
        ...
        :return: Returns the Job run id
        :rtype: str
        """
        return self._id

    def get_source_data_sets(self):
        """Returns source datasets
        ...
        :return: Returns source datasets
        :rtype: Dataset
        """
        source_array = []
        for dataset in self._source_data_sets:
            source_array.append(
                {
                    "objectName": dataset.get_name(),
                    "objectType": dataset.get_type(),
                    "fullyQualifiedObjectName": dataset.get_fully_qualified_object_name(),
                }
            )
        return source_array

    def get_target_data_sets(self):
        """Returns target datasets
        ...
        :return: Returns target datasets
        :rtype: Dataset
        """
        target_array = []
        for dataset in self._target_data_sets:
            target_array.append(
                {
                    "objectName": dataset.get_name(),
                    "objectType": dataset.get_type(),
                    "fullyQualifiedObjectName": dataset.get_fully_qualified_object_name(),
                }
            )
        return target_array

    def get_next_run_at(self):
        """Returns Next Run At Type
        ...
        :return: Returns Next Run At Type
        :rtype: JobDidNotRunAtMethods
        """
        return self._next_run_at

    def log_start(self, message="Started", records_effected=None):
        """Create Log for the Job start event
        :param message: Message to attach to the log
        :type message: str
        :param records_effected: Number of record effected by the job, defaults to none
        :type records_effected: Number, None
        ...
        """
        if self._reported_start:
            raise Exception(
                "report_Start can only be called once per JobRun instance. Job Run "
                + self._job["name"]
            )
        self._reported_start = True
        job_run_log = JobRunLog(
            job_run=self,
            status=JobRunLogStatuses.STARTED.value,
            message=self._get_normalized_message(message),
            records_effected=records_effected,
            timestamp=datetime.datetime.utcnow(),
        )
        self._convert_to_api_log(job_run_log)
        self.log_progress(message="Start In Progress Log")
        self._push_and_clear_log_buffer()

    def log_progress(self, message="Progressing", records_effected=None):
        """Create Log for the Job Progressing event
        :param message: Message to attach to the log
        :type message: str
        :param records_effected: Number of record effected by the job, defaults to None
        :type records_effected: Number, None
        ...
        """
        job_run_log = JobRunLog(
            job_run=self,
            status=JobRunLogStatuses.IN_PROGRESS.value,
            message=self._get_normalized_message(message),
            records_effected=records_effected,
            timestamp=datetime.datetime.utcnow(),
        )
        self._convert_to_api_log(job_run_log)

    def log_warning(self, message="Warning", records_effected=None):
        """Create Log for the Job Warning event
        :param message: Message to attach to the log
        :type message: str
        :param records_effected: Number of record effected by the job, defaults to none
        :type records_effected: Number, None
        ...
        """
        job_run_log = JobRunLog(
            job_run=self,
            status=JobRunLogStatuses.WARNING.value,
            message=self._get_normalized_message(message),
            records_effected=records_effected,
            timestamp=datetime.datetime.utcnow(),
        )
        self._convert_to_api_log(job_run_log)

    def log_success(self, message="Succeeded", records_effected=None):
        """Create Log for the Job Succeeded event
        :param message: Message to attach to the log
        :type message: str
        :param records_effected: Number of record effected by the job, defaults to none
        :type records_effected: Number, None
        ...
        """
        if self._reported_success:
            raise Exception(
                "reportSuccess can only be called once per JobRun instance. Job Run: "
                + self._job["name"]
            )
        if self._reported_failure:
            raise Exception(
                "reportSuccess cannot be called because reportFailure has already been"
                "called. Job Run: " + self._job["name"]
            )
        self._reported_success = True
        job_run_log = JobRunLog(
            job_run=self,
            status=JobRunLogStatuses.SUCCEEDED.value,
            message=self._get_normalized_message(message),
            records_effected=records_effected,
            timestamp=datetime.datetime.utcnow(),
        )
        self._convert_to_api_log(job_run_log)
        self._push_and_clear_log_buffer()

    def log_failure(self, message="Failed", records_effected=None):
        """Create Log for the Job Failed event
        :param message: Message to attach to the log
        :type message: str
        :param records_effected: Number of record effected by the job, defaults to none
        :type records_effected: Number, None
        ...
        """
        if self._reported_success:
            raise Exception(
                "reportFailure can only be called once per JobRun instance. Job Run: "
                + self._job["name"]
            )
        if self._reported_failure:
            raise Exception(
                "reportFailure cannot be called because reportSuccess has already been"
                "called. Job Run: " + self._job["name"]
            )
        self._reported_success = True
        job_run_log = JobRunLog(
            job_run=self,
            status=JobRunLogStatuses.FAILED.value,
            message=self._get_normalized_message(message),
            records_effected=records_effected,
            timestamp=datetime.datetime.utcnow(),
        )
        self._convert_to_api_log(job_run_log)
        self._push_and_clear_log_buffer()

    def _convert_to_api_log(self, job_run_log):
        """Convert the Job Run Log into an API ready Object and adds to the buffer
        :param job_run_log: Message to attach to the log
        :type job_run_log: JobRunLog
        ...
        """
        api_log = {
            "uniqueId": str(uuid.uuid4()),
            "jobRunId": str(self.get_job_run_id()),
            "objectName": str(self._job.get_name()),
            "objectType": str(self._job.get_type()),
            "fullyQualifiedObjectName": str(
                self._job.get_fully_qualified_object_name()
            ),
            "status": job_run_log.get_status(),
            "message": str(job_run_log.get_message()),
            "targetDataSets": self.get_target_data_sets(),
            "sourceDataSets": self.get_source_data_sets(),
            "isoTimestamp": str(job_run_log.get_timestamp()),
        }
        if job_run_log.get_records_effected():
            api_log["recordsEffected"] = int(job_run_log.get_records_effected())
        self._log_buffer.append(api_log)

    def _push_and_clear_log_buffer(self):
        """Sends the buffer to the Pantomath API
        ...
        """
        if not self._pushing_logs and len(self._log_buffer) > 0:
            self._pushing_logs = True
            try:
                self._pantomath_api_client.post_job_run_logs(
                    jobRunLogs=self._log_buffer
                )
            except Exception as e:
                print(e)
            finally:
                self._pushing_logs = False
            self._log_buffer = []
