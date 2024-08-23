from typing import List, Optional
from gql import gql


from primitive.utils.actions import BaseAction


class Projects(BaseAction):
    def get_job_runs(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        job_id: Optional[str] = None,
        reservation_id: Optional[str] = None,
        git_commit_id: Optional[str] = None,
        status: Optional[str] = None,
        conclusion: Optional[str] = None,
        first: Optional[int] = 1,
        last: Optional[int] = None,
    ):
        query = gql(
            """
fragment PageInfoFragment on PageInfo {
  hasNextPage
  hasPreviousPage
  startCursor
  endCursor
}

fragment JobRunFragment on JobRun {
  id
  pk
  createdAt
  updatedAt
  completedAt
  startedAt
  status
  conclusion
  stdout
  job {
    id
    pk
    slug
    name
    createdAt
    updatedAt
  }
  gitCommit {
    sha
    branch
    repoFullName
  }
}

query jobRuns(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: JobRunFilters
  $order: JobRunOrder
) {
  jobRuns(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
    order: $order
  ) {
    totalCount
    pageInfo {
      ...PageInfoFragment
    }
    edges {
      cursor
      node {
        ...JobRunFragment
      }
    }
  }
}
"""
        )

        filters = {}
        if organization_id:
            filters["organization"] = {"id": organization_id}
        if project_id:
            filters["project"] = {"id": project_id}
        if job_id:
            filters["job"] = {"id": job_id}
        if reservation_id:
            filters["reservation"] = {"id": reservation_id}
        if git_commit_id:
            filters["gitCommit"] = {"id": git_commit_id}
        if status:
            filters["status"] = {"exact": status}
        if conclusion:
            filters["conclusion"] = {"exact": status}

        variables = {
            "first": first,
            "last": last,
            "filters": filters,
            "order": {
                "createdAt": "DESC",
            },
        }

        result = self.primitive.session.execute(query, variable_values=variables)
        return result

    def get_job_run(self, id: str):
        query = gql(
            """
            query jobRun($id: GlobalID!) {
                jobRun(id: $id) {
                    id
                    organization {
                        id
                    }
                }
            }
            """
        )
        variables = {"id": id}
        result = self.primitive.session.execute(query, variable_values=variables)
        return result

    def job_run_update(
        self,
        id: str,
        status: str = None,
        conclusion: str = None,
        stdout: str = None,
        file_ids: Optional[List[str]] = [],
    ):
        mutation = gql(
            """
            mutation jobRunUpdate($input: JobRunUpdateInput!) {
                jobRunUpdate(input: $input) {
                    ... on JobRun {
                        id
                        status
                        conclusion
                    }
                }
            }
        """
        )
        input = {"id": id}
        if status:
            input["status"] = status
        if conclusion:
            input["conclusion"] = conclusion
        if file_ids and len(file_ids) > 0:
            input["files"] = file_ids
        if stdout:
            input["stdout"] = stdout
        variables = {"input": input}
        result = self.primitive.session.execute(mutation, variable_values=variables)
        return result

    def github_access_token_for_job_run(self, job_run_id: str):
        query = gql(
            """
query ghAppTokenForJobRun($jobRunId: GlobalID!) {
    ghAppTokenForJobRun(jobRunId: $jobRunId)
}
"""
        )
        variables = {"jobRunId": job_run_id}
        result = self.primitive.session.execute(query, variable_values=variables)
        return result["ghAppTokenForJobRun"]
