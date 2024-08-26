from crewai_tools.tools.base_tool import BaseTool
from langchain_core.tools.convert import tool

from . import tools as tools
from ..core.ext import zyxModuleLoader


class agents(zyxModuleLoader):
    pass


agents.init("zyx.agents.main", "Agents")
