from .Generator import Generator
from utils import generate_with_references, inject_references_to_messages
from loguru import logger
import utils as utils
import threading


class Fuser:
    def __init__(self, config):
        """
        Initialize the Fuser with configuration settings.

        Fuser class is responsible for handling the inputs
        Adding appropriate system messages

        Parameters:
        config (dict): Configuration dictionary containing model settings and other parameters.
        """
        self.config = config
        self.generator = None
        self.initialize_fuser()

    def initialize_fuser(self):
        """
        Initialize the generator with the specified model and generation function.
        """
        self.model = self.config["model"]
        # self.top_k_generations = self.config["top_k_generations"]
        self.temperature = self.config["temperature"]
        # output window must be >= than input + output
        self.max_context_length = self.config["max_context_length"]
        self.samples = self.config.get("samples", 1)

        self.fuser = Generator(config=self.config)

        self.length_control = self.config.get("length_control", False)
        print(f"Fuser initialized with model: {self.model}")

    def fuse(self, init_conv, contexts, critiques=None):
        """
        Fuse the generations from multiple models based on the provided query and contexts.

        Parameters:
        init_conv (list of dict): The conversation of the user.
        contexts (list of str): The list of contexts to generate responses from.

        Returns:
        list of str: The top_k_fused_generations fused results.
        """

        assert isinstance(init_conv, list) and isinstance(init_conv[0], dict)
        for item in init_conv:
            assert isinstance(item, dict) and "role" in item and "content" in item
        # assert init_conv[0]["role"] == "user" and len(init_conv[0]["content"]) > 0
        assert isinstance(contexts, list) and all(
            isinstance(context, str) for context in contexts
        )

        if utils.DEBUG:
            logger.debug(f"Length of contexts: {len(contexts)}")
            logger.debug(
                f"Length of critiques: {len(critiques) if critiques else critiques}"
            )
            logger.debug(f"{contexts=}")
            logger.debug(f"{init_conv=}")

        # breakpoint()
        messages = init_conv
        if len(contexts) > 0:
            if utils.DEBUG:
                logger.debug("Injecting references to messages")
            messages = inject_references_to_messages(
                messages, contexts, critiques, length_control=self.length_control
            )

        fuser_generations = []
        for _ in range(self.samples):

            if utils.DEBUG:
                logger.debug(f"Fusion sample {_}")
            output = self.fuser.generate_from_messages(messages)
            if output is not None:
                fuser_generations.extend(output)

        return fuser_generations
