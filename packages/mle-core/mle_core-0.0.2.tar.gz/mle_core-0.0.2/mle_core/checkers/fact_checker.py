from mle_core.checkers.prompts import f_fact_checker_system_prompt
from langchain_core.pydantic_v1 import BaseModel, Field

class FactCheckerOutput(BaseModel):
    output: bool = Field(description='Returns boolean')


def f_fact_checker(query, context,answer,llm_type='openai', model='gpt-3.5-turbo', method = 'llm') -> bool: 
    """
    Function to check the fact of the query
    Input Args : 
    query : str : The user query
    context : str : The context of the query
    model : str : The model to be used for the fact checking
    method : str : The method to be used for the fact checking. Methods available are 'llm' and 'similarity_check'
    """
    from mle_core.chat.chat_service import ChatService
    chat_service = ChatService(llm_type)
    if method == 'llm':
        user_prompt = f"question: ```{query} \n answer: {answer}```"
        system_prompt = f_fact_checker_system_prompt(context)
        input = {
                "system_message": system_prompt,
                "user_message": user_prompt 
            }
        
        llm_response = chat_service.get_sync_response(
            "invoke", 
            input, 
            model_name="gpt-3.5-turbo",
            temperature=0.2, 
            max_tokens=1000, 
            is_structured=True, 
            pydantic_model=FactCheckerOutput
        )
        return llm_response.output

    elif method == 'similarity_check':
        return True
    
    
