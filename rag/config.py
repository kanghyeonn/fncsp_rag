import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv
from google import genai

load_dotenv()

POSTGRES_CONN = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}/"
    f"{os.getenv('POSTGRES_DATABASE')}"
)

EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="nlpai-lab/kure-v1",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True}
)

LLM_A = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    convert_system_message_to_human=True
)

google_search_tool = Tool(
    google_search=GoogleSearch()
)

tool_config = {
    "function_calling_config": {
        "mode" : "ANY"
    },
    "google_search_retrieval": {
        "dynamic_threshold" : "0.8"
    }
}

LLM_B = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    convert_system_message_to_human=True,
    config=GenerateContentConfig(
        tools=[google_search_tool]
    )
)

GEMINI_CLIENT = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)
