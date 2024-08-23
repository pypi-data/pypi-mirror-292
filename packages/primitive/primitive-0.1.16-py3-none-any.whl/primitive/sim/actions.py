from gql import gql
from pathlib import Path
from primitive.utils.actions import BaseAction
from loguru import logger
import subprocess
from typing import Tuple, List
from ..utils.files import find_files_for_extension
import os
from .vcd import TokenKind, tokenize
import io
from collections import defaultdict
import urllib
import json


class Sim(BaseAction):
    def execute(
        self, source: Path = Path.cwd(), cmd: Tuple[str] = ["make"]
    ) -> Tuple[bool, str]:
        logger.debug(f"Starting simulation run for source: {source}")

        os.chdir(source)
        logger.debug(f"Changed to {source}, starting sim run")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
        except FileNotFoundError:
            message = f"Did not find {cmd}"
            logger.error(message)
            return False, message

        logger.debug("Sim run complete.")

        message = ""
        if result.stderr:
            logger.error("\n" + result.stderr)
        if result.stdout:
            logger.info("\n" + result.stdout)
        message = "See above logs for sim output."

        if result.returncode != 0:
            if not self.primitive.DEBUG:
                message = result.stderr
            return False, message
        else:
            message = "Sim run successful."

        return True, message

    def upload_file(self, path: Path) -> str:
        file_upload_response = self.primitive.files.file_upload(
            path, key_prefix=f"{self.job_run_id}/{str(path.parent)}"
        )
        return file_upload_response.json()["data"]["fileUpload"]["id"]

    def collect_artifacts(self, source) -> None:
        file_ids = []

        # Look for VCD artifacts
        files = find_files_for_extension(source, ".vcd")
        for file in files:
            trace_file_ids = self.generate_timeseries(path=file)
        file_ids.extend(trace_file_ids)

        logger.debug("Uploading additional artifacts...")
        files = find_files_for_extension(source, (".xml", ".vcd", ".log", ".history"))
        for file_path in files:
            try:
                file_ids.append(self.upload_file(file_path))
            except FileNotFoundError:
                logger.warning(f"{file_path} not found...")

        logger.debug("Updating job run...")
        if len(file_ids) > 0:
            job_run_update_response = self.primitive.projects.job_run_update(
                id=self.job_run_id, file_ids=file_ids
            )
            logger.success(job_run_update_response)

    def generate_timeseries(self, path: Path) -> List[str]:
        logger.debug("Parsing VCD file...")
        with open(path, "rb") as f:
            tokens = tokenize(io.BytesIO(f.read()))

        metadata = defaultdict(dict)
        traces = defaultdict(list)
        timescale_unit = "s"
        timescale_magnitude = 1
        active_module: str = ""
        time: int = 0

        for token in tokens:
            match token.kind:
                case TokenKind.TIMESCALE:
                    timescale_unit = token.data.unit.value
                    timescale_magnitude = token.data.magnitude.value
                case TokenKind.SCOPE:
                    active_module = token.data.ident
                case TokenKind.CHANGE_TIME:
                    time = int(token.data)
                case TokenKind.VAR:
                    var = {
                        "id_code": token.data.id_code,
                        "module": active_module,
                        "var_type": str(token.data.type_),
                        "var_size": token.data.size,
                        "reference": token.data.reference,
                        "bit_index": str(token.data.bit_index),
                    }
                    metadata[token.data.id_code] = var
                case TokenKind.CHANGE_SCALAR:
                    traces[token.data.id_code].append(
                        (str(time), str(token.data.value))
                    )
                case TokenKind.CHANGE_VECTOR:
                    traces[token.data.id_code].append(
                        (str(time), str(token.data.value))
                    )

        # Add traces and write files
        logger.debug("Uploading traces...")
        trace_file_ids = []
        for id_code, timeseries in traces.items():

            def hashed(id_code):
                return urllib.parse.quote_plus(id_code, safe="")

            file_path = path.parent / f"{hashed(id_code)}.vcd.json"
            with open(file_path, "w") as f:
                f.write(json.dumps(timeseries))

            trace_file_id = self.upload_file(file_path)
            trace_file_ids.append(trace_file_id)

            self.trace_create(
                id_code=id_code,
                module=metadata[id_code]["module"],
                var_type=metadata[id_code]["var_type"],
                var_size=metadata[id_code]["var_size"],
                reference=metadata[id_code]["reference"],
                bit_index=metadata[id_code]["bit_index"],
                timescale_unit=timescale_unit,
                timescale_magnitude=timescale_magnitude,
                organization=self.organization_id,
                file=trace_file_id,
                job_run=self.job_run_id,
            )

        return trace_file_ids

    def trace_create(
        self,
        id_code: str,
        module: str,
        var_type: str,
        var_size: int,
        reference: str,
        bit_index: str,
        timescale_unit: str,
        timescale_magnitude: int,
        organization: str,
        file: str,
        job_run: str,
    ):
        mutation = gql(
            """
            mutation createTrace($input: TraceCreateInput!) {
                traceCreate(input: $input) {
                    ... on Trace {
                        id
                    }
                }
            }
        """
        )
        input = {
            "idCode": id_code,
            "module": module,
            "varType": var_type,
            "varSize": var_size,
            "reference": reference,
            "bitIndex": bit_index,
            "timescaleUnit": timescale_unit,
            "timescaleMagnitude": timescale_magnitude,
            "organization": organization,
            "file": file,
            "jobRun": job_run,
        }
        variables = {"input": input}
        result = self.primitive.session.execute(mutation, variable_values=variables)
        return result
