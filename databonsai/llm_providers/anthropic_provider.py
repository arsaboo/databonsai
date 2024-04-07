import anthropic
from .llm_provider import LLMProvider
import os
from functools import wraps
from tenacity import retry, wait_exponential, stop_after_attempt
from dotenv import load_dotenv

load_dotenv()


class AnthropicProvider(LLMProvider):
    """
    A provider class to interact with Anthropic's Claude API.
    Supports exponential backoff retries, since we'll often deal with large datasets.
    """

    def __init__(
        self,
        api_key: str = None,
        multiplier: int = 1,
        min_wait: int = 1,
        max_wait: int = 60,
        max_tries: int = 10,
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0,
    ):
        """
        Initializes the ClaudeProvider with an API key and retry parameters.

        Parameters:
        api_key (str): Anthropic API key.
        multiplier (int): The multiplier for the exponential backoff in retries.
        min_wait (int): The minimum wait time between retries.
        max_wait (int): The maximum wait time between retries.
        max_tries (int): The maximum number of attempts before giving up.
        temperature (float): The temperature parameter for text generation.
        """
        super().__init__()

        # Provider related configs
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API key not provided.")
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.temperature = temperature
        self.input_tokens = 0
        self.output_tokens = 0

        # Retry related configs
        self.multiplier = multiplier
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.max_tries = max_tries

    def retry_with_exponential_backoff(method):
        """
        Decorator to apply retry logic with exponential backoff to an instance method.
        It captures the 'self' context to access instance attributes for retry configuration.
        """

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            retry_decorator = retry(
                wait=wait_exponential(
                    multiplier=self.multiplier, min=self.min_wait, max=self.max_wait
                ),
                stop=stop_after_attempt(self.max_tries),
            )
            return retry_decorator(method)(self, *args, **kwargs)

        return wrapper

    @retry_with_exponential_backoff
    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens=1000, json=False
    ) -> str:
        """
        Generates a text completion using Anthropic's Claude API, with a given system and user prompt.
        This method is decorated with retry logic to handle temporary failures.

        Parameters:
        system_prompt (str): The system prompt to provide context or instructions for the generation.
        user_prompt (str): The user's prompt, based on which the text completion is generated.

        Returns:
        str: The generated text completion.
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=f"{system_prompt}",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt,
                        }
                    ],
                }
            ],
        )
        self.input_tokens += response.usage.input_tokens
        self.output_tokens += response.usage.output_tokens
        return response.content[0].text
