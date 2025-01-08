"""
This class permits to interact with the MistralAI API.
It sends queries to the API and gets responses.
"""

import os
from mistralai import Mistral


class MistralAPI:
    """
    A client for interacting with the MistralAI API.

    Attributes:
        client (Mistral): The Mistral client instance.
        model (str): The model to use for queries.
    """

    def __init__(self, model: str) -> None:
        """
        Initializes the MistralAPI with the given model.

        Args:
            model (str): The model to use for queries.

        Raises:
            ValueError: If the MISTRAL_API_KEY environment variable is not set.
        """
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(
                "No MISTRAL_API_KEY as environment variable, please set it!"
            )
        self.client = Mistral(api_key=api_key)
        self.model = model

    def query(self, query: str, temperature: float = 0.5) -> str:
        """
        Sends a query to the MistralAI API and returns the response.

        Args:
            query (str): The input query to send to the model.
            temperature (float, optional): The temperature parameter for controlling
                                          the randomness of the output. Defaults to 0.5.

        Returns:
            str: The response from the API.
        """
        chat_response = self.client.chat.complete(
            model=self.model,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )
        return chat_response.choices[0].message.content
