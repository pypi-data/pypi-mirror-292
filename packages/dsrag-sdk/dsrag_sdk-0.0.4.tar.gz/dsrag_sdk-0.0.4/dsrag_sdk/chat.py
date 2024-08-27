from datetime import datetime
from typing import Optional
from typing_extensions import TypedDict

from dsrag_sdk.main import get_base_url, make_api_call


class UserInput(TypedDict):
    content: str
    timestamp: datetime

class ModelResponse(TypedDict):
    content: str
    timestamp: datetime

class SearchQuery(TypedDict):
    query: str
    kb_id: str

class RankedResult(TypedDict):
    content: str
    metadata: dict

class ChatThreadInteraction(TypedDict):
    user_input: UserInput
    model_response: ModelResponse
    search_queries: list[SearchQuery]
    ranked_results: list[RankedResult]


def create_chat_thread(knowledge_base_ids: list[str] = None, supp_id: str = None, model: str = None, temperature: float = None, system_message: str = None, title: str = None, response_length: str = None, auto_query_guidance: str = None) -> dict:
    """
    Create a chat thread. Chat threads are used to store the state of a conversation.

    Args:
        knowledge_base_ids (list[str], optional): A list of knowledge base IDs to use for the thread. Defaults to None.
        supp_id (str, optional): A supp ID to use for the thread. This will also be used for the ``supp_id`` field in the associated chat request billable events. Defaults to None.
        model (str, optional): The model to use for the thread. Defaults to None.
        temperature (float, optional): The temperature to use for the thread. Defaults to None.
        system_message (str, optional): The system message to use for the thread. Defaults to None.
        auto_query_guidance (str, optional): When we automatically generate queries based on user input, you may want to provide some additional guidance and/or context to the system. Defaults to ''.
        title (str, optional): The title to use for the thread. Defaults to None.
        response_length (str, optional): This parameter determines how long the response is. Defaults to 'medium'. Must be one of 'short', 'medium', or 'long'.

    Note:
        All parameters besides ``supp_id`` are the thread's default options. These options can be overridden when using the ``get_chat_response()`` function.

    Returns:
        dict: A chat thread object.

    References:
        ``POST /chat/threads``
    """
    data = {}

    if supp_id:
        data['supp_id'] = supp_id
    if title:
        data['title'] = title
    if knowledge_base_ids:
        data['kb_ids'] = knowledge_base_ids
    if model:
        data['model'] = model
    if temperature:
        data['temperature'] = temperature
    if system_message:
        data['system_message'] = system_message
    if response_length:
        data['target_output_length'] = response_length
    if auto_query_guidance:
        data['auto_query_guidance'] = auto_query_guidance

    args = {
        'method': 'POST',
        'url': f'{get_base_url()}/chat/threads',
        'json': data,
    }
    return make_api_call(args)


def list_chat_threads(supp_id: str = None):
    """
    List chat threads.

    Args:
        supp_id (str, optional): The supp_id of the thread. Defaults to None.

    Returns:
        dict: A list of chat thread objects.
    
    References:
        ``GET /chat/threads``
    """
    params = {}
    if supp_id:
        params['supp_id'] = supp_id

    args = {
        'method': 'GET',
        'url': f'{get_base_url()}/chat/threads',
        'params': params,
    }
    threads = make_api_call(args)

    return threads


def get_chat_thread(thread_id: str) -> dict:
    """
    Get a chat thread.

    Args:
        thread_id (str): The ID of the thread.

    Returns:
        dict: A chat thread object.

    References:
        ``GET /chat/threads/{thread_id}``
    """
    args = {
        'method': 'GET',
        'url': f'{get_base_url()}/chat/threads/{thread_id}',
    }
    return make_api_call(args)


def update_chat_thread(thread_id: str, knowledge_base_ids: list[str] = None, supp_id: str = None, model: str = None, temperature: float = None, system_message: str = None, title: str = None, response_length: str = None, auto_query_guidance: str = None) -> dict:
    """
    Update a chat thread.

    Args:
        thread_id (str): The ID of the thread.
        knowledge_base_ids (list[str], optional): A list of knowledge base IDs to use for the thread. Defaults to None.
        supp_id (str, optional): A supp ID to use for the thread. This will also be used for the ``supp_id`` field in the associated chat request billable events. Defaults to None.
        model (str, optional): The model to use for the thread. Defaults to None.
        temperature (float, optional): The temperature to use for the thread. Defaults to None.
        system_message (str, optional): The system message to use for the thread. Defaults to None.
        auto_query_guidance (str, optional): When we automatically generate queries based on user input, you may want to provide some additional guidance and/or context to the system. Defaults to None.
        title (str, optional): The title to use for the thread. Defaults to None.
        use_rse (bool, optional): Whether or not to use Relevant Segment Extraction (RSE). Defaults to None.
        segment_length (str, optional): Ignored if `use_rse` is False. This parameter determines how long each result (segment) is. Defaults to None. Must be one of 'very_short', 'short', 'medium', or 'long'.
        response_length (str, optional): This parameter determines how long the response is. Must be one of 'short', 'medium', or 'long'.

    Returns:
        dict: A chat thread object.

    References:
        ``PATCH /chat/threads/{thread_id}``
    """
    data = {}

    if supp_id:
        data['supp_id'] = supp_id
    if title:
        data['title'] = title
    if knowledge_base_ids:
        data['kb_ids'] = knowledge_base_ids
    if model:
        data['model'] = model
    if temperature:
        data['temperature'] = temperature
    if system_message:
        data['system_message'] = system_message
    if response_length:
        data['target_output_length'] = response_length
    if auto_query_guidance:
        data['auto_query_guidance'] = auto_query_guidance

    args = {
        'method': 'PATCH',
        'url': f'{get_base_url()}/chat/threads/{thread_id}',
        'json': data,
    }
    return make_api_call(args)


