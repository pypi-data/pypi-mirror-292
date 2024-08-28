from typing import Any, Dict, List, Optional
from creao.core.Endpoints import CreaoLLM
from datasets import Dataset
from sentence_transformers.evaluation import (
    InformationRetrievalEvaluator,
    SequentialEvaluator,
)
from datasets import concatenate_datasets

from sentence_transformers.util import cos_sim
from creao.core.Diagnosis import RetrieverDiagnoser
from creao.core.demo.rag import RAG
from ragas.metrics import answer_relevancy
from ragas.metrics import faithfulness

from ragas import evaluate as ragas_evaluate
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from datasets import load_dataset

class CreaoLangchainEmbedding:
    def __init__(self) -> None:
        self.embedding_model = CreaoLLM()

    def embed_query(self, text: str) -> List[float]:
        return self.embedding_model.invoke(text,"",component_id="embed")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embedding_model.invoke(t,"",component_id="embed") for t in texts]

class CreaoLangchainLLM(LLM):
        
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        creaollm = CreaoLLM()
        response_raw = creaollm.invoke(prompt, "", "ragas_custom_llm")
        return response_raw["reply"]
 
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "CreaoLangchainLLM",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "creao_langchain_llm"

class RagDiagnoser(object):
    """
    The RagDiagnoser class.
    
    # Load the dataset
    dataset = load_dataset("your_dataset")

    # Create an instance of the RagDiagnoser class
    diagnoser = RagDiagnoser(dataset)

    # Generate a diagnosis report
    report = diagnoser.generate_rag_diagnosis_report(full_dataset=True, question_limit=100)

    # Extract retrieval errors
    errors = diagnoser.extract_retrieval_errors(rank_threshold=2)

    # Create a RAG chatbot demo
    diagnoser.create_rag_chatbot_demo()

    # Get all unique chunks
    chunks = diagnoser.get_all_unique_chunks()

    # Construct an information retrieval evaluator
    evaluator = diagnoser.construct_information_retireval_evaluator()
    """
    def __init__(self, dataset: Dataset, embedding_model_id:str="BAAI/bge-base-en-v1.5", service="openai") -> None:
        """
        Initialize the RagDiagnoser.
        :param dataset: The dataset to use for evaluation.
        :param embedding_model_id: The embedding model id to use.
        :param service: The service to use for the LLM.
        """
        self.service = service
        self.train_dataset = dataset["train"]
        self.test_dataset = dataset["test"]
        chunks = set()
        for item in self.test_dataset:
            chunks.add(item["positive"])
        for item in self.train_dataset:
            chunks.add(item["positive"])
        self.chunks = chunks
        print(f"Number of unique chunks: {len(chunks)}")
        question_list = []
        if service == "default":
            self.creao_langchain_llm = CreaoLangchainLLM()
            self.creao_langchain_embedding = CreaoLangchainEmbedding()
        for item in self.test_dataset:
            question_list.append({"question":item["anchor"], "positive":item["positive"]})
        retriever_diagnoser = RetrieverDiagnoser(self.chunks, question_list, embedding_model_id=embedding_model_id)
        self.retriever_diagnoser = retriever_diagnoser
        self.rag_system = RAG(self.chunks, embedding_model_id=embedding_model_id,service=service)

    def get_rag_system(self):
        return self.rag_system
    
    def create_rag_chatbot_demo(self):
        self.rag_system.generate_gradio_interface()

    def generate_rag_diagnosis_report(self, full_dataset=False, question_limit:int=-1):
        """
        Generate a diagnosis report for the RAG system.
        :param full_dataset: Whether to use the full dataset or not.
        :param question_limit: The number of questions to limit the diagnosis to.
        :return: The diagnosis report.
        """
        def get_positive_context_rank(positive: str, contexts:List[str]):
            rank = -1
            if positive in contexts:
                rank = contexts.index(positive)
            return rank
        def get_context_and_answer(question:str):
            response =self.rag_system.query_response(question)
            answer = response["llm"]["replies"][0]
            context = [doc.content for doc in response["retriever"]["documents"]]
            return context, answer
        if full_dataset:
            question_list = concatenate_datasets([self.train_dataset, self.test_dataset])
        else:
            question_list = self.test_dataset
        if question_limit >= 0:
            question_list = question_list.select(range(question_limit))
        questions = []
        answers = []
        contexts = []
        ids = []
        postives = []
        personas = []
        styles = []
        original_questions = []
        positive_ranks = []
        for item in question_list:
            question = item["anchor"]
            postive = item["positive"]
            persona = item["persona"]
            style = item["style"]
            original_question = item["original_question"]
            id = item["id"]
            context, answer = get_context_and_answer(question)
            positive_rank = get_positive_context_rank(postive, context)
            questions.append(question)
            styles.append(style)
            original_questions.append(original_question)
            postives.append(postive)
            positive_ranks.append(positive_rank)
            personas.append(persona)
            answers.append(answer)
            contexts.append(context)
            ids.append(id)
        data_samples = {
            "positive_ranks": positive_ranks,
            "question": questions,
            "answer": answers,
            "positive": postives,
            "persona": personas,
            "contexts": contexts,
            "id": ids,
            "style": styles,
            "original_question": original_questions
        }
        rag_dataset = Dataset.from_dict(data_samples)
        if self.service == "default":
            score = ragas_evaluate(rag_dataset,llm=self.creao_langchain_llm, embeddings=self.creao_langchain_embedding, metrics=[answer_relevancy, faithfulness])
        elif self.service == "openai":
            score = ragas_evaluate(rag_dataset, metrics=[answer_relevancy, faithfulness])
        return score

    def get_all_unique_chunks(self):
        return self.chunks

    def extract_retrieval_errors(self, rank_threshold:int=2):
        # list of dict with question, and positive chunk (ground truth)
        filtered_res = self.retriever_diagnoser.detect_retriever_error(rank_threshold=rank_threshold)
        return filtered_res


    def construct_information_retireval_evaluator(self):
        matryoshka_dimensions = [768, 512, 256, 128, 64]  # Important: large to small\
        # cheat a chunk to dictionary index
        chunk_to_index = {}
        i = 0
        for item in self.chunks:
            chunk_to_index[item] = i
            i += 1
        # constreuct index to chunk
        index_to_chunk = {v: k for k, v in chunk_to_index.items()}
        # test queries for information retrieval evaluation
        queries = dict(zip(self.test_dataset["id"], self.test_dataset["anchor"]))
        # relevant_docs:  Query ID to relevant documents (qid => set([relevant_cids])
        relevant_docs = {}

        for i in range(len(self.test_dataset)):
            chunk = self.test_dataset[i]["positive"]
            id = self.test_dataset[i]["id"]
            relevant_docs[id] = [chunk_to_index[chunk]]

        matryoshka_evaluators = []
        # Iterate over the different dimensions
        for dim in matryoshka_dimensions:
            ir_evaluator = InformationRetrievalEvaluator(
                queries=queries,
                corpus=index_to_chunk,
                relevant_docs=relevant_docs,
                name=f"dim_{dim}",
                truncate_dim=dim,  # Truncate the embeddings to a certain dimension
                score_functions={"cosine": cos_sim},
                write_csv=True
            )
            matryoshka_evaluators.append(ir_evaluator)

        # Create a sequential evaluator
        evaluator = SequentialEvaluator(matryoshka_evaluators)
        return evaluator
    


