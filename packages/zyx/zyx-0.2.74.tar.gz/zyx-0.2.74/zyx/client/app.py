__all__ = ["app", "cli"]

# --- zyx ----------------------------------------------------------------

from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog
from textual.containers import VerticalScroll
from typing import Any, Union, Optional, List, Callable, Literal
from ..types import ClientModeParams
from ..core.ext import BaseModel

COLOR_MAP = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#008000",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "silver": "#C0C0C0",
    "deep_blue": "#001f3f",
    "ocean_blue": "#0074D9",
    "sunset_orange": "#FF851B",
    "twilight_purple": "#6F42C1",
    "forest_green": "#2ECC40",
    "midnight_black": "#111111",
    "crimson_red": "#DC143C",
    "royal_gold": "#FFD700",
    "peach": "#FFDAB9",
    "lavender": "#E6E6FA",
    "teal": "#008080",
    "coral": "#FF7F50",
    "mustard_yellow": "#FFDB58",
    "powder_blue": "#B0E0E6",
    "sage_green": "#B2AC88",
    "blush": "#FF6F61",
    "steel_grey": "#7A8B8B",
    "ice_blue": "#AFEEEE",
    "burnt_sienna": "#E97451",
    "plum": "#DDA0DD",
    "emerald_green": "#50C878",
    "ruby_red": "#E0115F",
    "sapphire_blue": "#0F52BA",
    "amethyst_purple": "#9966CC",
    "topaz_yellow": "#FFC87C",
    "turquoise": "#40E0D0",
    "rose_gold": "#B76E79",
    "olive_green": "#808000",
    "burgundy": "#800020",
    "navy_blue": "#000080",
    "mauve": "#E0B0FF",
    "chartreuse": "#7FFF00",
    "terracotta": "#E2725B",
    "indigo": "#4B0082",
    "periwinkle": "#CCCCFF",
    "maroon": "#800000",
    "cerulean": "#007BA7",
    "ochre": "#CC7722",
    "slate_gray": "#708090",
    "mint_green": "#98FF98",
    "salmon": "#FA8072",
    "tangerine": "#F28500",
    "taupe": "#483C32",
    "aquamarine": "#7FFFD4",
    "mahogany": "#C04000",
    "fuchsia": "#FF00FF",
    "azure": "#007FFF",
    "lilac": "#C8A2C8",
    "vermilion": "#E34234",
    "ivory": "#FFFFF0",
}

ColorName = Literal[
    "black",
    "white",
    "red",
    "green",
    "blue",
    "yellow",
    "cyan",
    "magenta",
    "silver",
    "deep_blue",
    "ocean_blue",
    "sunset_orange",
    "twilight_purple",
    "forest_green",
    "midnight_black",
    "crimson_red",
    "royal_gold",
    "peach",
    "lavender",
    "teal",
    "coral",
    "mustard_yellow",
    "powder_blue",
    "sage_green",
    "blush",
    "steel_grey",
    "ice_blue",
    "burnt_sienna",
    "plum",
    "emerald_green",
    "ruby_red",
    "sapphire_blue",
    "amethyst_purple",
    "topaz_yellow",
    "turquoise",
    "rose_gold",
    "olive_green",
    "burgundy",
    "navy_blue",
    "mauve",
    "chartreuse",
    "terracotta",
    "indigo",
    "periwinkle",
    "maroon",
    "cerulean",
    "ochre",
    "slate_gray",
    "mint_green",
    "salmon",
    "tangerine",
    "taupe",
    "aquamarine",
    "mahogany",
    "fuchsia",
    "azure",
    "lilac",
    "vermilion",
    "ivory",
]


