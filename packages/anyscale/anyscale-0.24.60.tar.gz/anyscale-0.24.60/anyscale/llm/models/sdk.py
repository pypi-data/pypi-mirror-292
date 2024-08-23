from typing import Any, Optional

from anyscale._private.anyscale_client import AnyscaleClientInterface
from anyscale._private.sdk import sdk_docs
from anyscale._private.sdk.base_sdk import BaseSDK, Timer
from anyscale.cli_logger import BlockLogger
from anyscale.llm.models._private.models_sdk import PrivateLLMModelsSDK
from anyscale.llm.models.commands import (
    _RETRIEVE_ARG_DOCSTRINGS,
    _RETRIEVE_EXAMPLE,
)


class LLMModelsSDK(BaseSDK):
    def __init__(
        self,
        *,
        logger: Optional[BlockLogger] = None,
        client: Optional[AnyscaleClientInterface] = None,
        timer: Optional[Timer] = None,
    ):
        self._private_sdk = PrivateLLMModelsSDK(
            logger=logger, client=client, timer=timer
        )

    @sdk_docs(
        doc_py_example=_RETRIEVE_EXAMPLE, arg_docstrings=_RETRIEVE_ARG_DOCSTRINGS,
    )
    def retrieve(self, model_id: str) -> Any:
        """Retrieves model card for a finetuned model."""
        return self._private_sdk.retrieve(model_id)
