import ast
import json

from .Endpoints import *
from .prompts import *
from pydantic import BaseModel



class POISchema(BaseModel):
    list_of_interest: list[str]

class TypeOfQuestionSchema(BaseModel):
    list_of_extractable_types_of_questions: list[str]
    reasoning:str

class GeneratedQuestionsSchema(BaseModel):
    generated_questions: list[str]

class RewriteSchema(BaseModel):
    re_written_question: str

class WritingStyleSchema(BaseModel):
    writing_style: str

class NewQuestionSchema(BaseModel):
    new_question: str

class RelevanceFilterSchema(BaseModel):
    Reasoning: str
    Your_Decision: str

class IntelligentSchema(BaseModel):
    Type_of_question: str



class Generator:
    def __init__(self):
        self.llm = OpenAILLM()

    def extract_points_of_interest(self, persona, file_name, passage):
        prompt = extract_user_interest_prompt.format(
            persona=persona, file_name=file_name, passage=passage
        )
        raw_answer = json.loads(self.llm.invoke(prompt, POISchema))
        return raw_answer

    def extract_compatible_question_type(self, interest, types, file_name, passage):
        prompt = extract_compatible_question_type_prompt.format(
            interest="\n".join(interest),
            types="\n".join(types),
            file_name=file_name,
            passage=passage,
        )

        answer = json.loads(self.llm.invoke(prompt, TypeOfQuestionSchema))
        return answer

    def generate_questions(self, file_name, passage, interest, types):
        prompt = extract_questions_prompt.format(
            file_name=file_name, passage=passage, interest=interest, types=types
        )
        try:
            answer = json.loads(self.llm.invoke(prompt, GeneratedQuestionsSchema))["generated_questions"]
            return answer
        except:
            return []

    def conversational_re_write(self, question, file_name, passage):
        prompt = conversational_re_write_prompt.format(
            question=question, file_name=file_name, passage=passage
        )
        try:
            answer = json.loads(self.llm.invoke(prompt, RewriteSchema))
            return answer
        except:
            return {"re_written_question":""}

    def writing_style(self, persona):
        prompt = extract_writing_style.format(persona=persona)
        answer = self.llm.invoke(prompt, WritingStyleSchema)

        return answer

    def persona_rewrite(self, persona, question):
        prompt = persona_rewrite_prompt.format(persona=persona, question=question)

        try:
            answer = self.llm.invoke(prompt, NewQuestionSchema)
            return answer
        except:
            return {"reasoning": "error", "new_question": question}


class Relevance_Filter:
    def __init__(self):
        self.llm = OpenAILLM()

    def execute(self, question, file_name, passage):
        prompt = filter_relevance_prompt.format(
            question=question, file_name=file_name, passage=passage
        )

        answer = json.loads(self.llm.invoke(prompt, RelevanceFilterSchema))

        return answer


class Intelligent_Question_Filter:
    def __init__(self):
        self.llm = OpenAILLM()

    def execute(self, question, file_name, passage):
        prompt = intelligent_question_filter_prompt.format(
            question=question, file_name=file_name, passage=passage
        )
        try:
            answer = json.loads(self.llm.invoke(prompt, IntelligentSchema))
            return answer
        except:
            return {"Type_of_question":"Type_C"}
