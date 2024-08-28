import os
import requests
from dsrag_sdk.main import get_base_url, make_api_call
import PyPDF2
import docx2txt
import uuid

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)

        # Initialize an empty string to store the extracted text
        extracted_text = ""

        # Loop through all the pages in the PDF file
        for page_num in range(len(pdf_reader.pages)):
            # Extract the text from the current page
            page_text = pdf_reader.pages[page_num].extract_text()

            # Add the extracted text to the final text
            extracted_text += page_text

    return extracted_text

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)


def create_document_via_text(knowledge_base_id: str, content: str, title: str = None, description: str = None, supp_id: str = None, auto_context_config: dict = None, document_type: str = "text", doc_id: str = "", file_name: str = "") -> dict:
    """
    Create a document in a knowledge base with raw text. For example, if you are adding Tweets to a knowledge base, you can just pass the text of the Tweet to this method.
    
    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        content (str): The content of the document.
        title (str, optional): The title of the document. Defaults to None.
        link_to_source (str, optional): A link to the source of the document. Defaults to None.
        description (str, optional): The description of the document. Defaults to None.
        supp_id (str, optional): The ID of the document in your system. Defaults to None.
        chunk_header (str, optional): This is used to prepend context to every chunk created from this document.  Must be <= 500 characters. Defaults to None.
        auto_context (bool, optional): Whether to automatically prepend document-level context to every chunk. Cannot be True when `chunk_header` is set. ``NOTE:`` Setting this to `True` will incur an extra charge. Please see our pricing for more details. Defaults to None.
    
    Returns:
        dict: The document object.

    References:
        ``POST /knowledge_bases/{knowledge_base_id}/documents/raw_text``
    """
    if doc_id == "":
        doc_id = str(uuid.uuid4())
    data = {
        'text': content,
        "document_type": document_type,
        "id": doc_id,
        "file_name": file_name
    }
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    if supp_id:
        data['supp_id'] = supp_id
    if auto_context_config is not None:
        data['auto_context_config'] = auto_context_config
    
    args = {
        'method': 'POST',
        'url': f'{get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/raw_text',
        'json': data,
    }
    return make_api_call(args)


def create_document_via_file(knowledge_base_id: str, file_path: str, title: str = None, description: str = None, supp_id: str = None, auto_context_config: dict = None) -> dict:

    # Get the file name from the file path
    file_name = os.path.basename(file_path)
    doc_id = str(uuid.uuid4())

    resp = requests.post(f"{get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/request_signed_file_url", json={"doc_id": doc_id})

    with open(file_path, 'rb') as file:
        response = requests.put(url=resp.json()['url'], data=file)

    # Read the file content now
    if file_path.endswith('.pdf'):
        content = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        content = extract_text_from_docx(file_path)
    else:
        with open(file_path, 'rb') as f:
            content = f.read()

    # If the file was uploaded successfully, create the document
    response = create_document_via_text(
        knowledge_base_id=knowledge_base_id,
        content=content,
        title=title,
        description=description,
        supp_id=supp_id,
        auto_context_config=auto_context_config,
        document_type="file",
        doc_id=doc_id,
        file_name=file_name
    )

    if response.get('id'):
        formatted_response = {
            "id": doc_id,
            "supp_id": supp_id,
            "knowledge_base_id": knowledge_base_id,
            "description": description,
            "file_name": file_name,
            "title": title,
            "document_type": "file",
            "vectorization_status": "CHUNKING_AND_EMBEDDING_STARTED",
        }

        return formatted_response

    return response


def list_documents(knowledge_base_id: str, title_begins_with: str = None, link_to_source: str = None, supp_id: str = None, vectorization_status: str = None) -> list:
    """
    List the documents in a knowledge base.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        title_begins_with (str, optional): A title prefix filter. Defaults to None.
        link_to_source (str, optional): Filter documents by their URL. Defaults to None.
        supp_id (str, optional): Filter documents by ``supp_id``. Defaults to None.

    Returns:
        list: A list of document objects.

    References:
        ``GET /knowledge_bases/{knowledge_base_id}/documents``
    """
    params = {}
    if title_begins_with:
        params['title_begins_with'] = title_begins_with
    if supp_id:
        params['supp_id'] = supp_id
    if vectorization_status:
        params['status'] = vectorization_status
    if link_to_source:
        params['link_to_source'] = link_to_source

    args = {
        'method': 'GET',
        'url': f'{get_base_url()}/knowledge_bases/{knowledge_base_id}/documents',
        'params': params,
    }
    resp = make_api_call(args)
    #documents = resp.get('documents', [])
    """while resp.get('next_page_token'):
        args['params']['next_page_token'] = resp['next_page_token']
        resp = superpowered.make_api_call(args)
        documents.extend(resp.get('documents', []))"""

    return resp


def get_document(knowledge_base_id: str, document_id: str, include_content: bool = False) -> dict:
    """
    Get an individual document from a knowledge base.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        document_id (str): The ID of the document.
        include_content (bool, optional): Whether to include the document content in the response. If you don't plan on displaying the content, setting this parameter to ``False`` could improve latency for large documents. Defaults to True.

    Returns:
        dict: A document object.

    References:
        ``GET /knowledge_bases/{knowledge_base_id}/documents/{document_id}``
    """
    params = {
        'include_content': include_content,
    }
    args = {
        'method': 'GET',
        'url': f'{get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/{document_id}',
        'params': params,
    }
    return make_api_call(args)

def delete_document(knowledge_base_id: str, document_id: str) -> bool:
    """
    Delete a document from a knowledge base.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        document_id (str): The ID of the document.

    Returns:
        bool: Whether the document was successfully deleted.

    References:
        DELETE /knowledge_bases/{knowledge_base_id}/documents/{document_id}
    """

    args = {
        'method': 'DELETE',
        'url': f'{get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/{document_id}',
    }

    
    return make_api_call(args)
