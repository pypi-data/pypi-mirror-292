import click

from anyscale.controllers.llm.models_controller import ModelsController


@click.group("models", help="Finetuned models stored on your Anyscale cloud.")
def models_cli():
    pass


@models_cli.command(
    name="retrieve",
    short_help="Retrieve information for a model in your Anyscale cloud.",
)
@click.argument("model_id", required=True)
def retrieve_model(model_id: str) -> None:
    """
    Retrieves the model card for the given model ID.

    MODEL_ID = ID for the model of interest

    Example usage:
        anyscale llm models retrieve my-model-id
    """
    print(ModelsController().retrieve_model(model_id))
