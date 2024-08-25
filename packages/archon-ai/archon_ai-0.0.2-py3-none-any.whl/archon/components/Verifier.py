import re
from .Generator import Generator
import utils as utils
from loguru import logger


class Verifier:
    def __init__(self, config):
        """
        Initialize the Verifier with configuration settings.

        Parameters:
        config (dict): Configuration dictionary containing model settings and other parameters.
        """
        self.config = config
        self.initialize_verifier()

    def initialize_verifier(self):
        """
        Initialize the verifier model and tokenizer with the specified settings.
        """
        self.model_name = self.config["model"]
        self.model_type = self.config["model_type"]
        self.temperature = self.config["temperature"]
        self.max_context_length = self.config["max_context_length"]
        self.samples = self.config["samples"]
        self.batch_num = self.config.get("batch_num", 1)

        self.verifier = Generator(config=self.config)

        print(f"Verifier model initialized: {self.model_name}")

    def parse_list(self, output):
        reasons = " ".join(output.split())
        # left = output.find("[")
        # right = output.rfind("]")
        # reasons = output[left + 1 : right]
        reasons_list = reasons.split("!!!")
        if utils.DEBUG_VERIFIER:
            logger.debug(f"Parsed list: {reasons_list}")

        return reasons_list

    def generate_reasoning(self, query, candidates, temperature=None):
        """
        Generate reasoning for a candidate.

        Parameters:
        query (str): The input query.
        candidates (list): The candidates for reasoning
        temperature (float, optional): Sampling temperature.

        Returns:
        list[str]: The reasonings for the candidate.
        """
        assert isinstance(query, str) and len(query) > 0
        assert isinstance(candidates, list) and len(candidates) > 0

        num = len(candidates)

        if temperature is None:
            temperature = self.temperature

        if num > 1:
            user_prompt = f"I will provide you with {num} responses, each indicated by a numerical identifier []. Provide reasoning for why the response accurately and completely addresses the instruction: {query}.\n"
            for j in range(num):
                user_prompt += f"\n[{j+1}] {candidates[j]}"
            user_prompt += f"Provide the reasoning for the response above based on its relevance, completeness, and accuracy when compared to the instruction."
            user_prompt += f"\n\nInstruction: {query}.\n\n Please provide the responses in the form of a Python list, where each element is the reasoning for a response and seperated by a !!!. It should begin with [ and end with ]."
            user_prompt += f"Do not include any preface or text after the reasoning."
        else:
            user_prompt = f"I will provide you with a response indicated by the identifier 'Response'. Provide reasoning for why the response accurately and completely addresses the instruction: {query}.\n"
            user_prompt += f"\nResponse: {candidates[0]}"
            user_prompt += f"\n\nInstruction: {query}.\n\nProvide the reasoning for the response above based on its relevance, completeness, and accuracy when compared to the instruction. "
            user_prompt += f"Do not include any preface or text after the reasoning."

        messages = [
            {
                "role": "system",
                "content": "You are a reasoning generator for instructions and their responses.",
            },
            {"role": "user", "content": user_prompt},
        ]

        if utils.DEBUG_VERIFIER:
            logger.debug(f"Message being sent to generate reasonings: {messages}")

        for retry in range(10):
            try:
                reasonings = self.verifier.generate_from_messages(messages)

                if utils.DEBUG_VERIFIER:
                    logger.debug(f"Output from generated reasonings: {reasonings[0]}")

                if len(candidates) > 1:
                    reasonings = self.parse_list(reasonings[0])

                assert len(reasonings) == len(
                    candidates
                ), f"reasoning length ({len(reasonings)}) != candidates length ({len(candidates)})"

                return reasonings
            except Exception as e:
                print(f"Error generating reasoning: {e}")
                print(f"Retry #{retry + 1}...")
                continue

        raise ValueError("Failed to generate reasoning with verifier!")

    def extract_verdict(generated_response: str):
        """
        Extract the verdict from the generated response.
        """
        assert (
            "[Correct]" in generated_response or "[Incorrect]" in generated_response
        ), f"Verdict not found in generated response. Found: {generated_response}"
        assert not (
            "[Correct]" in generated_response and "[Incorrect]" in generated_response
        ), f"Both '[Correct]' and '[Incorrect]' found in generated response. Found: {generated_response}"
        # return "[Correct]" if "[Correct]" in generated_response else "[Incorrect]"
        return 1 if "[Correct]" in generated_response else 0

    def verify_query_reasoning_pairs(
        self, query: str, candidates: list[str], reasonings: list[str], temperature=None
    ):
        """
        Verify the query-reasoning pair.

        Parameters:
        query (str): The input query.
        candidate (list[str]): The candidates generation.
        reasoning (list[str]): The reasonings for the candidate.
        temperature (float, optional): Sampling temperature.

        Returns:
        int: 1 if the reasoning is correct, 0 otherwise.
        """
        assert isinstance(query, str) and len(query) > 0
        assert isinstance(candidates, list) and len(candidates) > 0
        assert isinstance(reasonings, list) and len(reasonings) > 0
        assert len(reasonings) == len(candidates)

        if temperature is None:
            temperature = self.temperature

        num = len(reasonings)

        if num > 1:
            user_prompt = f"I will provide you with {num} responses and their reasonings, each indicated by a numerical identifier [].\n"
            user_prompt += f"For each pair, evaluate whether or not the response is correct evaluate whether or not the response is correct given the instruction: {query}.\n"
            for j in range(num):
                user_prompt += (
                    f"\n[{j+1}] Response: {candidates[j]}. Reasoning: {reasonings[j]}"
                )

            user_prompt += f"- In your evaluation, you should consider how the response aligns with the reasoning and query.\n"
            user_prompt += f"- You should also consider whether or not the logic in the reasoning is correct and complete.\n"
            user_prompt += f"- Provide an explanation for your verdict before you return your evaluation. At the end of your explanation, you should finish with your verdict of either '[Correct]' or '[Incorrect]'.\n"
            user_prompt += f"- You must include a verdict with one of these formatted options: '[Correct]' or '[Incorrect]'.\n\n"
            user_prompt += f"\n\nInstruction: {query}.\n\n Please provide the responses in a list, where each element is the verdict for a response and separated by a !!!. It should begin with [ and end with ]."
            user_prompt += f"Do not include any preface or text after the response."
        else:
            user_prompt = [
                f"Given the following query, response, and reasoning, evaluate whether or not the response is correct.\n"
                f"- In your evaluation, you should consider how the response aligns with the reasoning and query.\n"
                f"- You should also consider whether or not the logic in the reasoning is correct and complete.\n"
                f"- Provide an explanation for your verdict before you return your evaluation. At the end of your explanation, you should finish with your verdict of either '[Correct]' or '[Incorrect]'.\n"
                f"- You must include a verdict with one of these formatted options: '[Correct]' or '[Incorrect]'.\n\n"
                f"Query: {query}\n"
                f"Response: {candidates[0]}\n"
                f"Reasoning: {reasonings[0]}\n"
            ]
            user_prompt = "".join(user_prompt)

        messages = [
            {
                "role": "system",
                "content": "You are a verification system for judging responses and their reasoning.",
            },
            {"role": "user", "content": user_prompt},
        ]

        if utils.DEBUG_VERIFIER:
            logger.debug(f"Message being sent to verifier: {messages}")

        for retry in range(10):
            try:
                verdicts = self.verifier.generate_from_messages(messages)
                if utils.DEBUG_VERIFIER:
                    logger.debug(f"Output from verifier: {verdicts}")
                # breakpoint()

                # TODO: im here lol
                if num > 1:
                    verdicts = self.parse_list(verdicts[0])

                verification_result = []
                for verdict in verdicts:
                    verification_result.append(self.parse_verification_output(verdict))

                return verification_result
            except Exception as e:
                print(f"Error verifying query-reasoning pair: {e}")
                print(f"Retry #{retry + 1}...")
                continue

        raise ValueError("Failed to verify query-reasoning pair with verifier!")

    def parse_verification_output(self, output):
        """
        Parse the output from theƒ verification model to extract the verdict.

        Parameters:
        output (str): The raw output from the verification model.

        Returns:
        int: 1 if the reasoning is correct, 0 otherwise.
        """
        assert isinstance(output, str) and len(output) > 0

        if "[Correct]" in output and "[Incorrect]" in output:
            raise ValueError(
                "Both '[Correct]' and '[Incorrect]' found in verification output."
            )
        elif "[Correct]" in output:
            return 1
        elif "[Incorrect]" in output:
            return 0
        else:
            if utils.DEBUG_VERIFIER:
                logger.error(f"Verdict not found in verification output: {output}")
            raise ValueError("Verdict not found in verification output.")

    def filter_responses(self, init_input, candidates, critiques):
        """
        Filter responses based on verification results.

        Parameters:
        init_input (dict): The input conversation.
        candidates (list of str): The list of candidate generations.

        Returns:
        list: A list of verified correct candidate responses.
        """

        query = init_input[-1]["content"]
        query = ""
        for message in init_input:
            if message["role"] == "user":
                query += message["content"] + " "
        query = query.strip()

        assert isinstance(init_input, list) and isinstance(init_input[-1], dict)
        assert isinstance(query, str) and len(query) > 0
        assert isinstance(candidates, list) and len(candidates) > 0

        ####################################

        verified_responses = []
        verified_critiques = []
        incorrect_responses = []

        if critiques is not None:
            assert isinstance(critiques, list) and all(
                isinstance(critique, str) for critique in critiques
            )
            assert len(critiques) == len(candidates)

        for i in range(0, len(candidates), self.batch_num):
            cands = candidates[i : i + self.batch_num]
            try:
                # returns a list
                reasonings = self.generate_reasoning(query, cands)

                if utils.DEBUG_VERIFIER:
                    logger.debug(f"{len(reasonings)=}")

                verification_results = self.verify_query_reasoning_pairs(
                    query, cands, reasonings
                )
                if utils.DEBUG_VERIFIER:
                    logger.debug(f"{len(verification_results)=}")

                for j, cand in enumerate(cands):
                    if verification_results[j] == 1:
                        verified_responses.append(cand)
                        if critiques is not None:
                            verified_critiques.append(critiques[i + j])
                    else:
                        incorrect_responses.append(cand)
            except Exception as e:
                print(f"Error processing candidate for verification: {e}")

        ####################################

        if utils.DEBUG_VERIFIER:
            print(f"Verified Responses Length: {len(verified_responses)}")
            print(f"Incorrect Responses Length: {len(incorrect_responses)}")

        verified_critiques = verified_critiques if len(verified_critiques) > 0 else None
        return verified_responses, verified_critiques
