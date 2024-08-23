__all__ = [
    "BaseModel",
    "Field",
    "hf",
    "logger",
    "app",
    "agents",
    "cli",
    "chainofthought",
    "classify",
    "completion",
    "code",
    "delegate",
    "extract",
    "function",
    "generate",
    "rag",
    "zyxModuleLoader",
]

# --- zyx ----------------------------------------------------------------

from .core.ext import BaseModel, Field, zyxModuleLoader


class agents(zyxModuleLoader):
    pass


agents.init("zyx.client.agents", "Agents")


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


class rag(zyxModuleLoader):
    pass


rag.init("zyx.client.rag", "Qdrant")
