from typing import Dict
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack import Document
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder



class RetrieverDiagnoser(object):
    """
    This class is used to diagnose the retriever error.

    ### Usage example
    ```python
        from creao.core.Diagnosis import RetrieverDiagnoser
        retriever_diagnoser = RetrieverDiagnoser(chunk, question_with_chunk)
        filtered_res = retriever_diagnoser.detect_retriever_error()
    ```
    """
    def __init__(self, 
                 chunk: list[str], 
                 question_with_chunk:list[Dict[str, str]],
                 embedding_model_id:str="BAAI/bge-base-en-v1.5"):
        """
        :param chunk: The chunk to be stored in the vector database.
        :param question_with_chunk: The question with the corresponding chunk.
        """
        self.question_with_chunk = question_with_chunk
        docs = [Document(content=item, meta={"file_path":"concept.md"}) for item in chunk]
        doc_embedder = SentenceTransformersDocumentEmbedder(model=embedding_model_id)
        doc_embedder.warm_up()
        text_embedder = SentenceTransformersTextEmbedder(model=embedding_model_id)
        text_embedder.warm_up()
        # store all chunk in a vector database
        document_store = InMemoryDocumentStore()
        docs_with_embeddings = doc_embedder.run(docs)
        document_store.write_documents(docs_with_embeddings["documents"])
        # create a retriever from the vector database
        retriever = InMemoryEmbeddingRetriever(document_store)
        # build the retriever pipeline with haystack
        basic_rag_pipeline = Pipeline()
        # Add components to your pipeline
        basic_rag_pipeline.add_component("text_embedder", text_embedder)
        basic_rag_pipeline.add_component("retriever", retriever)

        # Now, connect the components to each other
        basic_rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        self.basic_rag_pipeline = basic_rag_pipeline

    def query_response(self, question:str):
        """
        Query the retriever pipeline and get the response.
        """
        response = self.basic_rag_pipeline.run({"text_embedder": {"text": question}})
        return [item.content for item in response["retriever"]["documents"]]
    

    def detect_retriever_error(self, rank_threshold:int=1):
        """
        Detect the retriever error by comparing the positive response with the query response.
        :param rank_threshold: The threshold to filter the result
        """
        res = []
        for item in self.question_with_chunk:
            temp_res = {}
            positive = item["positive"]
            query_res = self.query_response(item["question"])
            temp_res["item"] = item
            if positive not in query_res:
                temp_res["rank"] = 100
            else:
                temp_res["rank"] = query_res.index(positive)
            res.append(temp_res)
        filtered_res = []
        for item in res:
            if item["rank"] > rank_threshold:
                filtered_res.append(item)
        return filtered_res