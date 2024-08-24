from ..core.ext import BaseModel, Field
from typing import Any, Callable, Optional, get_type_hints, Union, List, Literal, Dict
from .main import Client


def chainofthought(
    query: str,
    answer_type: Any = str,
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 0,
    verbose: bool = False,
    mode: Literal["json", "md_json", "tools"] = "md_json",
):
    class Reasoning(BaseModel):
        chain_of_thought: str

    class FinalAnswer(BaseModel):
        answer: Any

    reasoning_prompt = f"""
    Let's approach this step-by-step:
    1. Understand the problem
    2. Identify key variables and their values
    3. Develop a plan to solve the problem
    4. Execute the plan, showing all calculations
    5. Verify the answer

    Question: {query}

    Now, let's begin our reasoning:
    """

    reasoning_response = Client().completion(
        messages=[{"role": "user", "content": reasoning_prompt}],
        model=model,
        api_key=api_key,
        base_url=base_url,
        max_tokens=max_tokens,
        temperature=temperature,
        response_model=Reasoning,
        verbose=verbose,
        mode="md_json" if model.startswith(("ollama/", "ollama_chat/")) else mode,
    )

    if verbose:
        print("Chain of Thought:")
        print(reasoning_response.chain_of_thought)

    extraction_prompt = f"""
    Based on the following reasoning:
    {reasoning_response.chain_of_thought}

    Provide the final answer to the question: "{query}"
    Your answer should be of type: {answer_type.__name__}
    Only provide the final answer, without any additional explanation.
    """

    final_answer_response = Client().completion(
        messages=[{"role": "user", "content": extraction_prompt}],
        model=model,
        api_key=api_key,
        base_url=base_url,
        max_tokens=max_tokens,
        temperature=temperature,
        response_model=FinalAnswer,
        mode="md_json" if model.startswith(("ollama/", "ollama_chat/")) else mode,
        verbose=verbose,
    )

    return final_answer_response.answer


def function(
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    mode: Literal["json", "md_json", "tools"] = "md_json",
    mock: bool = True,
    **kwargs,
) -> Callable[[Callable], Callable]:
    def decorator(f: Callable) -> Callable:
        from pydantic import create_model
        from functools import wraps
        import tenacity
        import tempfile
        import subprocess
        import sys
        import json

        @wraps(f)
        @tenacity.retry(
            stop=tenacity.stop_after_attempt(3),
            retry=tenacity.retry_if_exception_type(),
        )
        def wrapper(*args, **kwargs):
            type_hints = get_type_hints(f)
            return_type = type_hints.pop("return", Any)
            function_args = {k: v for k, v in type_hints.items()}
            input_dict = dict(zip(function_args.keys(), args))
            input_dict.update(kwargs)

            if mock:
                FunctionResponseModel = create_model(
                    "FunctionResponseModel",
                    output=(return_type, ...),
                )
                messages = [
                    {
                        "role": "system",
                        "content": f"""
                        You are a Python function emulator. Your goal is to simulate the response of this Python function:
                        Function: {f.__name__}
                        Arguments and their types: {function_args}
                        Return type: {return_type}
                        Description: {f.__doc__}
                        Respond only with the output the function would produce, without any additional explanation.
                        """,
                    },
                    {"role": "user", "content": f"Function inputs: {input_dict}"},
                ]
                response = Client().completion(
                    messages=messages,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    response_model=FunctionResponseModel,
                    mode="md_json"
                    if model.startswith(("ollama/", "ollama_chat/"))
                    else mode,
                    **kwargs,
                )
                return response.output
            else:

                class CodeGenerationModel(BaseModel):
                    code: str = Field(
                        ..., description="Complete Python code as a single string"
                    )

                messages = [
                    {
                        "role": "system",
                        "content": f"""
                        You are a Python code generator. Your goal is to generate a Python function that matches this specification:
                        Function: {f.__name__}
                        Arguments and their types: {function_args}
                        Return type: {return_type}
                        Description: {f.__doc__}
                        
                        Generate the complete Python code as a single string, including necessary import statements.
                        The code should define the function and include a call to the function with the provided inputs.
                        After calling the function, convert the result to a JSON-serializable format if necessary.
                        The last line should print the JSON-encoded result using json.dumps().
                        Do not include any explanations or comments in your response.
                        """,
                    },
                    {
                        "role": "user",
                        "content": f"Generate code for the function with these inputs: {input_dict}",
                    },
                ]
                response = Client().completion(
                    messages=messages,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    response_model=CodeGenerationModel,
                    mode="md_json"
                    if model.startswith(("ollama/", "ollama_chat/"))
                    else mode,
                    **kwargs,
                )

                # Create a temporary Python file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as temp_file:
                    temp_file.write(response.code)

                # Execute the temporary Python file
                result = subprocess.run(
                    [sys.executable, temp_file.name], capture_output=True, text=True
                )

                if result.returncode != 0:
                    raise RuntimeError(
                        f"Error executing generated code: {result.stderr}"
                    )

                # Parse the JSON output
                try:
                    output = json.loads(result.stdout.strip())
                except json.JSONDecodeError as e:
                    raise RuntimeError(
                        f"Error parsing JSON output: {e}\nRaw output: {result.stdout}"
                    )

                return output

        return wrapper

    return decorator


