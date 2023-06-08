import os


class ProjectConstants:
    # Azure OpenAI keys
    OPENAI_API_TYPE = "azure"
    OPENAI_API_VERSION = "2023-03-15-preview"
    OPENAI_API_BASE = "https://adhoc-south-central-us.openai.azure.com/"
    OPENAI_API_KEY = "f9f14bee8b8b47b0a25ed553832017ef"
    SERPAPI_API_KEY = "dc8560acaac2ef0a43805d078fff52b94480571b43fe894344318692e963570c"
    DEPLOYMENT = "gpt-4"
    MODEL = "gpt-4"
    TEMPERATURE = 0
    USE_RELEVANT_CONTEXT = False
    USE_QUESTION_TYPES = False
    FOLDER_PATH = "C:\AutoGPT\\aml-copilot\Dataset_Generation\BuildKeyNotes"
    OUTPUT_FILE_NAME = "outputQA.txt"