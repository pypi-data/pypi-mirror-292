from archon import Archon

# Initialize Archon

archon_config = {
    "name": "archon-testing",
    "layers": [
        [
            {
                "type": "model",
                "model": "Qwen/Qwen2-72B-Instruct",
                "model_type": "Together_API",
                "checkpoint": "",
                "temperature": 0.7,
                "max_context_length": 2048,
                "samples": 10,
            }
        ],
        [
            {
                "type": "critic",
                "model": "claude-3-5-sonnet-20240620",
                "model_type": "Anthropic_API",
                "checkpoint": "",
                "temperature": 0.7,
                "max_context_length": 8192,
                "samples": 1,
            }
        ],
        [
            {
                "type": "fuser",
                "model": "Qwen/Qwen1.5-110B-Chat",
                "model_type": "Together_API",
                "checkpoint": "",
                "top_k": 1,
                "temperature": 0.7,
                "max_context_length": 2048,
                "samples": 1,
            }
        ],
    ],
}

#################################################

archon = Archon(archon_config)

testing_instruction = [{"role": "user", "content": "How do I make a cake?"}]

response = archon.generate(testing_instruction)

print(response)
