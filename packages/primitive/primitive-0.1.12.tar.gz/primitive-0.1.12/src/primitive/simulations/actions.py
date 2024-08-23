from gql import gql


from primitive.utils.actions import BaseAction


class Simulations(BaseAction):
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