def code(
    instructions: str = None,
    language: Union[
        Literal[
            "python",
            "javascript",
            "typescript",
            "shell",
            "bash",
            "java",
            "cpp",
            "c++",
            "go",
            "sql",
        ],
        str,
    ] = "python",
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    organization: Optional[str] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    temperature: float = 0,
    tools: Optional[List[Union[Callable, dict, BaseModel]]] = None,
    verbose: bool = False,
    mode: Literal["json", "md_json", "tools"] = "md_json",
):
    system_prompt = f"""
    ## CONTEXT ##
    You are a code generator. Your only goal is provide code based on the instructions given.
    Language : {language}
    
    ## OBJECTIVE ##
    Plan out your reasoning before you begin to respond at all.
    """

    class CodeResponseModel(BaseModel):
        code: str

    response = Client().completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instructions},
        ],
        model=model,
        api_key=api_key,
        base_url=base_url,
        organization=organization,
        max_tokens=max_tokens,
        max_retries=max_retries,
        temperature=temperature,
        tools=tools,
        response_model=CodeResponseModel,
        verbose=verbose,
        mode="md_json" if model.startswith(("ollama/", "ollama_chat/")) else mode,
    )
    return response.code


def generate(
    target: BaseModel,
    instructions: Optional[str] = None,
    n: int = 1,
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    organization: Optional[str] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    temperature: float = 0,
    mode: Literal["json", "md_json", "tools"] = "md_json",
    verbose: bool = False,
):
    from pydantic import create_model

    ResponseModel = create_model("ResponseModel", items=(List[target], ...))

    system_message = f"""
    You are a data generator. Your task is to generate {n} valid instance(s) of the following Pydantic model:
    
    {target.model_json_schema()}
    
    Ensure that all generated instances comply with the model's schema and constraints.
    """
    user_message = (
        instructions
        if instructions
        else f"Generate {n} instance(s) of the given model."
    )

    response = Client().completion(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        model=model,
        api_key=api_key,
        base_url=base_url,
        organization=organization,
        max_tokens=max_tokens,
        max_retries=max_retries,
        temperature=temperature,
        verbose=verbose,
        mode="md_json" if model.startswith(("ollama/", "ollama_chat/")) else mode,
        response_model=ResponseModel,
    )
    return response.items


def extract(
    target: BaseModel,
    text: str,
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    organization: Optional[str] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    temperature: float = 0,
    mode: Literal["json", "md_json", "tools"] = "md_json",
    verbose: bool = False,
):
    system_message = f"""
    You are an information extractor. Your task is to extract relevant information from the given text 
    and fit it into the following Pydantic model:
    
    {target.model_json_schema()}
    
    Only extract information that is explicitly stated in the text. Do not infer or generate any information 
    that is not present in the input text. If a required field cannot be filled with information from the text, 
    leave it as None or an empty string as appropriate.
    """

    user_message = f"Extract information from the following text and fit it into the given model:\n\n{text}"

    response = Client().completion(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        model=model,
        api_key=api_key,
        base_url=base_url,
        organization=organization,
        max_tokens=max_tokens,
        max_retries=max_retries,
        temperature=temperature,
        verbose=verbose,
        mode="md_json" if model.startswith(("ollama/", "ollama_chat/")) else mode,
        response_model=target,
    )

    return response


def classify(
    inputs: Union[str, List[str]],
    labels: List[str],
    n: int = 1,
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    organization: Optional[str] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    temperature: float = 0,
    mode: Literal["json", "md_json", "tools"] = "md_json",
    verbose: bool = False,
):
    from pydantic import create_model

    class ClassificationResult(BaseModel):
        text: str
        label: str

    ResponseModel = create_model(
        "ResponseModel", items=(List[ClassificationResult], ...)
    )

    system_message = f"""
    You are a text classifier. Your task is to classify the given text(s) into one of the following categories:
    {', '.join(labels)}
    
    For each input, provide {n} classification(s). Each classification should include the original text 
    and the assigned label.
    """

    if isinstance(inputs, str):
        inputs = [inputs]
    user_message = "Classify the following text(s):\n\n" + "\n\n".join(inputs)

    response = Client().completion(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        model=model,
        api_key=api_key,
        base_url=base_url,
        organization=organization,
        max_tokens=max_tokens,
        max_retries=max_retries,
        temperature=temperature,
        verbose=verbose,
        mode="md_json" if model.startswith(("ollama/", "ollama_chat/")) else mode,
        response_model=ResponseModel,
    )

    results = response.items
    if len(inputs) == 1:
        return results
    else:
        grouped_results = []
        for i in range(0, len(results), n):
            grouped_results.append(results[i : i + n])
        return grouped_results


class Delegation(BaseModel):
    name: str
    description: str
    handler: Optional[Callable] = None


class Intent(BaseModel):
    delegation: str
    confidence: float
    task: str


