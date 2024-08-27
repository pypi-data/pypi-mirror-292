MistralAI Questionnaire
=================================

This project provides a toolkit for generating questionnaire from documents: [``txt``, ``docx``, ``pdf``] to ``.csv`` dataset format.

Requirements
------------

Before starting, you need to install the following libraries:
 .. code-block:: python

  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

- ``langchain``
- ``langchain_community``
- ``langchain-huggingface``
- ``playwright``
- ``html2text``
- ``sentence_transformers``
- ``faiss-cpu``
- ``pandas``
- ``peft==0.4.0``
- ``trl==0.4.7``
- ``pypdf``
- ``bitsandbytes``
- ``accelerate``

Description
-----------

ModelManager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class is responsible for loading mistralai model and generating QA.

Constructor
^^^^^^^^^^^

.. code-block:: python

   __init__(self, model_name)

- **model_name**: The path or name of the pre-trained model.


Methods
^^^^^^^

- **setup_tokenizer()**: Loads and configures the tokenizer for the model.
- **setup_bitsandbytes_parameters()**: Configures parameters for bit quantization (BitsAndBytes).
- **from_pretrained()**: Loads the model with pre-trained weights and quantization configuration.
- **print_model_parameters(examples)**: Prints the number of trainable and total parameters of the model.
- **__call__(self, *args, **kwargs)**: The main method for running the generate tasks.

Usage
-----

To start generating QA, you should create an instance of the ``ModelManager`` class and call its ``__call__`` method, passing the necessary arguments.

.. code-block:: python
   from questionnaire_mistral.models import ModelManager
   model = ModelManager(model_name="path_to_model")
   model(document=document, task=task, document_content=document_content, task_count=task_count)

License
-------

The project is distributed under the MIT License.
