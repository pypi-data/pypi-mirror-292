from typing import Optional

from anyscale._private.anyscale_client import AnyscaleClientInterface
from anyscale._private.sdk.base_sdk import BaseSDK
from anyscale._private.sdk.timer import Timer
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models import FineTunedModel


class PrivateLLMModelsSDK(BaseSDK):
    def __init__(
        self,
        *,
        logger: Optional[BlockLogger] = None,
        client: Optional[AnyscaleClientInterface] = None,
        timer: Optional[Timer] = None,
    ):
        super().__init__(logger=logger, client=client, timer=timer)

    def list(self):
        raise NotImplementedError

    def retrieve(self, model_id) -> FineTunedModel:
        return self.client.retrieve_finetuned_model(model_id)
