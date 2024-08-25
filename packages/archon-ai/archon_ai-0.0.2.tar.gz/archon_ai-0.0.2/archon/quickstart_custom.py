from archon import Archon
from components import Component, Generator

# Initialize Archon


class custom_component(Component):
    def __init__(self, config):
        self.config = config

        self.model_name = self.config["model"]
        self.model_type = self.config["model_type"]
        self.temperature = self.config["temperature"]
        self.max_context_length = self.config["max_context_length"]
        self.samples = self.config["samples"]

        self.model = Generator(self.config)

    def generate(self, init_input, prev_outputs, **kwargs):
        """
        Currently, generate will take in these arguements,
        although you are not required to use them if you have **kwargs.
            init_input=init_input,
            prev_outputs=prev_outputs,
            prev_critiques=prev_critiques,
            unit_tests=unit_tests,
            temperature=temperature,

        Output: your output is a list of str outputs to be passed to the next layer
        """

        # This example will fuse and turn the output into a song
        system_prompt = "You have been provided with a set of responses from various open-source models to the latest user query. Your task is to synthesize these responses into a memerable song that best answers the query"

        for i, reference in enumerate(prev_outputs):

            system_prompt += f"\n{i+1}. {reference}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": init_input},
        ]

        fuser_generations = []
        for _ in range(self.samples):
            output = self.model.generate_from_messages(
                messages, temperature=self.temperature
            )
            if output is not None:
                fuser_generations.extend(output)

        return fuser_generations


archon_config = {
    "name": "archon-testing",
    "custom": True,  # set the config to use custom
    "layers": [
        [
            {
                "type": "model",
                "model": "Qwen/Qwen2-72B-Instruct",
                "model_type": "Together_API",
                "temperature": 0.7,
                "max_context_length": 2048,
                "samples": 1,
            }
        ],
        [
            {
                "type": "custom_singer",  # custom type here
                "model": "Qwen/Qwen2-72B-Instruct",
                "model_type": "Together_API",
                "temperature": 0.7,
                "max_context_length": 2048,
                "samples": 1,
            }
        ],
    ],
}

#################################################

archon = Archon(archon_config)

# name has to match config
archon.add_component("custom_singer", custom_component)
archon.initialize()

testing_instruction = [{"role": "user", "content": "How do I make a cake?"}]

response = archon.generate(testing_instruction)

print(response)
