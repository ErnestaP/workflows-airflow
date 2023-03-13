import airflow
import common.pull_ftp as pull_ftp
from airflow.decorators import dag, task
from iop.repository import IOPRepository
from iop.sftp_service import IOPSFTPService
from structlog import get_logger


@dag(
    start_date=airflow.utils.dates.days_ago(0),
    params={
        "excluded_directories": [],
        "force_pull": False,
        "filenames_pull": {"enabled": False, "filenames": [], "force_from_ftp": False},
    },
)
def iop_pull_ftp():
    logger = get_logger().bind(class_name="iop_pull_ftp")

    @task()
    def migrate_from_ftp(repo=IOPRepository(), sftp=IOPSFTPService(), **kwargs):
        params = kwargs["params"]
        specific_files = (
            "filenames_pull" in params
            and params["filenames_pull"]["enabled"]
            and not params["filenames_pull"]["force_from_ftp"]
        )
        if specific_files:
            specific_files_names = pull_ftp.reprocess_files(repo, logger, **kwargs)
            return specific_files_names

        with sftp:
            return pull_ftp.migrate_from_ftp(sftp, repo, logger, **kwargs)

    @task()
    def trigger_file_processing(filenames=None):
        return pull_ftp.trigger_file_processing(
            publisher="iop",
            repo=IOPRepository(),
            logger=logger,
            filenames=filenames or [],
        )

    filenames = migrate_from_ftp()
    trigger_file_processing(filenames=filenames)


dag_taskflow = iop_pull_ftp()
