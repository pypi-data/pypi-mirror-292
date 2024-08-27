import sys

from setuptools import setup, find_packages

version_range_max = max(sys.version_info[1], 10) + 1

setup(
    name='questionnaire_mistral',
    version="1.0",
    packages=find_packages(where='src'),  # Вказуємо директорію, де шукати пакети
    package_dir={'': 'src'},  # Вказуємо, що пакети знаходяться в директорії `src`
    license="Apache 2.0 License",
    install_requires=[
        "langchain",
        "langchain_community",
        "langchain-huggingface",
        "playwright",
        "html2text",
        "sentence_transformers",
        "faiss-cpu",
        "pandas",
        "peft==0.4.0",
        "trl==0.4.7",
        "pypdf",
        "bitsandbytes",
        "accelerate",
        "datasets"
    ],
    extras_require={
        'torch': [
            "torch",
            "torchvision",
            "torchaudio"
        ]
    },
    dependency_links=[
        "https://download.pytorch.org/whl/cu124"
    ],
    include_package_data=True,
    author='Alex',
    long_description=open('README.rst', "r", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/skillfi/questionnairemistral',
    classifiers=[
                    "Development Status :: 5 - Production/Stable",
                    "Intended Audience :: Developers",
                    "Intended Audience :: Education",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: Apache Software License",
                    "Operating System :: OS Independent",
                    "Topic :: Scientific/Engineering :: Artificial Intelligence",
                    "Programming Language :: Python :: 3",
                ] + [f"Programming Language :: Python :: 3.{i}" for i in range(8, version_range_max)],
    python_requires='>=3.8'
)
