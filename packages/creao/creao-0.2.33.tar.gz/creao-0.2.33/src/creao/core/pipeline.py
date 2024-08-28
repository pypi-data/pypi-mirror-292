from typing import Dict, Any, List, Union
import networkx as nx
import yaml
from networkx.algorithms.dag import topological_sort
from creao.core.Endpoints import OpenAILLM, CreaoLLM
import json
from pydantic import BaseModel, create_model
from datasets import load_dataset
from jinja2 import Template, Environment, meta

# Utility functions for schema validation
def validate_schema(data: Dict[str, Any], schema: Dict[str, type], instance_name: str, validation_type: str) -> None:
    for key, expected_type in schema.items():
        if key not in data:
            raise ValueError(f"Missing key '{key}' in {validation_type} for '{instance_name}'")
        if not isinstance(data[key], expected_type):
            raise TypeError(f"Key '{key}' in {validation_type} for '{instance_name}' expected to be of type {expected_type}, but got {type(data[key])}")

# Class registry for components
class_registry = {}

def creao_component(cls):
    """
    Registers the class and wraps its `run` method with input/output validation logic.
    """
    original_run_method = getattr(cls, "run", None)
    if original_run_method is None:
        raise ValueError(f"Class {cls.__name__} must have a 'run' method.")

    input_schema = getattr(cls, "input_schema", None)
    output_schema = getattr(cls, "output_schema", None)

    def wrapped_run(self, chained_input, *args, **kwargs):
        # Extract instance_name from kwargs or args
        instance_name = kwargs.pop('instance_name', None)
        validate_schema = kwargs.pop('validate_schema', False)
        if validate_schema: # this logic is for demo purpose, need to adjust this for actual use case
            # Validate the input against the input schema
            if input_schema and chained_input:
                validate_schema(chained_input, input_schema, instance_name, "input")
            
            # Call the original run method
            output = original_run_method(self, chained_input)
            
            # Validate the output against the output schema
            if output_schema:
                validate_schema(output, output_schema, instance_name, "output")
        else:
            output = original_run_method(self, chained_input)
        return output

    # Replace the original run method with the wrapped one
    setattr(cls, "run", wrapped_run)
    
    # Register the class in the registry
    class_registry[cls.__name__] = cls
    return cls


