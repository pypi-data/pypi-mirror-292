import sys
from time import sleep
from primitive.utils.actions import BaseAction
from loguru import logger
from primitive.__about__ import __version__


class Agent(BaseAction):
    def execute(
        self,
    ):
        logger.enable("primitive")
        logger.info(" [*] primitive")
        logger.info(f" [*] Version: {__version__}")

        # self.primitive.hardware.update_hardware_system_info()
        try:
            self.primitive.hardware.check_in_http(is_available=True, is_online=True)
        except Exception as ex:
            logger.error(f"Error checking in hardware: {ex}")
            sys.exit(1)

        try:
            while True:
                hardware = self.primitive.hardware.get_own_hardware_details()

                active_reservation_id = None
                if hardware.get("activeReservation"):
                    active_reservation_id = hardware["activeReservation"]["id"]
                if not active_reservation_id:
                    logger.debug("No active reservation found")
                    sleep(5)
                    continue

                job_runs_data = self.primitive.jobs.get_job_runs(
                    status="pending", first=1, reservation_id=active_reservation_id
                )

                pending_job_runs = [
                    edge["node"] for edge in job_runs_data["jobRuns"]["edges"]
                ]

                for job_run in pending_job_runs:
                    logger.debug("Found pending Job Run")
                    logger.debug(f"Job Run ID: {job_run['id']}")
                    logger.debug(f"Job Name: {job_run['job']['name']}")

                    git_repo_full_name = job_run["gitCommit"]["repoFullName"]
                    git_ref = job_run["gitCommit"]["sha"]
                    logger.debug(
                        f"Downloading repository {git_repo_full_name} at ref {git_ref}"
                    )

                    github_access_token = (
                        self.primitive.jobs.github_access_token_for_job_run(
                            job_run["id"]
                        )
                    )

                    downloaded_git_repository_dir = (
                        self.primitive.git.download_git_repository_at_ref(
                            git_repo_full_name=git_repo_full_name,
                            git_ref=git_ref,
                            github_access_token=github_access_token,
                        )
                    )

                    match job_run["job"]["slug"]:
                        case "lint":
                            logger.debug("Executing Lint Job")

                            self.primitive.jobs.job_run_update(
                                job_run["id"], status="request_in_progress"
                            )

                            result, message = self.primitive.lint.execute(
                                source=downloaded_git_repository_dir
                            )
                            if result:
                                conclusion = "success"
                            else:
                                conclusion = "failure"
                            self.primitive.jobs.job_run_update(
                                job_run["id"],
                                status="request_completed",
                                conclusion=conclusion,
                                stdout=message,
                            )

                            logger.debug("Lint Job Completed")
                        case "sim":
                            logger.debug("Executing Sim Job")

                            self.primitive.job.job_run_update(
                                job_run["id"], status="request_in_progress"
                            )

                            result, message = self.primitive.sim.execute(
                                source=downloaded_git_repository_dir,
                                cmd=(
                                    "make",
                                    "all",
                                ),  # TODO: Change this to use container args container cmd
                            )

                            # Attempt artifact collection
                            self.primitive.sim.collect_artifacts(
                                source=downloaded_git_repository_dir
                            )

                            if result:
                                conclusion = "success"
                            else:
                                conclusion = "failure"
                            self.primitive.jobs.job_run_update(
                                job_run["id"],
                                status="request_completed",
                                conclusion=conclusion,
                                stdout=message,
                            )

                            logger.debug("Sim Job Completed")

                sleep(5)
        except KeyboardInterrupt:
            logger.info(" [*] Stopping primitive...")
            self.primitive.hardware.check_in_http(is_available=False, is_online=False)
            sys.exit()
