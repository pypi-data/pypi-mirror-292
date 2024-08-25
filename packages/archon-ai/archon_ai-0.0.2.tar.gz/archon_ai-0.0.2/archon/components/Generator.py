from utils import (
    generate_together,
    generate_openai,
    generate_anthropic,
    generate_groq,
    generate_google,
    generate_tgi,
    vllmWrapper,
    clean_messages,
)
import tiktoken


class Generator:
    def __init__(self, config):
        """
        Initialize the Model with configuration settings.

        Parameters:
        config (dict): Configuration dictionary containing model settings and other parameters.
        """
        self.config = config
        self.initialize_model()

    def initialize_model(self):
        """
        Initialize the model and tokenizer with the specified settings.
        """
        self.model_name = self.config["model"]
        self.model_type = self.config["model_type"]
        self.temperature = self.config["temperature"]
        self.max_context_length = self.config["max_context_length"]
        self.samples = self.config.get("samples", 1)

        if self.model_type == "encoder":
            pass
        elif self.model_type == "decoder":
            pass
        elif self.model_type == "Together_API":
            self.generator = generate_together
        elif self.model_type == "OpenAI_API":
            self.generator = generate_openai
        elif self.model_type == "Anthropic_API":
            self.generator = generate_anthropic
        elif self.model_type == "Groq_API":
            self.generator = generate_groq
        elif self.model_type == 'Google_API':
            self.generator = generate_google
        elif self.model_type == "tgi":
            self.generator = generate_tgi
        elif self.model_type == "vLLM":
            self.generator = vllmWrapper(self.model_name)
        else:
            raise ValueError("Invalid model type: %s", self.model_type)

        print(f"Model initialized: {self.model_name}")

    def generate_from_messages(self, messages, temperature=None):
        """
        Generate a response based on the input text.

        Parameters:
        messages to get a response with

        Returns:
        list of str: The generated responses.
        """
        if temperature is None:
            temperature = self.temperature

        # Cap output to model max context length - input context length
        # parsed_content = ' '.join([msg['content'] for msg in clean_messages(messages)])
        # encoding = tiktoken.encoding_for_model("gpt-3.5-turbo") # estimate since not all models have public tokenizers
        # input_token_len = len(encoding.encode(parsed_content, disallowed_special=())) - 5 # buffer for model variance
        # max_tokens = self.max_context_length - input_token_len

        max_tokens = self.max_context_length

        outputs = []
        for _ in range(self.samples):
            output = self.generator(
                self.model_name,
                clean_messages(messages),
                max_tokens,
                temperature,
            )
            if output is not None:
                outputs.append(output)

        return outputs

    def generate_from_query(self, query: str = None, temperature=None):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ]
        return self.generate_from_messages(messages, temperature)
