from typing import Any, Dict, List
from haystack import component, default_from_dict, default_to_dict, Document

from creao.core.Dedup import Dedup

@component
class Deduplication:
    def __init__(self):
        pass

    def warm_up(self):
        """
        Initializes the component.
        """
        if not hasattr(self, "dedup"):
            self.dedup = Dedup()

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        if not hasattr(self, "dedup"):
            raise RuntimeError("The embedding model has not been loaded. Please call warm_up() before running.")
        if len(documents) == 0:
            return {"dedup_list":[]}
        file_name = documents[0].meta["file_name"]
        chunk = documents[0].meta["chunk"]
        input_texts = [doc.content for doc in documents]
        res = self.dedup.execute(input_texts)
        dedup_list = []
        for item in res:
            doc = Document(meta={"file_name":file_name, "chunk":chunk}, content=item)
            dedup_list.append(doc)
        return {"documents":dedup_list}
    
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this component to a dictionary.

        :returns:
            The serialized component as a dictionary.
        """
        return default_to_dict(
            self,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dedup":
        """
        Deserialize this component from a dictionary.

        :param data:
            The dictionary representation of this component.
        :returns:
            The deserialized component instance.
        """
        return default_from_dict(cls, data)