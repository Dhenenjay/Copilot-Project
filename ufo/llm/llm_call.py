# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from ufo.utils import print_with_color
from ..config.config import load_config
from typing import Tuple


configs = load_config()

def get_completion(messages, agent: str='APP', use_backup_engine: bool=True) -> Tuple[str, float]:
    """
    Get completion for the given messages.

    Args:
        messages (list): List of messages to be used for completion.
        agent (str, optional): Type of agent. Possible values are 'hostagent', 'appagent' or 'BACKUP'.
        use_backup_engine (bool, optional): Flag indicating whether to use the backup engine or not.
        
    Returns:
        tuple: A tuple containing the completion response (str) and the cost (float).

    """
    
    responses, cost = get_completions(messages, agent=agent, use_backup_engine=use_backup_engine, n=1)
    return responses[0], cost


def get_completions(messages, agent: str='APP', use_backup_engine: bool=True, n: int=1) -> Tuple[list, float]:
    """
    Get completions for the given messages.

    Args:
        messages (list): List of messages to be used for completion.
        agent (str, optional): Type of agent. Possible values are 'hostagent', 'appagent' or 'backup'.
        use_backup_engine (bool, optional): Flag indicating whether to use the backup engine or not.
        n (int, optional): Number of completions to generate.

    Returns:
        tuple: A tuple containing the completion responses (list of str) and the cost (float).

    """
    if agent.lower() in ["host", "hostagent"]:
        agent_type = "HOST_AGENT"
    elif agent.lower() in ["app", "appagent"]:
        agent_type = "APP_AGENT"
    elif agent.lower() == "backup":
        agent_type = "BACKUP_AGENT"
    else:
        raise ValueError(f'Agent {agent} not supported')
    
    api_type = configs[agent_type]['API_TYPE']
    try:
        if api_type.lower() in ['openai', 'aoai', 'azure_ad']:
            from .openai import OpenAIService
            response, cost = OpenAIService(configs, agent_type=agent_type).chat_completion(messages, n)
            return response, cost
        elif api_type.lower() in ['qwen']:
            from .qwen import QwenService
            response, cost = QwenService(configs, agent_type=agent_type).chat_completion(messages, n)
            return response, cost
        elif api_type.lower() in ['ollama']:
            from .ollama import OllamaService
            response, cost = OllamaService(configs, agent_type=agent_type).chat_completion(messages, n)
            return response, cost
        else:
            raise ValueError(f'API_TYPE {api_type} not supported')
    except Exception as e:
        if use_backup_engine:
            print_with_color(f"The API request of {agent_type} failed: {e}.", "red")
            print_with_color(f"Switching to use the backup engine...", "yellow")
            return get_completion(messages, agent='backup', use_backup_engine=False, n=n)
        else:
            raise e