# Updated `Pipeline.run` with instance-specific params merged into `chained_input`
class Pipeline:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_id_counter = 0
        self.node_name_to_id = {}

    def add(self, name: str, class_instance):
        self.node_id_counter += 1
        self.graph.add_node(self.node_id_counter, name=name, data=class_instance)
        self.node_name_to_id[name] = self.node_id_counter

    def connect(self, from_name: str, to_name: str):
        from_node_id = self.node_name_to_id.get(from_name)
        to_node_id = self.node_name_to_id.get(to_name)
        if from_node_id is None or to_node_id is None:
            raise ValueError("One or both of the node names provided do not exist.")
        self.graph.add_edge(from_node_id, to_node_id)

    def run(self, instance_specific_params=None):
        input_configs = self.run_datanode()
        for config in input_configs:
            output = self.run_single(config)
            print("single_output:",output)

    def run_datanode(self):
        #instance_specific_params = instance_specific_params or {}

        if nx.is_directed_acyclic_graph(self.graph):
            execution_order = list(topological_sort(self.graph))
        else:
            raise ValueError("The graph is not a directed acyclic graph (DAG).")
        expanded_inputs = []
        for node_id in execution_order:
            class_instance = self.graph.nodes[node_id]['data']
            node_name = self.graph.nodes[node_id]['name']
            # Run the class instance with the updated chained_input
            output = class_instance.run([{}], instance_name=node_name, validate_schema=False)
            if class_instance.__class__.__name__ == "HFDataComponent":
                dataset_children_map = self.dataset_children_map
                for row_dict in output:
                    expanded_config = Pipeline.expand_run_config(dataset_children_map, row_dict)
                    expanded_inputs.append(expanded_config)
                print("expanded_input:",expanded_inputs[0])
                break
        return expanded_inputs

    def run_single(self, instance_specific_params=None):
        #instance_specific_params = instance_specific_params or {}
        output_store = {}

        if nx.is_directed_acyclic_graph(self.graph):
            execution_order = list(topological_sort(self.graph))
        else:
            raise ValueError("The graph is not a directed acyclic graph (DAG).")
        for node_id in execution_order[1:]:
            class_instance = self.graph.nodes[node_id]['data']
            node_name = self.graph.nodes[node_id]['name']
            predecessors = list(self.graph.predecessors(node_id))
            if self.graph.nodes[predecessors[0]]['data'] in output_store:
                chained_input = output_store[self.graph.nodes[predecessors[0]]['data']] if predecessors else [{}]
            else:
                chained_input = [{}]
            # Merge instance-specific parameters into chained_input
            if instance_specific_params is not None and node_name in instance_specific_params:
                chained_input = instance_specific_params[node_name]["chained_input"]
            if chained_input and hasattr(class_instance, "input_schema"):
                # Validate the chained input against the input schema of the current component
                self.validate_chained_input(chained_input, class_instance.input_schema, node_name)

            # Run the class instance with the updated chained_input
            output = class_instance.run(chained_input, instance_name=node_name, validate_schema=False)
            # Store the output for downstream nodes
            output_store[class_instance] = output
        return output

    def to_dict(self):
        # Convert the pipeline into a dictionary format for serialization
        pipeline_dict = {"nodes": [], "connections": []}

        # Add nodes with their configuration
        for node_id, node_data in self.graph.nodes(data=True):
            class_instance = node_data["data"]
            class_dict = class_instance.__dict__
            if "llm" in class_dict:
                class_dict.pop("llm")
            node_dict = {
                "name": node_data["name"],
                "class": class_instance.__class__.__name__,
                "params": class_dict,  # Serialize the instance parameters
            }
            pipeline_dict["nodes"].append(node_dict)

        # Add connections between nodes
        for from_node, to_node in self.graph.edges():
            from_name = self.graph.nodes[from_node]["name"]
            to_name = self.graph.nodes[to_node]["name"]
            pipeline_dict["connections"].append({"from": from_name, "to": to_name})

        return pipeline_dict

    def save_to_yaml(self, file_path):
        """
        Save the pipeline to a YAML file.
        # TODO: @joshua need to make this function work with load_from_yaml, you could reference from load_from_yaml
        """
        pipeline_dict = self.to_dict()
        with open(file_path, "w") as yaml_file:
            yaml.dump(pipeline_dict, yaml_file)

    @staticmethod
    def from_dict(pipeline_dict, dataset_children_map):
        pipeline = Pipeline()
        pipeline.dataset_children_map = dataset_children_map

        # Reconstruct nodes
        for node in pipeline_dict["nodes"]:
            class_name = node["class"]
            class_instance = class_registry[class_name](**node["params"])
            pipeline.add(node["name"], class_instance)

        # Reconstruct connections
        for connection in pipeline_dict["connections"]:
            pipeline.connect(connection["from"], connection["to"])

        # Manually reinitialize necessary components
        for node_id in pipeline.graph.nodes:
            class_instance = pipeline.graph.nodes[node_id]['data']
            if isinstance(class_instance, LLMComponent):
                # Re-initialize CreaoLLM or OpenAILLM based on the service type
                if class_instance.service == "default":
                    class_instance.llm = CreaoLLM(bot_name="assistant", bot_content="assistant")
                elif class_instance.service == "openai":
                    class_instance.llm = OpenAILLM()

        return pipeline
    
    @staticmethod
    def create_pydantic_model(fields: List[Dict[str, Any]]) -> BaseModel:
        """
        Create a Pydantic model dynamically from a list of dictionaries representing fields.

        Args:
        - fields (List[Dict[str, Any]]): A list where each dict contains 'name' and 'type' keys.

        Returns:
        - A dynamically created Pydantic model class.
        """
        new_json_list = []
        for item in fields:
            if item["type"] == "list[str]":
                item["type"] = List[str]
            elif item["type"] == "str":
                item["type"] = str
        new_json_list.append(item)
        fields = new_json_list
        field_definitions = {field['name']: (field['type'], ...) for field in fields}
        return create_model('JsonBase', **field_definitions)
    
    @staticmethod
    def extract_json_schema(class_instance) -> Dict[str, Any]:
        # Generate the JSON schema
        # Generate the JSON schema
        json_schema = class_instance.schema()
        output_dict = json_schema["properties"]
        
        for key in class_instance.__fields__:
            output_dict[key].pop("title")
        return output_dict

    @staticmethod
    def extract_jinja2_varaibles(template_str:str)->List[str]:
        env = Environment()
        # Parse the template
        parsed_content = env.parse(template_str)
        variables = meta.find_undeclared_variables(parsed_content)
        return list(variables)

    @staticmethod
    def expand_run_config(config_dict, row_dict):
        for dataset_key in config_dict:
            dataset_value = config_dict[dataset_key]
            final_res = {}
            for component_key in dataset_value:
                component_value = dataset_value[component_key] # which is a list
                temp_dict = {}
                for item in component_value:
                    temp_dict[item] = row_dict[item]
                final_res[component_key] = {"chained_input":[temp_dict]}
        return final_res
                
    @staticmethod
    def load_from_rf_json(file_path, rf_dict=None):
        if rf_dict is None:
            with open(file_path, "r") as rf_file:
                rf_dict = json.load(rf_file)
        #then prepare nodes
        nodes = []
        id_to_name_dict = {}
        for node in rf_dict["nodes"]:
            id = node["id"]
            temp_dict = {}
            #prepare params
            params = {}
            node_data = node["data"]
            output_schema = node_data["output_schema"]
            temp_dict["name"] = node_data["label"]
            if "type" not in node:
                temp_dict["class"] = "LLMComponent"
                json_schema = Pipeline.extract_json_schema(Pipeline.create_pydantic_model(output_schema))
                params["json_schema"] = json_schema
            elif node["type"] == "dataNode":
                temp_dict["class"] = "HFDataComponent"
            for key in node_data:
                if key == "output_schema" or key == "label":
                    continue
                params[key] = node_data[key]
            params["component_name"] = node_data["label"]
            temp_dict["params"] = params
            prompt_template  = node_data["prompt_template"] if "prompt_template" in node_data else ""
            id_to_name_dict[id] = {"label":node_data["label"],"class": temp_dict["class"], "prompt_template":prompt_template}
            nodes.append(temp_dict)
        #then prepare connections
        connections = []
        dataset_children_map = {}
        for edge in rf_dict["edges"]:
            from_node = id_to_name_dict[edge["source"]]
            to_node = id_to_name_dict[edge["target"]]
            if id_to_name_dict[edge["source"]]["class"] == "HFDataComponent":
                if from_node["label"] not in dataset_children_map:
                    dataset_children_map[from_node["label"]] = {to_node["label"]:Pipeline.extract_jinja2_varaibles(to_node["prompt_template"])} 
                else:
                    dataset_children_map[from_node["label"]][to_node["label"]] = Pipeline.extract_jinja2_varaibles(to_node["prompt_template"])
            connections.append({"from":from_node["label"], "to":to_node["label"]})
        print("dataset_children_map:",dataset_children_map)
        #res = loaded_pipeline.run({"extract_interest":{"chained_input":[{"persona": "Student", "file_name": "news.txt", "passage": "this is a university rank"}]}})
        final_json = {"nodes":nodes, "connections":connections}
        return Pipeline.from_dict(final_json, dataset_children_map)

    @staticmethod
    def load_from_yaml(file_path):
        # this function is not worked yet, it does not provide a dataset_children_map
        # TODO: @joshua need to fix this, you could reference the load_from_rf_json function
        with open(file_path, "r") as yaml_file:
            pipeline_dict = yaml.safe_load(yaml_file)
        print("pipeline_dict:",pipeline_dict)
        return Pipeline.from_dict(pipeline_dict)

