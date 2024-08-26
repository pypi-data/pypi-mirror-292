__all__ = [
    "BaseModel",
    "Field",
    "hf",
    "logger",
    "app",
    "legacy_agents",
    "cli",
    "chainofthought",
    "classify",
    "completion",
    "embedding",
    "image",
    "code",
    "delegate",
    "extract",
    "function",
    "generate",
    "qdrant",
    "sql",
    "transcribe",
    "speak",
    "zyxModuleLoader",
]

# --- zyx ----------------------------------------------------------------

from .core.ext import BaseModel, Field, zyxModuleLoader


class legacy_agents(zyxModuleLoader):
    pass


legacy_agents.init("zyx.client.agents", "Agents")


class app(zyxModuleLoader):
    pass


app.init("zyx.client.app", "app")


class cli(zyxModuleLoader):
    pass


cli.init("zyx.client.app", "cli")


class chainofthought(zyxModuleLoader):
    pass


chainofthought.init("zyx.client.fn", "chainofthought")


class classify(zyxModuleLoader):
    pass


classify.init("zyx.client.fn", "classify")


class code(zyxModuleLoader):
    pass


code.init("zyx.client.fn", "code")


class extract(zyxModuleLoader):
    pass


extract.init("zyx.client.fn", "extract")


class delegate(zyxModuleLoader):
    pass


delegate.init("zyx.client.fn", "delegate")


class function(zyxModuleLoader):
    pass


function.init("zyx.client.fn", "function")


class image(zyxModuleLoader):
    pass


image.init("zyx.multimodal.main", "image")


class generate(zyxModuleLoader):
    pass


generate.init("zyx.client.fn", "generate")


class completion(zyxModuleLoader):
    pass


completion.init("zyx.client.main", "completion")


class hf(zyxModuleLoader):
    pass


hf.init("huggingface_hub.inference._client", "InferenceClient")


class logger(zyxModuleLoader):
    pass


logger.init("loguru", "logger")


class qdrant(zyxModuleLoader):
    pass


qdrant.init("zyx.data.qdr", "Qdrant")


class embedding(zyxModuleLoader):
    pass


embedding.init("litellm.main", "embedding")


class speak(zyxModuleLoader):
    pass


speak.init("zyx.multimodal.main", "openai_text_to_speech")


class transcribe(zyxModuleLoader):
    pass


transcribe.init("zyx.multimodal.main", "openai_speech_to_text")


class sql(zyxModuleLoader):
    pass


sql.init("zyx.data.main", "SQLModelVectorDB")


def chat():
    import argparse
    from .client.app import cli as chat_cli

    parser = argparse.ArgumentParser(description="ZYX Chat CLI")

    parser.add_argument(
        "--provider", type=str, help="The provider instance to handle the chat logic"
    )
    parser.add_argument(
        "--messages", type=str, help="The messages to send to the model"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="The model to use for completions",
    )
    parser.add_argument("--tools", nargs="+", help="The tools to use for completions")
    parser.add_argument(
        "--run-tools", type=bool, default=True, help="Whether to run the tools"
    )
    parser.add_argument(
        "--response-model",
        type=str,
        help="The Pydantic response model to use for completions",
    )
    parser.add_argument(
        "--mode", type=str, default="tools", help="The mode to use for completions"
    )
    parser.add_argument("--base-url", type=str, help="The base URL for the API")
    parser.add_argument("--api-key", type=str, help="The API key to use for the API")
    parser.add_argument(
        "--organization", type=str, help="The organization to use for the API"
    )
    parser.add_argument("--top-p", type=float, help="The top-p value for completions")
    parser.add_argument(
        "--temperature", type=float, help="The temperature value for completions"
    )
    parser.add_argument(
        "--max-tokens", type=int, help="The maximum number of tokens for completions"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="The maximum number of retries for completions",
    )
    parser.add_argument(
        "--verbose", type=bool, default=False, help="Whether to print verbose output"
    )
    parser.add_argument(
        "--background",
        type=str,
        default="midnight_black",
        help="Background color of the app",
    )
    parser.add_argument(
        "--text", type=str, default="steel_grey", help="Text color in the chat display"
    )
    parser.add_argument(
        "--input-field", type=str, default="ocean_blue", help="Color of the input field"
    )

    args = parser.parse_args()

    # Convert args to a dictionary and remove None values
    chat_args = {k: v for k, v in vars(args).items() if v is not None}

    chat_cli(**chat_args)
