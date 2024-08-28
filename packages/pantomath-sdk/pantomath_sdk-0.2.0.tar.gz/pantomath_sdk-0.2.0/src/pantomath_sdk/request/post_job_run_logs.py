class PostJobRunLog:
    """PostJobRunLog's PostJobRunLog Class used for validating Logs before sending to Pantomath
    :param job_run_id: ID of the Job Run
    :type job_run_id: PantomathApiClient
    :param object_name: Name of the Job Run Log
    :type object_name: str
    :param object_type: Status of the Job Run Log
    :type object_type: JobRunLogStatuses
    :param fully_qualified_object_name: Fully Qualified Name for the Job Run
    :type fully_qualified_object_name: str
    :param source_data_sets: Source Dataset for the job
    :type source_data_sets: Dataset
    :param target_data_sets: Target Dataset for the job
    :type target_data_sets: Dataset
    :param iso_timestamp: Timestamp of the log
    :type iso_timestamp: Datetime
    ...
    """

    def __init__(
        self,
        job_run_id,
        object_name,
        object_type,
        fully_qualified_object_name,
        status,
        message,
        records_effected,
        source_data_sets,
        target_data_sets,
        iso_timestamp,
    ):
        """Constructor method"""
        self.job_run_id = job_run_id
        self.object_name = object_name
        self.object_type = object_type
        self.fully_qualified_object_name = fully_qualified_object_name
        self.status = status
        self.message = message
        self.records_effected = records_effected
        self.source_data_sets = source_data_sets
        self.target_data_sets = target_data_sets
        self.iso_timestamp = iso_timestamp
        if not self.validate_data():
            raise TypeError("Validation of the requestion job runs logs failed.")

    @staticmethod
    def create(
        job_run_id,
        object_name,
        object_type,
        fully_qualified_object_name,
        status,
        message,
        records_effected,
        source_data_sets,
        target_data_sets,
        iso_timestamp,
    ):
        """Static method for obtaining JobRun's DataSet Class
        used for getting the required infomation for Pantomath
        :param job_run_id: ID of the Job Run
        :type job_run_id: PantomathApiClient
        :param object_name: Name of the Job Run Log
        :type object_name: str
        :param object_type: Status of the Job Run Log
        :type object_type: JobRunLogStatuses
        :param fully_qualified_object_name: Fully Qualified Name for the Job Run
        :type fully_qualified_object_name: str
        :param source_data_sets: Source Dataset for the job
        :type source_data_sets: Dataset
        :param target_data_sets: Target Dataset for the job
        :type target_data_sets: Dataset
        :param iso_timestamp: Timestamp of the log
        :type iso_timestamp: Datetime
        ...
        :return: PostJobRunLog class object
        :rtype: PostJobRunLog
        """
        return PostJobRunLog(
            job_run_id,
            object_name,
            object_type,
            fully_qualified_object_name,
            status,
            message,
            records_effected,
            source_data_sets,
            target_data_sets,
            iso_timestamp,
        )

    def _validate_dataset(self, dataset):
        """Validates the dataset
        :param dataset: Dataset to be validated
        :type dataset: Dataset
        ...
        :return: Return if the dataset is valid
        :rtype: Boolean
        """
        return (
            "object_name" in dataset
            and isinstance(dataset["object_name"], str)
            and "object_type" in dataset
            and isinstance(dataset["object_type"], str)
            and "fully_qualified_object_name" in dataset
            and isinstance(dataset["fully_qualified_object_name"], str)
        )

    def validate_data(self):
        """Validates the PostJobRunLog
        ...
        :return: Return if the PostJobRunLog is valid
        :rtype: Boolean
        """
        valid_required_args = (
            isinstance(self.job_run_id, str)
            and isinstance(self.object_name, str)
            and isinstance(self.object_type, str)
            and isinstance(self.fully_qualified_object_name, str)
            and isinstance(self.status, str)
            and isinstance(self.message, str)
            and isinstance(self.iso_timestamp, str)
        )
        valid_optional_args = isinstance(self.records_effected, int) or isinstance(
            self.records_effected, None
        )
        valid_source_dataset = True
        if self.source_data_sets:
            for sdataset in self.source_data_sets:
                valid_source_dataset = valid_source_dataset and self._validate_dataset(
                    sdataset
                )
        valid_target_dataset = True
        if self.target_data_sets:
            for tdataset in self.target_data_sets:
                valid_target_dataset = valid_target_dataset and self._validate_dataset(
                    tdataset
                )
        return (
            valid_required_args
            and valid_optional_args
            and valid_source_dataset
            and valid_target_dataset
        )
