from setuptools import setup, find_packages

setup(
    name="ConceptGraphBuilder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.1.3",
        "numpy>=1.26.2",
        "networkx>=3.2.1",
        "seaborn>=0.13.0",
        "langchain>=0.0.335",
        "pypdf>=3.17.0",
        "pyvis>=0.3.1",
        "tqdm>=4.38",
        "yachalk>=0.1.5",
        "langchain_openai"
    ],
    description="A Python library for extracting concepts using LLMs and building knowledge graphs",
    author="Kshitij Kutumbe",
    author_email="kshitijkutumbe@gmail.com",
    url="https://github.com/kshitijkutumbe/ConceptGraphBuilder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
