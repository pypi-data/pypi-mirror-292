__all__ = ["Agents", "BaseTool", "tool", "tools"]


from . import tools
from ..core.ext import zyxModuleLoader


class Agents(zyxModuleLoader):
    pass


Agents.init("zyx.experimental.main", "Agents")


class BaseTool(zyxModuleLoader):
    pass


BaseTool.init("crewai_tools.tools.base_tool", "BaseTool")


class tool(zyxModuleLoader):
    pass


tool.init("langchain_core.tools.convert", "tool")
