from typing import Any, Dict, List
from haystack import component, default_from_dict, default_to_dict, Document
from creao.core.Endpoints import OpenAILLM, CreaoLLM
import json
from pydantic import BaseModel


extract_user_interest_prompt = """\
You are given a Persona and a Passage. Your task is to immitate the persona and create a list interesting topics from the given passage.

<Persona>
{persona}
</Persona>

<Passage>
The following information is from a file with the title "{file_name}".

{passage}
</Passage>

Answer format - Generate a json with the following fields
- "list_of_interest": [<fill with 1-5 word desription>]

Use Reflective Thinking: Step back from the problem, take the time for introspection and self-reflection. Examine personal biases, assumptions, and mental models that may influence problem-solving, and being open to learning from past experiences to improve future approaches. Show your thinking before giving an answer.
"""

class POISchema(BaseModel):
    list_of_interest: list[str]

@component
class ExtractPOI:
    def __init__(self, custom_prompt: str = None, service: str = "default", pipeline_id: str = "pipeline_id_default"):
        self.custom_prompt = custom_prompt
        self.pipeline_id = pipeline_id
        self.service = service
        if self.service == "default":
            self.llm = CreaoLLM(bot_name="point of interests extraction assistant", bot_content="You are given a Persona and a Passage. Your task is to adopt the given Persona and reflect deeply on the content of the Passage. Then, create a list of interesting topics from the Passage that align with the Persona's unique perspective and thinking style.Reflective Thinking: Before you generate the final list of topics, pause to examine your assumptions, biases, and the mental models that the Persona might use. Consider how the Persona's perspective influences what they find interesting, and how they prioritize topics. Be open to learning from previous similar tasks and improving the outcome. Explicitly share your reflective thought process before giving the final answer.")
        elif self.service == "openai":
            self.llm = OpenAILLM()

    @component.output_types(documents=List[Document])
    def run(self, personas:List[str], file_name:str, chunk:str):
        #print("extracting points of interest with minimax")
        res_list = []
        for persona in personas:
            prompt = extract_user_interest_prompt.format(
                persona=persona, file_name=file_name, passage=chunk
            )
            if self.service == "default":
                response_json = self.llm.invoke(prompt,{
                        "list_of_interest": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                        }
                    },"ExtractPOI",self.pipeline_id)
                try:
                    raw_answer = json.loads(response_json["reply"])
                except Exception as e:
                    print(f"ExtractPOI json decode error:{e}, response_json:{response_json}")
                    raw_answer = {"list_of_interest":[]}
            elif self.service == "openai":
                try:
                    raw_answer = json.loads(self.llm.invoke(prompt, POISchema))
                except Exception as e:
                    print(f"ExtractPOI json decode error:{e}")
                    raw_answer = {"list_of_interest":[]}
            for interest in raw_answer["list_of_interest"]:
                doc = Document(meta={"persona":persona, "file_name":file_name, "chunk":chunk}, content=interest)
                res_list.append(doc)
        #print("extracting points of interest with minimax done")
        return {"documents":res_list}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this component to a dictionary.

        :returns:
            The serialized component as a dictionary.
        """
        return default_to_dict(
            self,
            custom_prompt=self.custom_prompt,
            service=self.service,
            pipeline_id = self.pipeline_id
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractPOI":
        """
        Deserialize this component from a dictionary.

        :param data:
            The dictionary representation of this component.
        :returns:
            The deserialized component instance.
        """
        return default_from_dict(cls, data)