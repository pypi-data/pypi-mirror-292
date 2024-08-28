## Overview
This python package is only useful for a custom cloud deployment of dsRAG

## Usage
`pip install dsrag-sdk`

## Setup
You can set the base url that the sdk connects to by running the following:
```python
from dsrag_sdk.main import set_base_url
set_base_url("http://0.0.0.0:8000")
```

## Knowledge bases

`from dsrag_sdk.knowledge_bases import create_knowledge_base, list_knowledge_bases, get_knowledge_base, delete_knowledge_base, update_knowledge_base`

#### Create knowledge base
```python
kb = create_knowledge_base(title="sdk_test_kb", supp_id="test-supp-id")
```

#### List knowledge bases
```python
knowledge_bases = list_knowledge_bases()
```

List with `supp_id` filter
```python
knowledge_bases = list_knowledge_bases(supp_id="test-supp-id")
```

#### Get a knowledge base by id
```python
knowledge_base = get_knowledge_base(knowledge_base_id="test-kb-id")
```

#### Update a knowledge base
```python
knowledge_base = update_knowledge_base(knowledge_base_id="test-kb-id", title="updated-title", supp_id="updated-supp-id")
```

#### Delete a knowledge base
```python
response = delete_knowledge_base(knowledge_base_id="test-kb-id")
```

## Documents

`from dsrag_sdk.documents import create_document_via_text, list_documents, get_document, delete_document`

#### Add a document via text
```python
kb_id = "test-kb-id"
document_text = "This is some test text for document upload"
document = create_document_via_text(kb_id, document_text)
```

#### List documents
```python
documents = list_documents(kb_id)
```

List documents with `supp_id` filter

```python
documents = list_documents(knowledge_base_id="test-kb-id", supp_id="test-supp-id")
```

#### Get document by id
```python
document = get_document(knowledge_base_id="test-kb-id", document_id="test-document-id")
```

#### Delete a document
```python
response = delete_document(knowledge_base_id="test-kb-id", document_id="test-document-id")
```

## Chat

`from dsrag_sdk.chat import create_chat_thread, list_chat_threads, update_chat_thread, get_chat_thread, delete_chat_thread, get_chat_response, list_thread_interactions`

#### Create a chat thread
```python
response = create_chat_thread(knowledge_base_ids=[kb_id])
```

#### List chat threads
```python
chat_threads = list_chat_threads()
```

Filter with `supp_id`

```python
chat_threads = list_chat_threads(supp_id="test-supp-id")
```

#### Get chat thread by id
```python
chat_thread = get_chat_threads(thread_id="test-thread-id")
```

#### Get a chat response
```python
response = get_chat_response(thread_id="test-thread-id", input="What is AGI?")
```

#### Update a chat thread
```python
chat_thread = update_chat_thread(thread_id="test-thread-id", knowledge_base_ids=[kb_id_1, kn_id_2], supp_id="updated-supp-id", model="gpt-4o-mini")
```

#### Delete a chat thread
```python
response = delete_chat_thread(thread_id="test-thread-id")
```