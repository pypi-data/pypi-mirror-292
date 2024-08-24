from typing import List
from datasets import Dataset
from sentence_transformers.evaluation import (
    InformationRetrievalEvaluator,
    SequentialEvaluator,
)
from sentence_transformers.util import cos_sim
from creao.core.Diagnosis import RetrieverDiagnoser
from creao.core.demo.rag import RAG
from ragas.metrics import answer_relevancy
from ragas.metrics import faithfulness

from ragas import evaluate as ragas_evaluate
class RagDiagnoser(object):
    """
    This class is used to evaluate the Rag system.
    ### Usage example
    ```python
        from creao.core.evaluator import RagDiagnoser
        evaluator = RagDiagnoser(dataset)
        evaluator.extract_retrieval_errors()
        evaluator.construct_information_retireval_evaluator()
    ```
    """
    def __init__(self, dataset: Dataset, embedding_model_id:str="BAAI/bge-base-en-v1.5"):
        # extract all unique chunk
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
        for item in self.test_dataset:
            question_list.append({"question":item["anchor"], "positive":item["positive"]})
        retriever_diagnoser = RetrieverDiagnoser(self.chunks, question_list, embedding_model_id=embedding_model_id)
        self.retriever_diagnoser = retriever_diagnoser
        self.rag_system = RAG(self.chunks, embedding_model_id=embedding_model_id)

    def get_rag_system(self):
        return self.rag_system
    
    def create_rag_chatbot_demo(self):
        self.rag_system.generate_gradio_interface()

    def generate_rag_diagnosis_report(self, question_limit:int=-1):
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
        if question_limit >= 0:
            question_list = self.test_dataset.select(range(question_limit))
        else:
            question_list = self.test_dataset
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
    


