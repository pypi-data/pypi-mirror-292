from typing import Optional

from anyscale._private.anyscale_client import AnyscaleClientInterface
from anyscale._private.sdk.base_sdk import BaseSDK
from anyscale._private.sdk.timer import Timer
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import (
    DeletedPlatformFineTunedModel,
    FineTunedModel,
)


class PrivateLLMModelsSDK(BaseSDK):
    def __init__(
        self,
        *,
        logger: Optional[BlockLogger] = None,
        client: Optional[AnyscaleClientInterface] = None,
        timer: Optional[Timer] = None,
    ):
        super().__init__(logger=logger, client=client, timer=timer)

    def list(
        self,
        *,
        cloud_id: Optional[str] = None,
        project_id: Optional[str] = None,
        max_items: int = 20,
    ):
        return self.client.list_finetuned_models(cloud_id, project_id, max_items)

    def get(
        self, *, model_id: Optional[str] = None, job_id: Optional[str] = None
    ) -> FineTunedModel:
        return self.client.get_finetuned_model(model_id, job_id)

    def delete(self, model_id) -> DeletedPlatformFineTunedModel:
        return self.client.delete_finetuned_model(model_id)
