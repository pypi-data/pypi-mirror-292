Pantomath SDK
=============

Installation and Setup
----------------------

1. Install the Pantomath SDK for Python:
    ```shell
    $ pip install pantomath-sdk
    ```

    This is the preferred method to install the Pantomath SDK, as it will always
    install the most recent stable release.

    If you don't have [pip](https://pip.pypa.io) installed, this [Python installation guide](https://docs.python-guide.org/starting/installation/) can guide you through the process.

1. Add configuration ENVs to your runtime:
   ```shell
   PANTOMATH_API_BASE_URL = ******,
   PANTOMATH_API_KEY = ******
   ```


Example
-------

```python
from pantomath_sdk import PantomathSDK, AstroTask, S3Bucket, SnowflakePipe
from time import sleep

def main():
    # Create an instance of the PantomathSDK
    pantomath_sdk = PantomathSDK(api_key="****")

    # Construct your job
    astro_task = AstroTask(
        name="astro_task_1",
        dag_name="astro_dag_1",
        host_name="astro_host_1"
    )

    # Construct your source and target data sets
    source_data_sets = [
        S3Bucket(s3_bucket="s3://some-bucket-1/file.csv")
    ]

    target_data_sets = [
        SnowflakePipe(
            name="snowpipe_1",
            schema="snowflake_schema_1",
            database="snowflake_database_1",
            port=443,
            host="snowflake_host_1.example.com",
        )
    ]

    # Capture your job run
    job_run = pantomath_sdk.new_job_run(
        job=astro_task,
        source_data_sets=source_data_sets,
        target_data_sets=target_data_sets,
    )
    try:
        job_run.log_start(message="Starting Astro task")
        for i in range(5):
            job_run.log_progress(
                message=f"Completed step {i + 1}",
                records_effected=i * 100
            )
            sleep(2)
    except Exception as e:
        job_run.log_failure(message=e.message)
    finally:
        job_run.log_success(message="Succeeded!")

if __name__ == '__main__':
    main()
```

Limitations
-----------
The SDK will not publish logs to Pantomath until the Job Run has received a success or failure message via a call to `log_success()` or `log_failure()`.  Therefore, the SDK is unable to trigger any latency incident events within Pantomath.
