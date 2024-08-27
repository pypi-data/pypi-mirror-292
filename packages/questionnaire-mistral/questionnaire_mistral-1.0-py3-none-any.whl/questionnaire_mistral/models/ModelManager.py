import re
from pathlib import Path

import pandas as pd
import torch
import transformers as tf
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
from datasets import Dataset

from ..utils import DocumentLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ModelManager:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.tokenizer = self.setup_tokenizer()
        self.bnb_config = ModelManager.setup_bitsandbytes_parameters()
        self.model = self.from_pretrained()
        self.dataset = pd.DataFrame(columns=['DocName', 'Question', 'Answer'])
        self.__question = None

    @property
    def question(self) -> dict[str, dict[str, str]]:
        """
        :return:
        """
        return self.__question

    @property
    def train_dataset(self) -> dict[str, dict[str]]:
        return Dataset.from_csv('./DatasetQA.csv')

    @question.setter
    def question(self, value):
        """
        Question property\n
        Example::

            question[DocName]['text-generation'] - Generate chapter or summary list
            question[DocName]['calculation-pages'] - Calculate pages on document for generate task count
            question[DocName]['question-answering'] - Generate Questionnaire

        :param dict value: Dict with questions
        :return:
        """
        self.__question = value

    def setup_tokenizer(self):
        """
        Initializes and configures a tokenizer for the model.

        The tokenizer is loaded using the model's name, and the end-of-sequence (eos) token is
        set as the padding token. The padding side is set to 'right'.

        :return: A configured tokenizer instance.
        """
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        return tokenizer

    @classmethod
    def setup_bitsandbytes_parameters(cls):
        """
        Configures parameters for the BitsAndBytes quantization library.

        This setup is designed to load the model in 4-bit precision using the NF4 quantization type.
        The compute dtype is set to float16, and double quantization is disabled.

        :return: A BitsAndBytesConfig instance with the specified settings.
        """
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False
        )
        return bnb_config

    def from_pretrained(self):
        """
        Loads a pre-trained causal language model with quantization settings.

        The model is loaded using the specified model name and quantization configuration.
        The model is then moved to the appropriate device (e.g., CPU or GPU).

        :return: The loaded and quantized model instance.
        """
        model = AutoModelForCausalLM.from_pretrained(self.model_name, quantization_config=self.bnb_config,
                                                     trust_remote_code=True)
        return model

    def print_model_parameters(self):
        """
        Prints the number of trainable and total parameters in the model.

        This function calculates and displays the total number of parameters,
        the number of parameters that are trainable (i.e., require gradients),
        and the percentage of parameters that are trainable.
        """
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"Trainable model parameters: {trainable_params}")
        print(f"Total model parameters: {total_params}")
        print(f"Percentage of trainable model parameters: {100 * trainable_params / total_params:.2f}%")

    @classmethod
    def setup_prompt(cls):
        """
        Creates a prompt template for use in language model tasks.

        The prompt template is structured to handle multiple documents by formatting each
        document's text as a separate contextual block. The template includes placeholders
        for context and question, which are dynamically filled.

        :return: A PromptTemplate instance configured with the specified template.
        """
        template_str = """
        ### [INST]
        Instruction: Answer the question based on your knowledge.
        Here is context to help:

        ### Context:
        {context}

        ### Question:
        {question}
        [/INST]
        """
        return PromptTemplate(
            input_variables=['context', 'question'],
            template=template_str
        )

    @classmethod
    def create_rag_chain(cls, retriever, llm_chain):
        """
        Creates a Retrieval-Augmented Generation (RAG) chain.

        This chain connects a retriever (which fetches relevant context) with a language model
        chain (which generates answers based on the retrieved context). The context is passed
        through the retriever, and the question is passed directly to the language model chain.

        :param retriever: A retriever instance that fetches relevant documents.
        :param llm_chain: A language model chain for generating responses.
        :return: A configured RAG chain.
        """
        return (
                {"context": retriever,
                 "question": RunnablePassthrough()} | llm_chain
        )

    def pipeline(self, task):
        """
        Creates a Hugging Face pipeline for a specific task.

        The pipeline is initialized with the model, tokenizer, and various generation settings
        such as temperature, repetition penalty, and max tokens. The pipeline is set to run
        on the specified device (e.g., CPU or GPU).

        :param task: The NLP task for which the pipeline is created (e.g., 'text-generation').
        :return: A Hugging Face pipeline configured for the specified task.
        """
        return tf.pipeline(task=task,
                           model=self.model,
                           tokenizer=self.tokenizer,
                           temperature=0.2,
                           repetition_penalty=1.1,
                           return_full_text=True,
                           max_new_tokens=1000
                           )

    def rag(self, document):
        """
        Executes the Retrieval-Augmented Generation (RAG) process for a given document.

        This function loads the document, indexes it, creates a prompt, and runs the RAG process
        by passing the document through the retriever and generating responses using the language model.

        :param document: The input document(s) for the RAG process.
        :return: The result of the RAG chain execution.
        """
        loader = DocumentLoader()
        loader.load_multiple(document)
        retriever = DocumentLoader.indexing(loader.documents)
        prompt = ModelManager.setup_prompt()
        mistral_llm = HuggingFacePipeline(pipeline=self.pipeline('text-generation'))
        llm = LLMChain(llm=mistral_llm, prompt=prompt)
        rag = ModelManager.create_rag_chain(retriever, llm)
        return rag

    @classmethod
    def extract_summaries(cls, text: str, document_content: str,
                          chapter_count, chapters):
        """
        Extracts summaries that follow a numbered list format from the given text.

        :param chapter_count:
        :param chapters:
        :param document_content: Document content to extract summaries
        :param text: The text containing the numbered summaries.
        :return: A list of extracted summaries.
        """
        # Regular expression pattern to match numbered summaries
        pattern = r"Summary: ([^\n]+)\n((?:\s+- [^\n]+\n)*)"
        len_chap = 0
        if document_content == 'chapters':
            # Регулярний вираз для розділів і секцій
            pattern = r"Chapter: ([^\n]+)\n((?:\s+- [^\n]+\n)*)"
            # Пошук усіх збігів
            matches = re.findall(pattern, text, re.MULTILINE)

            # Виведення результатів
            for match in matches:
                # chapter_number = match[0]
                chapter_title = match[0]
                sections_text = match[1]
                sections = re.findall(r"- Section: ([^\n]+)", sections_text)
                chapters[chapter_title] = []
                chapter_count += 1
                for section in sections:
                    chapters[chapter_title].append(section)
                    chapter_count += 1
        else:
            # Find all matches
            matches = re.findall(pattern, text, re.MULTILINE)
            # Виведення результатів
            for match in matches:
                # chapter_number = match[0]
                chapter_title = match[0]
                chapters[chapter_title] = []
                chapter_count += 1

    def process_rag_result(self, document, DocName, task, **kwargs):
        if task == 'question-answering':
            task_count = kwargs.pop('task_count')
            chapter = kwargs.pop('chapter')
            question = self.question[DocName][task].format(task_count, chapter)
            result = self.rag(document).invoke(question)
            replaced_result = result.get('text').split('[/INST]')[1].strip()
            del result
            torch.cuda.empty_cache()
            return replaced_result
        result = self.rag(document).invoke(self.question[DocName][task])
        replaced_result = result.get('text').split('[/INST]')[1].strip()
        del result
        torch.cuda.empty_cache()
        return replaced_result

    def __call__(self, document: str, task: str, document_content: str, task_count: int):
        question = None
        DocName = Path(document).name
        chapter_count = 0
        chapters = {}

        def text_generation():
            replaced_result = self.process_rag_result(document, DocName, 'text-generation')
            print(replaced_result)
            ModelManager.extract_summaries(replaced_result, document_content, chapter_count, chapters)
            data = {
                'DocName': DocName,
                'Question': question,
                'Answer': replaced_result
            }
            self.dataset = pd.concat([self.dataset, pd.DataFrame([data])], ignore_index=True)

        def question_answering(task_count: int):
            tasks = 5
            pages_result = self.process_rag_result(document, DocName, 'calculation-pages')
            result_pages = int(pages_result)

            if task_count < tasks:
                task_count = result_pages // chapter_count

            for section in chapters:
                replaced_result = self.process_rag_result(document, DocName, 'question-answering',
                                                          task_count=task_count, chapter=section)
                data = {
                    'DocName': DocName,
                    'Question': question,
                    'Answer': replaced_result
                }
                self.dataset = pd.concat([self.dataset, pd.DataFrame([data])], ignore_index=True)

        if task == 'text-generation':
            text_generation()

        elif task == 'question-answer':
            question_answering(task_count)
        elif task == 'multi-task':
            text_generation()
            question_answering(task_count)

    def save_dataset(self):
        return self.dataset.to_csv(f'DatasetQA.csv')