######BaseComponent
extract_poi_prompt_str = """\
You are given a Persona and a Passage. Your task is to immitate the persona and create a list interesting topics from the given passage.

<Persona>
{{persona}}
</Persona>

<Passage>
The following information is from a file with the title "{{file_name}}".

{{passage}}
</Passage>

Answer format - Generate a json with the following fields
- "list_of_interest": [<fill with 1-5 word desription>]

Use Reflective Thinking: Step back from the problem, take the time for introspection and self-reflection. Examine personal biases, assumptions, and mental models that may influence problem-solving, and being open to learning from past experiences to improve future approaches. Show your thinking before giving an answer.
"""

class POISchema(BaseModel):
    list_of_interest: list[str]



def flatten_res_list(res_list: List[Dict[str, Union[str, List[str]]]]) -> List[Dict[str, str]]:
    flattened_list = []

    for entry in res_list:
        # Find keys that have list values
        list_keys = {key: value for key, value in entry.items() if isinstance(value, list)}
        
        if not list_keys:
            # If there are no list values, just add the entry as is
            flattened_list.append(entry)
            continue
        
        # For the first list key, create multiple entries based on the list
        for _, item in enumerate(list_keys.values()):
            for val in item:
                # Create a new dictionary for each element in the list
                new_entry = {key: value for key, value in entry.items() if key not in list_keys}
                new_entry[next(iter(list_keys))] = val
                flattened_list.append(new_entry)

    return flattened_list

