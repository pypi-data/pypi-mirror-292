import pandas as pd
import uuid
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path


class DataLoader:
    def __init__(self, input_dir):
        """
        Initializes the DataLoader with the directory containing the documents.
        """
        self.inputdirectory = Path(input_dir)

    def load_documents(self):
        """
        Loads documents from the specified directory.

        Returns:
            list: A list of loaded documents.
        """
        loader = DirectoryLoader(self.inputdirectory, show_progress=True)
        return loader.load()

    def split_documents(self, documents, chunk_size=1500, chunk_overlap=150):
        """
        Splits the loaded documents into smaller chunks.

        Args:
            documents (list): List of documents to be split.
            chunk_size (int): Size of each chunk in characters.
            chunk_overlap (int): Overlap between consecutive chunks.

        Returns:
            list: A list of text chunks.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        return splitter.split_documents(documents)

    def documents_to_dataframe(self, documents):
        """
        Converts the list of document chunks into a Pandas DataFrame.

        Args:
            documents (list): List of document chunks.

        Returns:
            pd.DataFrame: DataFrame containing the text chunks and metadata.
        """
        rows = []
        for chunk in documents:
            row = {
                "text": chunk.page_content,
                **chunk.metadata,
                "chunk_id": uuid.uuid4().hex,
            }
            rows.append(row)

        return pd.DataFrame(rows)
