import pdb
import re
import ast
from .Generator import Generator


class Unit_Test_Generator:
    def __init__(self, config):
        """
        Initialize the Unit_Test_Generator with configuration settings.

        Parameters:
        config (dict): Configuration dictionary containing model settings and other parameters.
        """
        self.config = config
        self.initialize_unit_test_generator()

    def initialize_unit_test_generator(self):
        """
        Initialize the unit test generator model with the specified settings.
        """
        self.model_name = self.config["model"]
        self.model_type = self.config["model_type"]
        self.temperature = self.config["temperature"]
        self.max_context_length = self.config["max_context_length"]
        self.samples = self.config["samples"]
        self.unit_test_cap = (
            self.config["unit_test_cap"] if "unit_test_cap" in self.config else None
        )

        self.unit_test_generator = Generator(config=self.config)

        print(f"Unit_Test_Generator model initialized: {self.model_name}")

    def generate_unit_tests(self, init_input: list, temperature=None):
        """
        Generate unit tests for a given query.

        Parameters:
        init_input (list of dicts): The conversation.
        temperature (float, optional): Sampling temperature.

        Returns:
        list: A list of generated unit tests.
        """

        # If it is a multi-stage conversation, extract all the user queries from the messages
        query = init_input[-1]["content"]
        query = query.strip()

        assert isinstance(query, str) and len(query) > 0

        ########################################

        if temperature is None:
            temperature = self.temperature

        if self.unit_test_cap is not None and self.unit_test_cap >= 1:
            user_prompt = [
                f"Given the following query, generate a set of {self.unit_test_cap} unit tests that would evaluate the correctness of responses to this query.\n"
            ]
        else:
            user_prompt = [
                f"Given the following query, generate a set of unit tests that would evaluate the correctness of responses to this query.\n"
            ]

        user_prompt.extend(
            [
                # f"Given the following query, generate a set of unit tests that would evaluate the correctness of responses to this query.\n",
                f"- The unit tests should cover various aspects of the query and ensure comprehensive evaluation.\n",
                f"- Each unit test should be clearly stated and should include the expected outcome.\n",
                f"- The unit tests should be in the form of assertions that can be used to validate the correctness of responses to the query.\n",
                f"- The unit test should be formatted like 'The answer mentions...', 'The answer states...', 'The answer uses...', etc. followed by the expected outcome.\n",
                f"- Solely provide the unit tests for the question below. Do not provide any text before or after the list. Only output the unit tests as a list of strings (e.g. ['unit test #1', 'unit test #2', 'unit test #3']).\n\n",
                f"Query: {query}\n",
            ]
        )

        ########################################

        user_prompt = "".join(user_prompt)

        messages = [
            {"role": "system", "content": "You are a unit test generator."},
            {"role": "user", "content": user_prompt},
        ]

        for retry in range(10):
            try:
                output = self.unit_test_generator.generate_from_messages(messages)
                unit_tests = self.parse_unit_tests_output(output[0])
                unit_tests = (
                    unit_tests[: self.unit_test_cap]
                    if self.unit_test_cap is not None
                    else unit_tests
                )
                print(f"Number of Unit Tests: {len(unit_tests)}")
                return unit_tests
            except Exception as e:
                print(f"Error generating unit tests: {e}")
                print(f"Problematic messages: " + messages[-1]["content"])
                print(
                    f"Problematic unit tests: {output[0] if len(output) > 0 else 'NA'}"
                )
                print(f"Retry #{retry + 1}...")

        raise ValueError("Failed to generate unit tests with unit test generator!")

    def parse_unit_tests_output(self, output):
        """
        Parse the output from the unit test generator to extract unit tests.

        Parameters:
        output (str): The raw output from the unit test generator.

        Returns:
        list: A list of generated unit tests.
        """
        # pdb.set_trace()
        if (
            isinstance(output, list)
            and len(output) > 0
            and [isinstance(test, str) for test in output]
        ):
            return output
        else:
            # Remove newlines and extra spaces
            assert isinstance(output, str) and len(output) > 0
            output = " ".join(output.split())

            # Remove the outer square brackets
            if output.startswith("[") and output.endswith("]"):
                output = output[1:-1]

            # Use regex to split the string into individual test cases
            pattern = r"""(?:[^,'"]|"(?:\\.|[^"])*"|'(?:\\.|[^'])*')+"""
            test_cases = re.findall(pattern, output)

            # Process each test case
            unit_tests = []
            for test in test_cases:
                # Remove leading/trailing whitespace and quotes
                test = test.strip().strip("'\"")
                # Unescape quotes
                test = test.replace("\\'", "'").replace('\\"', '"')
                unit_tests.append(test)

            # pdb.set_trace()
            assert (
                isinstance(unit_tests, list)
                and len(unit_tests) > 0
                and [isinstance(test, str) for test in unit_tests]
            )

            return unit_tests
