from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant capable of analyzing large datasets. If you are not capable of analyzing, ask for a preference."),
        ("system", "If the input is not complete, ask the user for specification."),
        ("system", "Don't make PCB combinations up by yourself. Only use the results of the function."),
        ("system", "You are not allowed to call more than one optimization function in response to a single prompt."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)