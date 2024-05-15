import os
from dotenv import load_dotenv
from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd
from apps.services.models import FactNewCustomerRegion

# from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


# def get_bot_reply_message(prompt):
#     client = AzureOpenAI(
#         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#         api_version=os.getenv("OPENAI_API_VERSION"),
#         azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     )

#     response = client.chat.completions.create(
#         model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt},
#         ],

#     )


#     return response.choices[0].message.content


def get_bot_reply_message(prompt):
    load_dotenv()
    data = FactNewCustomerRegion.objects.all()
    df = pd.DataFrame(list(data.values()))

    llm = AzureChatOpenAI(
        openai_api_version="2023-12-01-preview", azure_deployment="test-demo"
    )

    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
    tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    tools = [tool]

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        extra_tools=tools,
        verbose=False,
        handle_parsing_errors=True
    )

    try:
        # Assuming `invoke` method returns a dictionary with 'output' key on successful execution
        response = agent.invoke({"input": prompt})["output"]
        if response == "N/A":
            return "I couldn't understand your message. Please try again."
        return response
    except Exception as e:
        # Log the error for debugging purposes if logging is set up in your project
        # logging.error(f"Failed to get bot reply: {str(e)}")
        print(
            f"Error occurred: {str(e)}"
        )  # Optional, for debugging, remove in production
        return "I couldn't understand your message. Please try again."
