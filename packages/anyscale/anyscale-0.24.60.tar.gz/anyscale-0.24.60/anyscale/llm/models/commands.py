from anyscale._private.sdk import sdk_command
from anyscale.client.openapi_client import FineTunedModel
from anyscale.llm.models._private.models_sdk import PrivateLLMModelsSDK


_LLM_MODELS_SDK_SINGLETON_KEY = "llm_models_sdk"


_RETRIEVE_EXAMPLE = """
import anyscale

anyscale.llm.models.retrieve(model_id="my-model-id")
"""

_RETRIEVE_ARG_DOCSTRINGS = {
    "model_id": " ID of the finetuned model for which the model card is being retrieved."
}


@sdk_command(
    _LLM_MODELS_SDK_SINGLETON_KEY,
    PrivateLLMModelsSDK,
    doc_py_example=_RETRIEVE_EXAMPLE,
    arg_docstrings=_RETRIEVE_ARG_DOCSTRINGS,
)
def retrieve(model_id: str, _sdk: PrivateLLMModelsSDK,) -> FineTunedModel:
    """Retrieves model card for a finetuned model."""
    return _sdk.retrieve(model_id)
