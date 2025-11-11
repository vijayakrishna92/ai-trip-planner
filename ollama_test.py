# from langchain_ollama import ChatOllama

# model = ChatOllama(model="gemma3:1b")
# response = model.invoke("Hello, how are you?")
# print(response.content)

from typing import List
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama

def validate_user(user_id: int, address:List) ->bool:
    """validate user using historical addresses.
    Args:
        user_id: (int) the useeer ID
        addresses: previous addresses
        """
    return True

llm = ChatOllama(
    model = "llama3-groq-tool-use:8b",
    temperature = 0,
).bind_tools([validate_user])

result = llm.invoke(
    "could you validate user 123? they previously lived at"
    "123 fake St in boston Ma and 234 houston Tx"
)


print(result)