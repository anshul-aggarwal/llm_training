import os
import tempfile

import openai
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore

load_dotenv("../.env")

openai.api_key = os.environ["OPENAI_API_KEY"]
openai.organization = os.getenv("OPENAI_ORGANIZATION")


def initialise():
    # Load documents in langchain
    loader = DirectoryLoader(
        "../data/movies/", glob="*.txt", show_progress=True
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=40,
        length_function=len,
        add_start_index=True,
    )

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    persist_path = os.path.join(tempfile.gettempdir(), "union.parquet")

    vector_store = SKLearnVectorStore(
        embedding=embeddings,
        persist_path=persist_path,
        serializer="parquet",
    )

    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vector_store,
        docstore=store,
        child_splitter=text_splitter,
    )

    retriever.add_documents(docs, None)

    return retriever


def query_llm(messages, model="gpt-3.5-turbo", temperature=1):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content
