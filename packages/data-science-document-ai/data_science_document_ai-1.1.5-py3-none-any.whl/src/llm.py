"""LLM related functions."""
import json

from vertexai.generative_models import GenerationConfig, GenerativeModel

model_gen, model_config = None, None


def initialize_gemini(parameters: dict):
    """Ask the Gemini model a question.

    Args:
        parameters (dict): The parameters to use for the model.

    Returns:
        str: The response from the model.
    """
    if parameters is None:
        parameters = {
            "temperature": 0,
            "maxOutputTokens": 100,
            "top_p": 0.8,
            "top_k": 40,
            "model_id": "gemini-1.5-flash-001",
        }

    # Initialize the model if it is not already initialized
    model_gen = GenerativeModel(model_name=parameters["model_id"])

    # Set the generation configuration
    model_config = GenerationConfig(
        max_output_tokens=parameters["maxOutputTokens"],
        temperature=parameters["temperature"],
        top_p=parameters["top_p"],
        top_k=parameters["top_k"],
    )

    return model_gen, model_config


def ask_gemini(prompt: str, parameters: dict):
    """Ask the Gemini model a question.

    Args:
        prompt (str): The prompt to send to the model.
        parameters (dict): The parameters to use for the model.

    Returns:
        str: The response from the model.
    """
    global model_gen, model_config

    if model_gen is None or model_config is None:
        # Initialize the model
        model_gen, model_config = initialize_gemini(parameters)

    # Generate the response
    model_response = model_gen.generate_content(
        contents=prompt, generation_config=model_config
    )

    return model_response.text


def get_unified_json_genai(prompt, parameters=None):
    """Send a prompt to a Google Cloud AI Platform model and returns the generated json.

    Args:
        prompt (str): The prompt to send to the LLM model.
        parameters (dict, optional): The parameters to use for the model. Defaults to None.

    Returns:
        dict: The generated json from the model.
    """
    # Ask the LLM model
    result = ask_gemini(prompt, parameters)

    # Find the enclosed json in the result
    start_bracket = result.find("{")
    end_bracket = result.rfind("}")
    result = result[start_bracket : (end_bracket + 1)]  # noqa: E203

    return json.loads(result)
