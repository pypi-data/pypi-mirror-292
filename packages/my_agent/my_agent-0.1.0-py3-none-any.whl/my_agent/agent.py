from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional, Type
from dotenv import load_dotenv
from langchain_core.prompts.prompt import PromptTemplate
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import MessageGraph, END

from langgraph.checkpoint.memory import MemorySaver

from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
    AsyncCallbackManagerForToolRun,
)
import os
import json

# Load environment variables
load_dotenv(override=True)

# Import the cypher chain
from neo4j_cypher.chain import chain as cypher_chain
from neo4j_advanced_rag import chain as advanced_rag_chain


# Import prompts from separate file
from my_agent.prompts import (
    SYSTEM_MESSAGE_TEMPLATE,
    TOOL_DESCRIPTION,
    RETRIEVER_INPUT_DESCRIPTION,
)


# Define input schema for the custom tool
class RetrieverInput(BaseModel):
    full_query: str = Field(description=RETRIEVER_INPUT_DESCRIPTION)


# Create custom retriever tool for council alignment system
class CustomCouncilAlignmentRetrieverTool(BaseTool):
    name = "search_council_alignment"
    description = TOOL_DESCRIPTION
    args_schema: Type[BaseModel] = RetrieverInput
    return_direct: bool = True

    def _run(
        self, full_query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        result = advanced_rag_chain.invoke({"question": full_query})
        return result

    async def _arun(
        self,
        full_query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await advanced_rag_chain.ainvoke(
            {"question": full_query},
            # {"configurable": {"strategy": "parent_strategy"}},
        )
        return result


# Create the custom tool
custom_tool = CustomCouncilAlignmentRetrieverTool()

tools = [custom_tool]
tool_executor = ToolExecutor(tools)

# Initialize LLM and chain
llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-4")
llm_with_tool = llm.bind_tools(tools)

# System message template
template = SYSTEM_MESSAGE_TEMPLATE


async def get_messages_info(messages):
    return [SystemMessage(content=template)] + messages


chain = get_messages_info | llm_with_tool


# Helper function for determining if tool was called
def _is_tool_call(msg):
    return hasattr(msg, "additional_kwargs") and "tool_calls" in msg.additional_kwargs


# Function to process messages and execute tool if called
async def process_messages(messages):
    tool_call = None
    # reverse the messages to find avoid using same tool call multiple times
    for m in reversed(messages):
        if _is_tool_call(m):
            tool_call = m.additional_kwargs["tool_calls"][0]
            arguments = json.loads(tool_call["function"]["arguments"])
            break

    if tool_call:
        print(f"\033[94mTool Call: {tool_call}\033[0m")
        action = ToolInvocation(
            tool=tool_call["function"]["name"], tool_input=arguments["full_query"]
        )
        response = await tool_executor.ainvoke(action)
        function_message = ToolMessage(
            content=str(response), name=action.tool, tool_call_id=tool_call["id"]
        )
        messages.append(function_message)

    return messages


from langchain_core.messages import AIMessage


# Define state logic
async def get_state(messages):
    if _is_tool_call(messages[-1]):
        return "process_tool"
    elif isinstance(messages[-1], AIMessage):
        return END
    return "user_input"


# Create the graph
memory = MemorySaver()


nodes = {k: k for k in ["user_input", "process_tool", END]}
workflow = MessageGraph()
workflow.add_node("user_input", chain)
workflow.add_node("process_tool", process_messages)
workflow.add_conditional_edges("user_input", get_state, nodes)
workflow.add_conditional_edges("process_tool", get_state, nodes)
workflow.set_entry_point("user_input")
graph = workflow.compile(checkpointer=memory)

import uuid
import asyncio
from langchain_core.messages import HumanMessage


async def main():
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    while True:
        user = input("User (q/Q to quit): ")
        if user in {"q", "Q"}:
            print("AI: Byebye")
            break
        async for output in graph.astream([HumanMessage(content=user)], config=config):
            if "__end__" in output:
                continue
            # astream() yields dictionaries with output keyed by node name
            for key, value in output.items():
                print(f"Output from node '{key}':")
                print("---")
                print(value)
            print("\n---\n")


if __name__ == "__main__":
    asyncio.run(main())
