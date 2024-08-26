
# **hammad-dev**

### *the hammad master repository*

### <font color="#9bc2cc">Libraries</font>

| <font color="#00BFFF">**Library**</font> | <italic> Working Dates </italic> | <italic>Link</italic> | <italic>Depreciated</italic>
| :--- | :--- | :--- | :--- |
| <font color="#d96752">hammadpy</font> | <italic> ```11/2023 -> 01/2024```</italic> | [```hammadpy```](./python/hammadpy) | [x] |
| <font color="#d96752">hadronic</font> | <italic> ```01/2024 -> 01/2024```</italic> | [```hadronic```](./python/hadronic) | [x] |
| <font color="#d96752">suzuka</font> | <italic> ```01/2024 -> 02/2024```</italic> | [```suzuka```](./python/suzuka) | [x] |
| <font color="#d96752">yosemite</font> | <italic> ```02/2024 -> 04/2024```</italic> | [```yosemite```](./python/yosemite) | [x] |
| <font color="#b4d998">zyx</font> | <italic> ```02/2024 -> Current```</italic> | [```zyx```](./python/zyx) | [] |

</br>

## <font color="#9bc2cc">**zyx** - *ease of use hyper-fast abstractions*</font> </br>

| <b>Notebooks</b> | <i>Link</i> |
| :--- | :--- |
| <font color="#00BFFF">**LLM Completions**</font> | [```llm-completions.ipynb```](./concepts/zyx/notebooks/llm-completions.ipynb) |
| <font color="#00BFFF">**Agents (*New*)**</font> | [```agents.ipynb```](./concepts/zyx/notebooks/agents.ipynb) |
| <font color="#00BFFF">**RAG**</font> | [```rag.ipynb```](./concepts/zyx/notebooks/rag.ipynb) |
| <font color="#00BFFF">**MarvinAI Inspired LLM Functions**</font> | [```llm-functions.ipynb```](./concepts/zyx/notebooks/llm-functions.ipynb) |
| <font color="#00BFFF">**Multimodal Generations**</font> | [```multimodal.ipynb```](./concepts/zyx/notebooks/multimodal.ipynb) |

### <font color="#9bc2cc">**Installation**</font>

```bash
pip install zyx
```

```bash
# New CrewAI Based Agents
pip install 'zyx[experimental]'
```

<font color="#00BFFF">**zyx**</font> is a library built with the sole purpose of providing one of the easiest API's and abstractions for working with LLMs, using single functions; to perform tasks such as: </br>

```markdown
> Click on the function name to view example usage.
```

- <font color="#FFA500">**Ease of Use LLM Modules**</font> 
    - <font color="#00BFFF">Easy access CLI chatbot</font> (Use either straight from terminal or with the function.) 
    - <font color="#00BFFF">Simple & Modular Chatbot builder</font> to create custom input/output chatbots.
    - <font color="#00BFFF">Pydantic modules</font> easily accessible @ <font color="#b4d998">**zyx.BaseModel</font>()** & <font color="#b4d998">**zyx.Field</font>()** for structured data.

- <font color="#FFA500">**Extremely Modular LLM Completions**</font> (built on LiteLLM & Instructor)
    - **<font color="#b4d998">zyx.completion</font>()**
    - *<font color="#00BFFF">One function</font> to run the LLM workflow*
    - *Any <font color="#00BFFF">LiteLLM supported model</font> is compatible*
    - <font color="#00BFFF">*Structured outputs*</font> using either **Pydantic BaseModels** or **JSON Dictionaries**.
    - <font color="#00BFFF">Tool calling</font> with **Python functions**, **Pydantic BaseModels** & **OpenAI format tool/function JSON**.
    - Optional <font color="#00BFFF">tool execution</font> for functions/workflows.
    - <font color="#00BFFF">Vision model</font> support.

- <font color="#FFA500">**LLM Agents w/ Multi Agent Pipelines**</font>
    - *<font color="#b4d998">**zyx.legacy_agents**</font>()* - Legacy LLM agents, built on top of instructor.
    - *<font color="#b4d998">**zyx.agents**</font>()* - New multi agent pipeline, built on **CrewAI**. (Not available in base package, requires ```zyx[experimental]```) 

- <font color="#FFA500">**Easy memory & vector search/creation for RAG**</font>
    - *<font color="#b4d998">**zyx.qdrant**</font>()* - Incredibly simple <font color="#00BFFF">vector store with search & LLM completions</font>.
    - *<font color="#b4d998">**zyx.sql**</font>()* - Easy <font color="#00BFFF">SQL data management with search & LLM completions</font>.

- <font color="#FFA500">**Hyper Quick Multimodal Generations**</font>
    - *<font color="#b4d998">**zyx.image**</font>()* - <font color="#00BFFF">*Image generation*</font> connected to Dall-E, FAL-AI, or your local comfyUI or Automatic1111 endpoint.
    - *<font color="#b4d998">**zyx.transcribe**</font>()* - <font color="#00BFFF">*Speech Transcription*</font> OpenAI whisper powered speech transcription; with optional microphone support.
    - *<font color="#b4d998">**zyx.speak**</font>()* - <font color="#00BFFF">*Text-to-Speech Generations*</font> with OpenAI powered TTS, with easy quick-play parameters.

- <font color="#FFA500">**@Marvin-AI Inspired LLM Functions**</font>
    - **<font color="#b4d998">zyx.function</font>()** (comes with two options)
        - <font color="#00BFFF">*Create a mock function response*</font>
        - <font color="#00BFFF">*Generate an actual Python method</font>, to return the desired output*
    - **<font color="#b4d998">zyx.classify</font>()** - <font color="#00BFFF">*Label based classification.*</font>
    - **<font color="#b4d998">zyx.extract</font>()** - <font color="#00BFFF">*Extract content into desired schema.*</font>
    - **<font color="#b4d998">zyx.generate</font>()** - <font color="#00BFFF">*Easiest way to create structured data.*</font>
    - **<font color="#b4d998">zyx.chainofthought</font>()** - <font color="#00BFFF">*Create a chain of thought response.*</font>
    - **<font color="#b4d998">zyx.code</font>()** - <font color="#00BFFF">*Slightly increased code response accuracy.*</font>