import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

import torch
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
import transformers as tf
from ..utils import DocumentLoader
import pandas as pd

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ModelManager:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.tokenizer = self.setup_tokenizer()
        self.bnb_config = ModelManager.setup_bitsandbytes_parameters()
        self.model = self.from_pretrained()
        self.dataset = pd.DataFrame(columns=['DocName', 'Question', 'Answer'])

    def setup_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        return tokenizer

    @classmethod
    def setup_bitsandbytes_parameters(cls):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False
        )
        return bnb_config

    def from_pretrained(self):
        model = AutoModelForCausalLM.from_pretrained(self.model_name, quantization_config=self.bnb_config,
                                                     trust_remote_code=True).to(device)
        return model

    def print_model_parameters(self):
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"Trainable model parameters: {trainable_params}")
        print(f"Total model parameters: {total_params}")
        print(f"Percentage of trainable model parameters: {100 * trainable_params / total_params:.2f}%")

    @classmethod
    def setup_prompt(cls):
        """
        Creates a prompt template that can handle multiple documents by formatting each document's text
        as a separate contextual block within the template.

        :return: A PromptTemplate instance configured with the dynamically created template.
        """
        # Define the template structure with placeholders for dynamically inserted content
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

        # Create and return the PromptTemplate with filled-in template
        return PromptTemplate(
            input_variables=['context', 'question'],
            template=template_str
        )

    @classmethod
    def create_rag_chain(cls, retriever, llm_chain):
        return (
                {"context": retriever,
                 "question": RunnablePassthrough()} | llm_chain
        )

    def pipeline(self, task):
        return tf.pipeline(task=task,
                           model=self.model,
                           tokenizer=self.tokenizer,
                           temperature=0.2,
                           repetition_penalty=1.1,
                           return_full_text=True,
                           max_new_tokens=1000,
                           device=device)

    def rag(self, document):
        loader = DocumentLoader().load_multiple(document)
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

    def __call__(self, *args, **kwargs):
        document = kwargs.pop('document')
        task = kwargs.pop('task')
        document_content = kwargs.pop('document_content')
        task_count = kwargs.pop('task_count')
        question = None
        DocName = Path(document).name
        chapter_count = 0
        chapters = []

        def generate_question(context_type):
            if context_type == 'chapters':
                return '''Extract and list all headings and subheadings from the given context. 
                Format each chapter and section as follows:
                    Chapter: [Chapter name]
                      - Section: [Section name]'''
            elif context_type == 'summaries':
                return '''Generate few summaries on given context.
                 Format each summary and section as follows:
                 Summary: [Summary name] - [Summary content]'''
            return None

        def process_rag_result(question):
            result = self.rag(document).invoke(question)
            replaced_result = result.get('text').split('[/INST]')[1].strip()
            del result
            torch.cuda.empty_cache()
            return replaced_result

        if task == 'text-generation':
            question = generate_question(document_content)
            replaced_result = process_rag_result(question)
            ModelManager.extract_summaries(replaced_result, document_content, chapter_count, chapters)
            data = {
                'DocName': DocName,
                'Question': question,
                'Answer': replaced_result
            }
            self.dataset = pd.concat([self.dataset, pd.DataFrame([data])], ignore_index=True)

        elif task == 'question-answer':
            tasks = 5
            pages_result = process_rag_result(question)
            result_pages = int(pages_result)

            if task_count < tasks:
                task_count = result_pages // chapter_count

            for section in chapters:
                question = f"""
                   Create {task_count} multiple-choice problems on the topic of "{section}".
                   Each question should have 4 answer options, where 1 answer is correct and the other 3 are random.
                   Provide the correct answer and mark it clearly.
                   Indicate the difficulty level for each question (easy, medium, hard).
                   Ensure there are no repeated questions across different difficulty levels.
                   Divide the problems equally into two categories: theoretical questions and problem-solving questions.
                   Additionally, provide one problem-solving task for independent work (if the topic is mathematics).
                   Include additional information about the given topic to help form the questions.
                   Format for each question:
                   Question: [Your question here]
                   Difficulty: [easy/medium/hard]
                   Category: [theory/problem-solving]
                   A) [Option 1]
                   B) [Option 2]
                   C) [Option 3]
                   D) [Option 4]
                   Correct Answer: [Correct option letter]
                   Independent Problem-Solving Task: [Your problem-solving task here]
                   Overview: [brief overview]
                   Important formulas or theorems: [formulas/theorems]
                   Historical context: [historical context]
                   Applications: [examples of applications]
                   Key principles and methods: [principles/methods]
                   Complex aspects or exceptions: [complex aspects]
                   Important scientists/researchers: [scientists/researchers]"""

                replaced_result = process_rag_result(question)
                data = {
                    'DocName': DocName,
                    'Question': question,
                    'Answer': replaced_result
                }
                self.dataset = pd.concat([self.dataset, pd.DataFrame([data])], ignore_index=True)

        return self.dataset.to_csv(f'{DocName}QA.csv')
