from .LLMInitialization import Initialize as ini
from .LLMModels import LLM_MODELS
from typing import Optional
from pydantic import BaseModel

class Output:
    """
    Provides methods for generating output from various large language models (LLMs).
    
    The `Output` class provides static methods for generating output from different LLM models, including GPT, Claude, and Gemini. Each method takes a prompt as input and returns the generated output.
    
    The `GPT` method uses the OpenAI GPT model to generate output, with options to specify the model, temperature, and maximum tokens. The `Claude` method uses the Anthropic Claude model, with similar options. The `Gemini` method uses the Gemini model, which does not have any additional options.
    
    All methods raise a `ValueError` if the provided model name is invalid or the temperature is out of the valid range.
    """
        
    @staticmethod
    def GPT(prompt, system_prompt: Optional[str] = None, model: str = "gpt-4o-mini-2024-07-18", temperature: float = 0.15, max_tokens: int = 1024, response_format: Optional[BaseModel] = None):
        
        """
            Generates output using the GPT language model.
            
            Args:
                prompt (str): The user prompt to generate output from.
                system_prompt (str, optional): The system prompt to set context. Defaults to None.
                model (str, optional): The name of the GPT model to use. Defaults to "gpt-4o-mini-2024-07-18".
                temperature (float, optional): The temperature value to use for generating output. Must be between 0 and 1. Defaults to 0.15.
                max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 1024.
                response_format (BaseModel, optional): A Pydantic model for structured output. Defaults to None.
            
            Returns:
                Union[str, BaseModel]: The generated output, either as a string or a structured Pydantic model.
            
            Raises:
                ValueError: If the provided model name is invalid or the temperature is out of the valid range.
        """
    
        chatgpt = ini.get_chatgpt()
        
        if model not in LLM_MODELS['openai'].values():
            raise ValueError(f"Invalid model name: {model}. Please use one of the following: {', '.join(LLM_MODELS['openai'].values())}")
        
        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        completion_args = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        if response_format:
            completion_args["response_format"] = response_format
            response = chatgpt.beta.chat.completions.parse(**completion_args)
            return response.choices[0].message.parsed
        else:
            response = chatgpt.chat.completions.create(**completion_args)
            return response.choices[0].message.content

    @staticmethod
    def Claude(prompt, model: str = "claude-3-5-sonnet-20240620", temperature: float = 0, max_tokens: int = 2048):
        """
        Generates output using the Anthropic Claude language model.
        
        Args:
            prompt (str): The input prompt to generate output from.
            model (str, optional): The name of the Claude model to use. Defaults to "claude-3-5-sonnet-20240620".
            temperature (float, optional): The temperature value to use for generating output. Must be between 0 and 1. Defaults to 0.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 2048.
        
        Returns:
            str: The generated output.
        
        Raises:
            ValueError: If the provided model name is invalid or the temperature is out of the valid range.
        """
                
        
        claude = ini.get_claude()
        
        if model not in LLM_MODELS['anthropic'].values():
            raise ValueError(f"Invalid model name: {model}. Please use one of the following: {', '.join(LLM_MODELS['anthropic'].values())}")
        
        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        
        message = claude.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        return message.content[0].text
    
    @staticmethod
    def Gemini(prompt):
        gemini = ini.get_gemini()
        
        return gemini.generate_content(prompt)