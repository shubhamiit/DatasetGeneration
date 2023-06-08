import os

def get_filepaths(folder_path):
    file_paths = []
    for root, directories, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)
    return file_paths

def set_open_api_keys():
    import os
    # Azure OpenAI keys
    print("Setting open api keys")
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
    os.environ["OPENAI_API_BASE"] = "https://adhoc-south-central-us.openai.azure.com/"
    os.environ["OPENAI_API_KEY"] = "open_api_key"
    os.environ["SERPAPI_API_KEY"] = "dc8560acaac2ef0a43805d078fff52b94480571b43fe894344318692e963570c"