@creao_component
class HFDataComponent:
    def __init__(self,hf_dataset_path: str, split: str = 'train', component_name:str="default", **kwargs):
        """
        Initialize HFDataComponent by downloading the dataset from Hugging Face.

        Args:
            hf_path (str): Path to the Hugging Face dataset (e.g., 'imdb').
            split (str): Which split of the dataset to use ('train', 'test', etc.).
        """
        self.hf_path = hf_dataset_path

    def _convert_to_dict_list(self, dataset) -> List[Dict[str, str]]:
        """
        Convert the Hugging Face dataset into a list of dictionaries.

        Returns:
            List[Dict[str, str]]: Processed data.
        """
        return [{key: str(value) for key, value in example.items()} for example in dataset]

    def run(self, chained_input: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Return the downloaded data.

        Args:
            chained_input (List[Dict[str, str]]): Input from previous component.
        
        Returns:
            List[Dict[str, str]]: The dataset as a list of dictionaries.
        """
        print(f"Downloading dataset from {self.hf_path}...")
        dataset = load_dataset(self.hf_path, split="train")
        data = self._convert_to_dict_list(dataset)
        return data


@creao_component
class LLMComponent:
    def __init__(self, prompt_template: str = None, class_instance=None, service: str = "default", pipeline_id: str = "pipeline_id_default",component_name:str="default", **kwargs):
        self.prompt_template = prompt_template
        self.component_name = component_name
        self.pipeline_id = pipeline_id
        json_schema = kwargs.pop('json_schema', None)
        if json_schema is None:
            if class_instance is not None:
                self.json_schema = Pipeline.extract_json_schema(class_instance)
            else:
                self.json_schema = None
        else:
            self.json_schema = json_schema
        self.service = service
        if self.service == "default":
            self.llm = CreaoLLM(bot_name="assistant", bot_content="assistant")
        elif self.service == "openai":
            self.llm = OpenAILLM()

    def run(self, chained_input:List[Dict[str,str]])->List[Dict[str,str]]:
        prompt_template = Template(self.prompt_template)
        #print("extracting points of interest with minimax")
        prompt_list = [prompt_template.render(item) for item in chained_input]
        res_list = []
        for prompt in prompt_list:
            if self.service == "default":
                if self.json_schema is not None:
                    response_json = self.llm.invoke(prompt,self.json_schema,self.component_name,self.pipeline_id)
                else:
                    response_json = self.llm.invoke(prompt,"",self.component_name,self.pipeline_id)
                try:
                    if self.json_schema is not None:
                        raw_answer = json.loads(response_json["reply"]) 
                    else:
                        raw_answer = response_json["reply"]
                except Exception as e:
                    print(f"ExtractPOI json decode error:{e}, response_json:{response_json}")
                    return None
            elif self.service == "openai":
                try:
                    raw_answer = json.loads(self.llm.invoke(prompt))
                except Exception as e:
                    print(f"ExtractPOI json decode error:{e}")
                    return None
            if self.service == "openai":
                res_list.append({"reply":raw_answer})
            else:
                res_list.append(raw_answer)
        if self.json_schema is not None and self.service == "default":
            res_list = flatten_res_list(res_list)
        return res_list
    

#extract_interest = LLMComponent(prompt_template=extract_poi_prompt_str, 
#                            class_instance=POISchema, 
#                            service="default", 
#                            pipeline_id="pipeline_id_default")



#interest_to_persona_prompt_str = """
#You are given a interest. Your task is to identify the persona that would be most interested in each topic.
#<interest>
#{{list_of_interest}}
#</interest>
#"""

#class Persona(BaseModel):
#    persona: str


#hfdataset = HFDataComponent(hf_path="creaoai/lilianweng_blog_url_synthetic_data_abstractive")

#res = hfdataset.run([])
#print(res)


#interest_to_persona = LLMComponent(prompt_template=interest_to_persona_prompt_str, 
#                            class_instance=Persona, 
#                            service="default", 
#                            pipeline_id="pipeline_id_default")

#pipeline = Pipeline()

# Add nodes
#pipeline.add("extract_interest", extract_interest)
#pipeline.add("interest_to_persona", interest_to_persona)
# Define connections
#pipeline.connect("extract_interest", "interest_to_persona")
#pipeline.save_to_yaml("pipeline.yaml")
#loaded_pipeline = Pipeline.load_from_rf_json("rf_json.json")
#res = loaded_pipeline.run()
#print("start to run")
#res = loaded_pipeline.run({"extract_interest":{"chained_input":[{"persona": "Student", "file_name": "news.txt", "passage": "this is a university rank"}]}})
#res = extract_interest.run([{"persona": "Student", "file_name": "news.txt", "passage": "this is a university rank"}])
#print(res)