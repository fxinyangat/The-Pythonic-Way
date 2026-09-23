# tools/registry.py
#
# AGENTIC CONCEPT #1 — what "tool calling" actually is at the API level:
# You send the model your normal conversation PLUS a list of tool
# *definitions* (name, description, JSON-schema-shaped parameters). The model
# can respond with either normal text, OR a structured "call this tool with
# these arguments" message instead of text. The model never executes
# anything itself — it only ever emits text or JSON. YOUR code is
# responsible for:
#   1. advertising what tools exist               -> get_schemas()
#   2. actually running the requested function     -> execute_tool()
#   3. feeding the result back in as a new message so the model can keep
#      going (that last part is orchestrator.py's job, not this file's)
#
# This file is deliberately RAG-agnostic — it knows nothing about vector
# stores, embeddings, or rerankers. It's a generic "expose a python function
# to an LLM" mechanism. rag_tools.py (next phase) is what registers actual
# RAG capabilities into it.
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError


@dataclass
class Tool:
    name: str
    description: str
    parameters: type[BaseModel]  # the CONTRACT for this tool's arguments
    func: Callable[..., Any]
    category: str = "general"  # lets callers request a subset, e.g. ["rag"]


# name -> Tool. This is the dispatch table: the model refers to tools by
# *name* (a string) in its structured response, so something has to map that
# string back to an actual python function. Without this you'd need an
# if/elif chain keyed on tool name, hardcoded wherever tools get called.
TOOL_REGISTRY: dict[str, Tool] = {}


def tool(
    name: str,
    description: str,
    parameters: type[BaseModel],
    category: str = "general",
):
    """
    Decorator that registers a function as an LLM-callable tool.

    AGENTIC CONCEPT #2 — why Pydantic, why a schema at all:
    The model needs a machine-readable contract of what arguments a tool
    accepts, so it can produce syntactically valid arguments for it. That
    contract is JSON Schema — the same standard OpenAPI/form validation use,
    reused by every LLM provider's tool-calling API rather than inventing a
    new format. Pydantic models are the Python-native way to describe "shape
    of structured data": define it once with normal type hints, and get BOTH
    the JSON schema to hand the model (`parameters.model_json_schema()`) AND
    a validator to check the model's *actual* returned arguments against that
    exact same shape (`parameters.model_validate(...)`). Hand-writing a JSON
    schema separately from your argument-parsing code risks the two silently
    drifting apart (schema says a field is required, parsing code doesn't
    check) — deriving both from one model makes that bug class impossible.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        TOOL_REGISTRY[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            func=func,
            category=category,
        )
        return func

    return decorator


def get_schemas(categories: list[str] | None = None) -> list[dict[str, Any]]:
    """
    Returns tool definitions in OpenAI's function-calling schema shape:
        {"type": "function", "function": {"name", "description", "parameters"}}

    `categories` filters by the `category` a tool was registered under (e.g.
    `get_schemas(["rag"])`) — so an agent can be handed only a subset of its
    available capabilities for a given task instead of everything at once.

    TOOL_REGISTRY itself stores schema data in a provider-NEUTRAL way (a
    Pydantic model, not a pre-formatted dict). This function is the one place
    that shapes it for OpenAI specifically. Anthropic's tool schema shape is
    different (`{"name", "description", "input_schema"}`); once providers/
    exists, a second formatter function can read the same TOOL_REGISTRY
    without this file needing to change at all.
    """
    schemas = []
    for registered_tool in TOOL_REGISTRY.values():
        if categories is not None and registered_tool.category not in categories:
            continue
        schemas.append(
            {
                "type": "function",
                "function": {
                    "name": registered_tool.name,
                    "description": registered_tool.description,
                    "parameters": registered_tool.parameters.model_json_schema(),
                },
            }
        )
    return schemas


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """
    Looks up a tool by name, validates `arguments` against its parameters
    model, runs it, and returns a string result.

    AGENTIC CONCEPT #3 — why this must never raise:
    Whatever this returns becomes a "tool" role message sent back to the
    model as part of the conversation — the model literally cannot continue
    the tool-calling exchange without one. `arguments` came from the model's
    own (sometimes wrong) output, so treat it as untrusted input: a
    malformed or missing field should become an error message the model can
    read and react to (e.g. retry with corrected arguments), not a Python
    exception that kills the whole agent turn.
    """
    registered_tool = TOOL_REGISTRY.get(name)
    if registered_tool is None:
        return f"Error: no tool registered with name '{name}'. Available tools are {list(TOOL_REGISTRY)}"

    try:
        validated_args = registered_tool.parameters.model_validate(arguments)
    except ValidationError as exc:
        return f"Error: invalid arguments for tool '{name}': {exc}"

    try:
        return registered_tool.func(**validated_args.model_dump())
    except Exception as exc:
        return f"Error: tool '{name}' failed: {exc}"


if __name__ == "__main__":
    # A tiny dummy tool with NO real dependencies, just to prove the
    # mechanism end to end before rag_tools.py plugs real capabilities in.
    import json

    class EchoParams(BaseModel):
        message: str

    @tool(
        name="echo",
        description="Repeats back whatever message you send it.",
        parameters=EchoParams,
        category="demo",
    )
    
    
    def echo(message: str) -> str:
        return f"you said: {message}"

    
    
    class GreetingParams(BaseModel):
        msg: str
        name: str
        
    @tool(
        name="greets",
        description="Greets the person you specify it.",
        parameters=GreetingParams,
        category="greetings",    
    )
    def greet(msg: str, name:str):
        return f"Greeting Message: {msg}, for: {name}"
    
    print("Registered tools:", list(TOOL_REGISTRY))
    
    print("\n--- schema sent to the LLM ---")
    print(json.dumps(get_schemas(["demo","greetings"]), indent=2))

    print("\n--- valid call ---")
    print(execute_tool("echo", {"message": "hello agent"}))
    print(execute_tool("greets", {"msg": "hello from greets tool", "name": "Peter"}))

    print("\n--- missing required field (simulates a bad LLM tool call) ---")
    print(execute_tool("echo", {}))
    print(execute_tool("greets", {"msgs": "hello from greets tool", "name": "Peter"}))

    print("\n--- unknown tool name ---")
    print(execute_tool("echoz_not_tool", {}))
    print(execute_tool("greetz_not_tool", {}))
    
    
        
