import os
import json
import functools
from pydantic import BaseModel, Field

from langchain.tools import StructuredTool

from tolstoy_agents.utils import (
    handle_exceptions
    )

@handle_exceptions
def get_meeting_links() -> str:
    calendar_links = [
        "https://calendly.com/gilbert-tolstoy/30min",
        "https://calendly.com/amorbaron/30min"
    ]
    return json.dumps(calendar_links)


def get_meeting_links_factory() -> StructuredTool:
    return StructuredTool.from_function(
        func=get_meeting_links,
        name="get_meeting_links",
        description= (
            "Returns the calendar links of Gilbert and Amor scheduling meetings. Use this tool to generate a meeting link for the user to schedule a meeting with Gilbert or Amor."
        ),
        args_schema=None,
        return_direct=False
    )
