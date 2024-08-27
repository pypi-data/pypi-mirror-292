from typing import List, Sequence, Dict, Union

import numpy as np
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import AsyncChromiumLoader, PyPDFLoader, TextLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer


class DocumentLoader:
    def __init__(self):
        self.documents = []
        self.docs_mapped = {}
        self.loader_classes: Dict[str, Union[AsyncChromiumLoader, PyPDFLoader, TextLoader]] = {
            'html': AsyncChromiumLoader,
            'pdf': PyPDFLoader,
            'txt': TextLoader
        }

    @classmethod
    def convert_html_to_text(cls, docs: List[Document]) -> Sequence[Document]:
        """Converts a list of documents containing HTML to a list containing text."""
        html2text = Html2TextTransformer()
        return html2text.transform_documents(docs)

    def load_document(self, loader_type: str, **kwargs):
        """Loads and converts documents of a given type to text."""
        loader_class = self.loader_classes.get(loader_type)
        if not loader_class:
            raise ValueError(f"Unsupported loader type: {loader_type}")

        argument_key = {
            'html': 'articles',
            'pdf': 'path',
            'txt': 'input'
        }.get(loader_type)

        argument_value = kwargs.get(argument_key)
        if argument_value is None:
            raise ValueError(f"Missing required argument: '{argument_key}' for {loader_type} loader")

        loader_instance = loader_class(argument_value)
        docs = loader_instance.load()

        if loader_type == 'html':
            docs = DocumentLoader.convert_html_to_text(docs)
        self.documents = docs

    @classmethod
    def indexing(cls, documents: Sequence[Document]):
        chunked_documents = cls.split_documents(documents)
        huggingface_embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L12-v2')
        db = FAISS.from_documents(chunked_documents, huggingface_embedding)
        return db.as_retriever()

    def load_multiple(self, url: str):
        """Loads documents from a list of URLs and converts them to text."""
        loader_type = 'html' if url.endswith('.html') else ('pdf' if url.endswith('.pdf') else 'txt')
        self.load_document(loader_type, **{
            'articles' if loader_type == 'html' else 'path' if loader_type == 'pdf' else 'input': url})

    def retriever(self, embedding: HuggingFaceEmbeddings):
        db = FAISS.from_documents(self.documents, embedding)
        return db.as_retriever()

    @classmethod
    def split_documents(cls, docs: Sequence[Document]) -> Sequence:
        """Splits documents into parts for indexing or further processing."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_overlap=0)
        return text_splitter.split_documents(docs)
