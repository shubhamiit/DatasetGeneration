from utils import get_filepaths, set_open_api_keys
from constants import ProjectConstants
from templates import (
    PLANNING_SYSTEM_CONTEXT,
    SUMMARIZE_SYSTEM_CONTEXT,
    TASK_SYSTEM_CONTEXT,
    CONVERSATION_TEMPLATE,
    FEEDBACK_SYSTEM_CONTEXT,
)

# import text loader to
from langchain.document_loaders.word_document import Docx2txtLoader

from langchain.chat_models import AzureChatOpenAI
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from termcolor import colored

chat = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name=ProjectConstants.MODEL,
    temperature=ProjectConstants.TEMPERATURE,
    openai_api_base=ProjectConstants.OPENAI_API_BASE,
    openai_api_key=ProjectConstants.OPENAI_API_KEY,
    openai_api_type=ProjectConstants.OPENAI_API_TYPE,
    openai_api_version=ProjectConstants.OPENAI_API_VERSION,
)
from langchain.prompts import ChatPromptTemplate, PromptTemplate


def get_all_chunks(FolderPath):
    filepaths = get_filepaths(FolderPath)
    print("file paths: ", filepaths)
    chunks = []
    for filepath in filepaths:
        loader = Docx2txtLoader(file_path=filepath)
        docstemp = loader.load_and_split()
        chunks = chunks + docstemp
    return chunks


def create_a_vector_db(chunks):
    from langchain.embeddings import OpenAIEmbeddings

    # Define your embedding model
    embeddings_model = OpenAIEmbeddings(
        deployment="text-embedding-ada-002",
        model="text-embedding-ada-002",
        chunk_size=1,
        openai_api_base=ProjectConstants.OPENAI_API_BASE,
        openai_api_key=ProjectConstants.OPENAI_API_KEY,
        openai_api_type=ProjectConstants.OPENAI_API_TYPE,
        openai_api_version=ProjectConstants.OPENAI_API_VERSION,
    )
    db = DocArrayInMemorySearch.from_documents(
        chunks,
        embeddings_model,
    )
    print("vector db created")
    return db


class ChunkIterator(object):
    def __init__(self, data, chunk_size):
        self.data = data
        self.chunk_size = chunk_size
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        chunk = self.data[self.index : self.index + self.chunk_size]
        self.index += self.chunk_size
        return chunk


def get_question_types(chunk):

    """
    Planning system Prompt: The prompt to be used to generate the question type
    """
    # Call the LLM to translate to the style of the customer message

    prompt_template = ChatPromptTemplate.from_template(PLANNING_SYSTEM_CONTEXT)

    messages = prompt_template.format_messages(text=chunk.page_content)
    print(colored("messages: ", "magenta"))
    print(messages)
    response = chat(messages)
    print(colored("response: ", "green"))
    print(response.content)
    return response.content


def get_summary_of_relevant_chunks(chunk, db):
    """
    Get the summary of the relevant chunks
    """
    # Get the relevant chunks
    relevant_chunks = db.similarity_search(chunk.page_content)
    print("length of relevant chunks: ", len(relevant_chunks))
    # combined relevant docs
    qdocs = "".join(
        [relevant_chunks[i].page_content for i in range(len(relevant_chunks))]
    )
    # Get the summary of the relevant chunks
    summary_prompt_template = ChatPromptTemplate.from_template(SUMMARIZE_SYSTEM_CONTEXT)
    messages = summary_prompt_template.format_messages(text=qdocs)

    print(colored("messages: ", "magenta"))
    print(messages)
    response = chat(messages)
    print(colored("response: ", "green"))
    print(response.content)
    return response.content


def generate_QA_pairs_for_chunk(
    chunk, Use_Question_Types=True, Use_Summary=True, db=None, feed_back=None
):

    QuestionsTypes = "OOps! No Questions Types Available, Try Generating without Them"
    Summary = "OOps! No additional context Available, Try Generating without Them"

    if Use_Summary:
        Summary = get_summary_of_relevant_chunks(chunk, db)

    if Use_Question_Types:
        QuestionsTypes = get_question_types(chunk)

    prompt_template = ChatPromptTemplate.from_template(TASK_SYSTEM_CONTEXT)
    messages = prompt_template.format_messages(
        text=chunk.page_content,
        questions_types=QuestionsTypes,
        context=Summary,
        feedback=feed_back,
    )

    print(colored("\nGenerating QA pairs, Thank you for your patience!!\n ", "magenta"))
    # print(messages)
    response = chat(messages)
    print(colored("response: ", "green"))
    print(response.content)
    return response.content


def ask_for_feedback(previous_feedback=None):
    PROMPT = PromptTemplate(
        input_variables=["history", "input"], template=CONVERSATION_TEMPLATE
    )
    conversation = ConversationChain(
        prompt=PROMPT,
        llm=chat,
        verbose=False,
        memory=ConversationBufferMemory(ai_prefix="AI Assistant"),
    )

    print(
        colored(
            "\nHi There! Please enter your feedback or suggestions about the generated question answer pairs, If no feedback, just press: n \n",
            "magenta",
        )
    )

    while True:
        print(colored("Your Response: \n", "blue"))
        userinput = input()
        if userinput == "n":
            break

        import sys
        if userinput == "exit":
            sys.exit()
            
        output = conversation.predict(
            input=userinput,
        )

        print(colored("\nAI Response:\n", "green"))
        print(output, "\n")

    chat_history = str(conversation.memory.chat_memory.messages)

    prompt_template = ChatPromptTemplate.from_template(FEEDBACK_SYSTEM_CONTEXT)
    messages = prompt_template.format_messages(
        chat_history=chat_history, previous_feedback=previous_feedback
    )
    feedback = chat(messages)
    print(
        colored("Thanks for your feedback. Feedback successfully collected.", "green")
    )
    print(feedback.content)

    return feedback.content


if __name__ == "__main__":
    print(colored("\nWelcome to the dataset generation module\n", "yellow"))

    set_open_api_keys()

    # # Get all the chunks
    chunks = get_all_chunks(ProjectConstants.FOLDER_PATH)

    # Create a vector db
    db = create_a_vector_db(chunks)

    feedback = ""
    # chunk_iterator = ChunkIterator(chunks, 1)
    with open(ProjectConstants.OUTPUT_FILE_NAME, "a") as file:
        while True:
            if (
                feedback == "Summary: No feedback provided."
                or feedback == "No feedback provided."
            ):
                break
            for chunk in chunks:
                QApairs_for_the_chunk = generate_QA_pairs_for_chunk(
                    chunk,
                    Use_Question_Types=ProjectConstants.USE_QUESTION_TYPES,
                    Use_Summary=ProjectConstants.USE_RELEVANT_CONTEXT,
                    feed_back=feedback,
                    db=db,
                )
                # Append data to the file
                file.write(QApairs_for_the_chunk)
                file.write("\n")

                # running for one chunk only
                break

            file.write("Next Iteration for QA Pairs")
            feedback = ask_for_feedback(previous_feedback=feedback)

    print(colored("Thank you for using the dataset generation module", "yellow"))
