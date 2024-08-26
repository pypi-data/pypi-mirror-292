from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from langchain_core.runnables import chain, RunnablePassthrough, Runnable
import uuid
import copy
from .agent import graph

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@chain
async def graph_chain(inputs, config):

    if config.get("configurable", {}).get("thread_id") is None:
        config["configurable"]["thread_id"] = str(uuid.uuid4())

    print("\033[34mconfigurable:\033[0m", config["configurable"])
    print("\033[34minputs:\033[0m", inputs)

    # Use the search_kwargs from the config if available, otherwise use default
    search_kwargs = config.get("configurable", {}).get(
        "search_kwargs", {"namespace": "E2j4gGtvsJ2v75THGY0L_DEVELOPMENT", "k": 5}
    )
    config["configurable"]["search_kwargs"] = search_kwargs

    inputs_copy = copy.deepcopy(inputs)

    # Check if 'messages' key exists, if not, fall back to 'undefined'
    messages = inputs_copy.get("messages", inputs_copy.get("undefined", []))

    for message in messages:
        if "type" in message:
            message["role"] = message.pop("type")

    from langchain_core.messages.utils import convert_to_messages

    # try:
    #     messages = convert_to_messages(messages)
    # except ValueError as e:
    #     # Handle the case where the message format is incorrect
    #     print(f"Error converting messages: {e}")
    #     # You might want to add some error handling here, such as:
    #     # - Returning an error response
    #     # - Skipping the problematic messages
    #     # - Using a default message format
    #     # For now, we'll just use an empty list of messages
    #     messages = []

    async for event in graph.astream_events(messages, config, version="v1"):
        kind = event["event"]
        name = event["name"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(
                    "\033[32m" + str(content) + "\033[0m", end="|"
                )  # Green for chat model output
                yield content


server_runnable: Runnable = graph_chain | RunnablePassthrough()

add_routes(
    app,
    graph_chain,
    path="/chat",
    enable_feedback_endpoint=True,
    playground_type="chat",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.server:app", host="0.0.0.0", port=8000, reload=True)