class DelegationResponse(BaseModel):
    intents: List[Intent] = Field(default_factory=list)
    chat_response: Optional[str] = None
    original_messages: List[Dict[str, str]]


class Delegator:
    def __init__(self, delegations: List[Union[Delegation, str, Dict]]):
        self.delegations = self._process_delegations(delegations)

    def _process_delegations(
        self, delegations: List[Union[Delegation, str, Dict]]
    ) -> List[Delegation]:
        processed = []
        for item in delegations:
            if isinstance(item, Delegation):
                processed.append(item)
            elif isinstance(item, str):
                processed.append(Delegation(name=item, description=item))
            elif isinstance(item, dict):
                processed.append(Delegation(**item))
            else:
                raise ValueError(f"Invalid delegation type: {type(item)}")
        return processed

    @staticmethod
    def format_messages(
        messages: Union[str, List[Dict[str, str]]],
    ) -> List[Dict[str, str]]:
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        return messages

    def delegate(
        self,
        messages: Union[str, List[Dict[str, str]]],
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        temperature: float = 0,
        mode: Literal["json", "md_json", "tools"] = "md_json",
        verbose: bool = False,
    ) -> DelegationResponse:
        """
        Delegates the given messages to appropriate delegations or provides a chat response.

        Args:
            messages (Union[str, List[Dict[str, str]]]): The user's messages to be delegated or responded to.
            model (str): The language model to use. Defaults to "gpt-4o-mini".
            api_key (Optional[str]): The API key for the language model.
            base_url (Optional[str]): The base URL for the API.
            organization (Optional[str]): The organization for the API.
            max_tokens (Optional[int]): Maximum number of tokens for the response.
            max_retries (int): Maximum number of retries for the API call.
            temperature (float): Temperature for response generation.
            verbose (bool): Whether to show verbose output.

        Returns:
            DelegationResponse: A response containing intents for delegation or a chat response.
        """
        from .main import Client

        formatted_messages = self.format_messages(messages)
        delegation_names = [d.name for d in self.delegations]

        system_message = f"""
        You are a query delegator and intent classifier. Your task is to analyze the given messages and determine if they should be delegated to any of the following delegations:
        {', '.join(delegation_names)}
        
        If the messages are relevant to one or more delegations, create intents for delegation. If the messages are not relevant to any delegation, provide a chat response.
        
        For each relevant delegation, provide:
        1. The delegation's name
        2. A confidence score (0-1) indicating how relevant the delegation is to the messages
        3. A specific task description for the delegation based on the messages

        If no delegations are relevant, provide a chat response addressing the messages directly.
        """

        all_messages = [
            {"role": "system", "content": system_message}
        ] + formatted_messages

        response = Client().completion(
            messages=all_messages,
            model=model,
            api_key=api_key,
            base_url=base_url,
            organization=organization,
            max_tokens=max_tokens,
            max_retries=max_retries,
            temperature=temperature,
            verbose=verbose,
            mode="md_json" if model.startswith(("ollama/", "ollama_chat/")) else mode,
            response_model=DelegationResponse,
        )

        return response

    def process_response(self, response: DelegationResponse) -> DelegationResponse:
        """
        Process the delegation response, calling handlers if available.

        Args:
            response (DelegationResponse): The response from the delegate method.

        Returns:
            DelegationResponse: The processed response with any updates from handlers.
        """
        for intent in response.intents:
            delegation = next(
                (d for d in self.delegations if d.name == intent.delegation), None
            )
            if delegation and delegation.handler:
                handler_result = delegation.handler(intent.task)
                # If the handler returns a string, update the intent's task
                if isinstance(handler_result, str):
                    intent.task = handler_result

        return response


def delegate(
    delegations: List[Union[Delegation, str, Dict]],
    messages: Union[str, List[Dict[str, str]]],
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    organization: Optional[str] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    temperature: float = 0,
    mode: Literal["json", "md_json", "tools"] = "md_json",
    verbose: bool = False,
) -> DelegationResponse:
    """
    Delegates the given messages to appropriate delegations or provides a chat response.

    Args:
        delegations (List[Union[Delegation, str, Dict]]): The list of delegations to consider.
        messages (Union[str, List[Dict[str, str]]]): The user's messages to be delegated or responded to.
        model (str): The language model to use. Defaults to "gpt-4o-mini".
        api_key (Optional[str]): The API key for the language model.
        base_url (Optional[str]): The base URL for the API.
        organization (Optional[str]): The organization for the API.
        max_tokens (Optional[int]): Maximum number of tokens for the response.
        max_retries (int): Maximum number of retries for the API call.
        temperature (float): Temperature for response generation.
        verbose (bool): Whether to show verbose output.

    Returns:
        DelegationResponse: A response containing intents for delegation or a chat response.
    """
    delegator = Delegator(delegations)
    return delegator.delegate(
        messages=messages,
        model=model,
        api_key=api_key,
        base_url=base_url,
        organization=organization,
        max_tokens=max_tokens,
        max_retries=max_retries,
        temperature=temperature,
        mode=mode,
        verbose=verbose,
    )
