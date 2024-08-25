import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class LLMExtractor:
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initializes the LLMExtractor with a specific model.

        Args:
            model (str): The model to use for extraction.
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def graph_prompt(self, input_text, metadata={}):
        """
        Extracts graph-based concepts and relationships from text using an LLM.

        Args:
            input_text (str): The input text to extract from.
            metadata (dict): Additional metadata to attach to each extracted item.

        Returns:
            list: A list of extracted concepts and relationships in JSON format.
        """
        SYS_PROMPT = (
            "You are a network graph maker who extracts terms and their relations from a given context."
            " Your task is to extract the ontology of terms mentioned in the given context."
        )
        inst = (
            "Format your output as a list of json. Each element of the list contains a pair of terms"
            " and the relation between them, like the following: "
            "[{'node_1': 'A concept', 'node_2': 'A related concept', 'edge': 'relationship'}]"
        )

        USER_PROMPT = f"context: ```{input_text}``` {inst} \n\n output: "
        prompt = ChatPromptTemplate.from_messages([("system", SYS_PROMPT), ("human", "{input_text}")])
        response = (prompt | self.llm).invoke({'input_text': USER_PROMPT}).content

        try:
            result = json.loads(response)
            return [dict(item, **metadata) for item in result]
        except:
            print(f"ERROR: {response}")
            return None

    def extract_concepts(self, prompt_text, metadata={}):
        """
        Extracts key concepts from text using an LLM.

        Args:
            prompt_text (str): The text from which to extract concepts.
            metadata (dict): Additional metadata to attach to each extracted item.

        Returns:
            list: A list of extracted concepts in JSON format.
        """
        SYS_PROMPT = (
            "Your task is to extract the key concepts mentioned in the given context."
            " Extract only the most important and atomistic concepts."
        )
        inst = (
            "Format your output as a list of json with the following format:"
            "[{'entity': 'Concept', 'importance': 1-5, 'category': 'Type of Concept'}]"
        )

        USER_PROMPT = f"context: ```{prompt_text}``` {inst} \n\n output: "
        prompt = ChatPromptTemplate.from_messages([("system", SYS_PROMPT), ("human", "{prompt_text}")])
        response = (prompt | self.llm).invoke({'prompt_text': USER_PROMPT}).content

        try:
            result = json.loads(response)
            return [dict(item, **metadata) for item in result]
        except:
            print(f"ERROR: {response}")
            return None
