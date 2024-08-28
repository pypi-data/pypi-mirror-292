from typing import List, Optional

from anyscale.api_utils.common_utils import (
    get_current_workspace_id,
    source_cloud_id_and_project_id,
)
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client import (
    DeletedPlatformFineTunedModel,
    FineTunedModel,
    FinetunedmodelListResponse,
)
from anyscale.controllers.base_controller import BaseController


LIST_ENDPOINT_COUNT = 20


class ModelsController(BaseController):
    def __init__(
        self, log: Optional[BlockLogger] = None, initialize_auth_api_client: bool = True
    ):
        if log is None:
            log = BlockLogger()

        super().__init__(initialize_auth_api_client=initialize_auth_api_client)

        self.log = log
        self.log.open_block("Output")

    def get_model(
        self, model_id: Optional[str], job_id: Optional[str]
    ) -> FineTunedModel:
        """Retrieves model information given model id"""
        if model_id:
            return self.api_client.get_model_api_v2_llm_models_model_id_get(
                model_id
            ).result
        elif job_id:
            return self.api_client.get_model_by_job_id_api_v2_llm_models_get_by_job_id_job_id_get(
                job_id
            ).result
        else:
            raise ValueError("Atleast one of `model-id` or `job-id` should be provided")

    def delete_model(self, model_id: str) -> DeletedPlatformFineTunedModel:
        return self.api_client.delete_model_api_v2_llm_models_model_id_delete(
            model_id
        ).result

    def list_models(
        self, *, cloud_id: Optional[str], project_id: Optional[str], max_items: int
    ) -> List[FineTunedModel]:
        """Lists fine-tuned models optionally filtered by `cloud_id` and `project_id`"""
        if get_current_workspace_id() is not None:
            # Resolve `cloud_id` and `project_id`. If not provided and if this is being run in a workspace,
            # we use the `cloud_id` and `project_id` of the workspace
            cloud_id, project_id = source_cloud_id_and_project_id(
                internal_api=self.api_client,
                external_api=self.anyscale_api_client,
                cloud_id=cloud_id,
                project_id=project_id,
            )
        paging_token = None
        results = []
        while True:
            count = min(LIST_ENDPOINT_COUNT, max_items)
            resp: FinetunedmodelListResponse = self.api_client.list_models_api_v2_llm_models_get(
                cloud_id=cloud_id,
                project_id=project_id,
                paging_token=paging_token,
                count=count,
            )
            models = resp.results
            results.extend(models)
            if not len(models) or not resp.metadata.next_paging_token:
                break

            if max_items and len(results) >= max_items:
                break
            paging_token = resp.metadata.next_paging_token

        return results[:max_items] if max_items else results