class ChatApp(App):
    def __init__(
        self,
        provider: Optional[Any] = None,
        messages: Union[str, list[dict]] = None,
        model: Optional[str] = "gpt-4o-mini",
        theme: Optional[Literal["light", "dark"]] = "dark",
        tools: Optional[List[Union[Callable, dict, BaseModel]]] = None,
        run_tools: Optional[bool] = True,
        response_model: Optional[BaseModel] = None,
        mode: Optional[ClientModeParams] = "tools",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        top_p: Optional[float] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: Optional[int] = 3,
        verbose: Optional[bool] = False,
        background: Optional[Union[str, ColorName]] = "midnight_black",
        text: Optional[Union[str, ColorName]] = "steel_grey",
        input_field: Optional[Union[str, ColorName]] = "ocean_blue",
        cutoff: Optional[int] = 95,
        **kwargs,
    ):
        try:
            from .main import Client

            super().__init__()
            self.client = Client()
            self.provider = provider
            self.chat_history = (
                self.client.format_messages(messages) if messages else []
            )
            self.model = model
            self.tools = tools
            self.run_tools = run_tools
            self.response_model = response_model
            self.mode = mode
            self.base_url = base_url
            self.api_key = api_key
            self.organization = organization
            self.top_p = top_p
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.max_retries = max_retries
            self.verbose = verbose
            self.background = "#f0f0f0" if theme == "light" else "#1e1e1e"
            self.text = "#000000" if theme == "light" else "#f0f0f0"
            self.input_field = "#f0f0f0" if theme == "light" else "#1e1e1e"
            self.cutoff = cutoff
            self.kwargs = kwargs

        except Exception as e:
            print(f"Error initializing ChatApp: {e}")

    def compose(self) -> ComposeResult:
        try:
            self.CSS = f"""
            ChatApp {{
                background: {self.background};
            }}
            
            RichLog#chat_display {{
                border: round $primary;
                background: {self.background};
                color: {self.text};
                padding: 1 2;
            }}
        
            Input#input_field {{
                border: round $primary;
                background: {self.input_field};
                color: $text;
                padding: 1 2;
            }}
            """

            with VerticalScroll():
                yield RichLog(id="chat_display")
                yield Input(placeholder="Type your message...", id="input_field")
        except Exception as e:
            print(f"Error composing ChatApp: {e}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            from rich.text import Text

            user_message = event.value.strip()
            if user_message:
                self.chat_history.append({"role": "user", "content": user_message})

                user_text = Text()
                user_text.append("User: ", style="bold blue")
                user_text.append(f"{user_message}\n")

                self.query_one("#chat_display", RichLog).write(user_text)

                if self.provider:
                    # Use the provider (Agents instance) to handle the message
                    response = self.provider.run(user_message, **self.kwargs)
                else:
                    # Use the completion client directly
                    response = self.client.completion(
                        messages=self.chat_history,
                        model=self.model,
                        tools=self.tools,
                        run_tools=self.run_tools,
                        response_model=self.response_model,
                        mode=self.mode,
                        base_url=self.base_url,
                        api_key=self.api_key,
                        organization=self.organization,
                        top_p=self.top_p,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        max_retries=self.max_retries,
                        verbose=self.verbose,
                        **self.kwargs,
                    )
                    assistant_reply = response.choices[0].message["content"]
                    self.chat_history.append(
                        {"role": "assistant", "content": assistant_reply}
                    )
                    response = assistant_reply

                assistant_text = Text()
                assistant_text.append("Assistant: ", style="bold green")

                if "\n" in response:
                    for section in response.split("\n"):
                        assistant_text.append(f"{section}\n")
                else:
                    for i in range(0, len(response), self.cutoff):
                        assistant_text.append(f"{response[i:i+self.cutoff]}\n")

                self.query_one("#chat_display", RichLog).write(assistant_text)

                self.query_one("#input_field", Input).value = ""
        except Exception as e:
            print(f"Error processing input: {e}")


def cli(
    provider: Optional[Any] = None,
    messages: Union[str, list[dict]] = None,
    model: Optional[str] = "gpt-4o-mini",
    tools: Optional[List[Union[Callable, dict, BaseModel]]] = None,
    run_tools: Optional[bool] = True,
    response_model: Optional[BaseModel] = None,
    mode: Optional[ClientModeParams] = "tools",
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    organization: Optional[str] = None,
    top_p: Optional[float] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    max_retries: Optional[int] = 3,
    verbose: Optional[bool] = False,
    background: Optional[Union[str, ColorName]] = "midnight_black",
    text: Optional[Union[str, ColorName]] = "steel_grey",
    input_field: Optional[Union[str, ColorName]] = "ocean_blue",
    **kwargs,
):
    """Runs an easy to use CLI interface for a Chatbot, using either an Agents instance or the .completion() function.

    Parameters:
        - provider (Optional[Any]): The provider instance (e.g., Agents) to handle the chat logic.
        - messages (Union[str, list[dict]]): The messages to send to the model.
        - model (Optional[str]): The model to use for completions.
        - tools (Optional[List[Union[Callable, dict, BaseModel]]]): The tools to use for completions.
        - run_tools (Optional[bool]): Whether to run the tools.
        - response_model (Optional[BaseModel]): The Pydantic response model to use for completions.
        - background (Optional[Union[str, ColorName]]): Background color of the app.
        - text (Optional[Union[str, ColorName]]): Text color in the chat display.
        - input_field (Optional[Union[str, ColorName]]): Color of the input field.
        - mode (Optional[str]): The mode to use for completions.
        - base_url (Optional[str]): The base URL for the API.
        - api_key (Optional[str]): The API key to use for the API.
        - organization (Optional[str]): The organization to use for the API.
        - top_p (Optional[float]): The top-p value for completions.
        - temperature (Optional[float]): The temperature value for completions.
        - max_tokens (Optional[int]): The maximum number of tokens for completions.
        - max_retries (Optional[int]): The maximum number of retries for completions.
        - verbose (Optional[bool]): Whether to print verbose output.
    """

    try:
        ChatApp(
            provider=provider,
            messages=messages,
            model=model,
            tools=tools,
            run_tools=run_tools,
            response_model=response_model,
            mode=mode,
            base_url=base_url,
            api_key=api_key,
            organization=organization,
            top_p=top_p,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            verbose=verbose,
            background=background,
            text=text,
            input_field=input_field,
            **kwargs,
        ).run()
    except Exception as e:
        print(f"Error running ChatApp: {e}")


# --- zyx ----------------------------------------------------------------


class CustomChatApp(App):
    def __init__(
        self,
        input_handler: Callable[[str], Any],
        output_handler: Callable[[Any], str],
        background: Optional[Union[str, ColorName]] = "midnight_black",
        text: Optional[Union[str, ColorName]] = "steel_grey",
        input_field: Optional[Union[str, ColorName]] = "ocean_blue",
    ):
        try:
            super().__init__()
            self.input_handler = input_handler
            self.output_handler = output_handler
            self.background = COLOR_MAP.get(background, background)
            self.text = COLOR_MAP.get(text, text)
            self.input_field = COLOR_MAP.get(input_field, input_field)
        except Exception as e:
            print(f"Error initializing CustomChatApp: {e}")

    def compose(self) -> ComposeResult:
        try:
            self.CSS = f"""
            CustomChatApp {{
                background: {self.background};
            }}
            
            RichLog#chat_display {{
                border: round $primary;
                background: #2e2e2e;
                color: {self.text};
                padding: 1 2;
            }}
        
            Input#input_field {{
                border: round $primary;
                background: {self.input_field};
                color: $text;
                padding: 1 2;
            }}
            """
            with VerticalScroll():
                yield RichLog(id="chat_display")
                yield Input(placeholder="Type your message...", id="input_field")
        except Exception as e:
            print(f"Error composing CustomChatApp: {e}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            from rich.text import Text

            user_message = event.value.strip()
            if user_message:
                user_text = Text()
                user_text.append("User: ", style="bold blue")
                user_text.append(f"{user_message}\n")
                self.query_one("#chat_display", RichLog).write(user_text)

                processed_input = self.input_handler(user_message)

                response = self.output_handler(processed_input)

                assistant_text = Text()
                assistant_text.append("Assistant: ", style="bold green")
                assistant_text.append(f"{response}\n")
                self.query_one("#chat_display", RichLog).write(assistant_text)

                self.query_one("#input_field", Input).value = ""
        except Exception as e:
            print(f"Error processing input in CustomChatApp: {e}")


def app(
    input_handler: Callable[[str], Any],
    output_handler: Callable[[Any], str],
    background: Optional[Union[str, ColorName]] = "midnight_black",
    text: Optional[Union[str, ColorName]] = "steel_grey",
    input_field: Optional[Union[str, ColorName]] = "ocean_blue",
):
    """
    Creates and runs a custom chat application with user-defined input and output handlers.

    Parameters:
    - input_handler: A function that takes a string (user input) and returns any type of data.
    - output_handler: A function that takes the result of input_handler and returns a string (assistant's response).
    - background: Background color of the app.
    - text: Text color in the chat display.
    - input_field: Color of the input field.

    Example usage:
    def custom_input_handler(user_input: str) -> dict:
        return {"user_message": user_input}

    def custom_output_handler(processed_input: dict) -> str:
        return f"Received: {processed_input['user_message']}"

    app(custom_input_handler, custom_output_handler)
    """
    try:
        CustomChatApp(
            input_handler=input_handler,
            output_handler=output_handler,
            background=background,
            text=text,
            input_field=input_field,
        ).run()
    except Exception as e:
        print(f"Error running CustomChatApp: {e}")
