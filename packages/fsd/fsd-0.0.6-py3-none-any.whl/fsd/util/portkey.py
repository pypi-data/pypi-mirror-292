from portkey_ai import Portkey

class AIGateway:
    """
    A gateway for interfacing with various AI models provided by Portkey.

    Attributes:
        portkey (Portkey): The Portkey client used to interact with the AI models.
    """

    def __init__(self, type="azure"):
        """
        Initializes the AIGateway with a specific type of AI model.

        Args:
            type (str): The type of AI model to use. Default is "azure".
                        Supported types: "azure", "azure-turbo", "bedrock".
        """
        api_key = "Tf7rBh3ok+wNy+hzHum7dmizdBFh"
        virtual_keys = {
            "azure": "azure-7e4746",
            "azure-turbo": "azure-turbo-14c8a1",
            "bedrock": "bedrock-bfa916"
        }
        self.portkey = Portkey(
            api_key=api_key,
            virtual_key=virtual_keys.get(type),  # Default to 'azure' if type is incorrect
            config="pc-zinley-74e593" # Supports a string config id or a config object
        )

    async def prompt(self, messages, max_tokens=4096, temperature=0.2, top_p=0.1):
        """
        Sends messages to the AI model and receives responses.

        Args:
            messages (list of str): The messages or prompts to send to the AI.
            max_tokens (int): The maximum number of tokens to generate. Default is 4096.
            temperature (float): The randomness of the response. Default is 0.2.
            top_p (float): The nucleus sampling rate. Default is 0.1.

        Returns:
            dict: The AI's response.
        """
        completion = self.portkey.chat.completions.create(
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        return completion