def delete_chat_thread(thread_id: str) -> dict:
    """
    Delete a chat thread.

    Args:
        thread_id (str): The ID of the thread.

    Returns:
        dict: A chat thread object.

    References:
        ``DELETE /chat/threads/{thread_id}``
    """
    args = {
        'method': 'DELETE',
        'url': f'{get_base_url()}/chat/threads/{thread_id}',
    }
    return make_api_call(args)


def format_chat_interaction(interaction: dict) -> dict:

    ranked_results = []
    for segment in interaction["relevant_segments"]:
        ranked_results.append({
            "content": segment['text'],
            "metadata": {
                "document_id": segment['doc_id'],
                "knowledge_base_id": segment['kb_id'],
                "num_chunks": segment['chunk_end'] - segment['chunk_start'] + 1,
                "result_type": "segment"
            },
        })
    formatted_response = ChatThreadInteraction(
        user_input=interaction.get('user_input', {}),
        model_response=interaction.get('model_response', {}),
        search_queries=interaction.get('search_queries', []),
        ranked_results=ranked_results
    )

    return formatted_response

def get_chat_response(thread_id: str, input: str, knowledge_base_ids: list = None, model: str = None, temperature: float = None, system_message: str = None, response_length: str = None, timeout: int = 90, auto_query_guidance: str = None) -> dict:
    """
    Get a response for a specific chat thread. This endpoint uses a tool we call "Auto Query" to reformulate queries to the knowledge base given the recent chat history as well as user input.

    Note:
        To ensure "Auto Query" works as well as it can, please ensure the knowledge bases you are using have good titles and descriptions. If you are only querying from a single knowledge base, this doesn't matter.

    Args:
        thread_id (str): The ID of the thread.
        input (str): The user's input.
        knowledge_base_ids (list, optional): A list of knowledge base IDs to use for the thread. **These override any default config options defined in the thread itself**. Defaults to None.
        model (str, optional): The model to use for the thread. **This overrides any default config options defined in the thread itself**. Defaults to None.
        temperature (float, optional): The temperature to use for the thread. **This overrides any default config options defined in the thread itself**. Defaults to None.
        system_message (str, optional): The system message to use for the thread. **This overrides any default config options defined in the thread itself**. Defaults to None.
        auto_query_guidance (str, optional): When we automatically generate queries based on user input, you may want to provide some additional guidance and/or context to the system. **This overrides any default config options defined in the thread itself**. Defaults to None.
        response_length (str, optional): This parameter determines how long the response is. Must be one of 'short', 'medium', or 'long'. **This overrides any default config options defined in the thread itself**. Defaults to None.
        
    Returns:
        dict: A chat response object.

    References:
        ``POST /chat/threads/{thread_id}/get_response``
    """
    data = {
        #'async': True,
        'user_input': input,
    }
    if knowledge_base_ids:
        data['knowledge_base_ids'] = knowledge_base_ids
    if model:
        data['model'] = model
    if temperature:
        data['temperature'] = temperature
    if system_message:
        data['system_message'] = system_message
    if auto_query_guidance:
        data['auto_query_guidance'] = auto_query_guidance
    if response_length:
        data['response_length'] = response_length

    args = {
        'method': 'POST',
        'url': f'{get_base_url()}/chat/threads/{thread_id}/get_response',
        'json': data,
    }
    resp = make_api_call(args)
    # Format the response
    formatted_response = format_chat_interaction(resp)

    return formatted_response
    

def list_thread_interactions(thread_id: str, order: str = None) -> dict:
    """
    List interactions for a chat thread.

    Args:
        thread_id (str): The ID of the thread.
        order (str, optional): The order to return the interactions in. Must be `asc` or `desc`. Defaults to `desc`.

    Returns:
        dict: A list of chat interaction objects.

    References:
        ``GET /chat/threads/{thread_id}/interactions``
    """
    params = {}
    if order:
        if order.lower() not in ['asc', 'desc']:
            raise ValueError('`order` parameter must be "asc" or "desc"')
        params['order'] = order.lower()

    args = {
        'method': 'GET',
        'url': f'{get_base_url()}/chat/threads/{thread_id}/interactions',
        'params': params,
    }
    resp = make_api_call(args)

    all_interactions = []
    for interaction in resp:
        all_interactions.append(format_chat_interaction(interaction))

    return all_interactions