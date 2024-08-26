from . import tools
from ..core.ext import zyxModuleLoader


class Agents(zyxModuleLoader):
    pass


Agents.init("zyx.agents.main", "Agents")



class BaseTool(zyxModuleLoader):
    pass


BaseTool.init("crewai_tools.tools.base_tool", "BaseTool")



class tool(zyxModuleLoader):
    pass


tool.init("langchain_core.tools.convert", "tool")