from langchain import hub

def get_prompt(prompt_name):
    """Returns public prompts from langchain hub"""
    prompt = hub.pull(prompt_name)
    return prompt

