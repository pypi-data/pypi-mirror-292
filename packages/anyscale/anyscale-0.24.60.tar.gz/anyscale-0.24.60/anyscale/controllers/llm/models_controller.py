from typing import Optional

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client import FineTunedModel
from anyscale.controllers.base_controller import BaseController


class ModelsController(BaseController):
    def __init__(
        self, log: Optional[BlockLogger] = None, initialize_auth_api_client: bool = True
    ):
        if log is None:
            log = BlockLogger()

        super().__init__(initialize_auth_api_client=initialize_auth_api_client)

        self.log = log
        self.log.open_block("Output")

    def retrieve_model(self, model_id: str) -> FineTunedModel:
        return self.api_client.get_model_api_v2_llm_models_model_id_get(model_id)
