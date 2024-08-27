from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langchain-altero",
    version="0.0.3",
    description="Streamline your AI workflows with langChain-altero, the essential toolkit for seamless LangChain integration.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dicky Umardhani",
    author_email="dicky@alterolab.com",
    url="https://github.com/cakeplabs/langchain-altero",
    install_requires=[
        "langchain",
        "kiwipiepy",
        "konlpy",
        "rank_bm25",
        "pinecone-client[grpc]",
        "pinecone-text",
        "olefile",
        "pdf2image",
    ],
    packages=find_packages(exclude=[]),
    keywords=[
        "langchain",
        "altero",
    ],
    python_requires=">=3.10",
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
