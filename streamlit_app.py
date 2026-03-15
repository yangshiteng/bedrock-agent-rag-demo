from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

DEFAULT_BACKEND_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
SAMPLE_PROMPTS = [
    "What is the internal definition of quarterly net revenue?",
    "What policy applies to vendor risk reviews?",
    "Summarize the approval workflow for non-standard contract terms.",
]


def get_backend_health(base_url: str) -> dict[str, Any]:
    response = requests.get(f"{base_url}/health", timeout=10)
    response.raise_for_status()
    return response.json()


def send_chat(base_url: str, question: str, session_id: str | None, enable_trace: bool) -> dict[str, Any]:
    response = requests.post(
        f"{base_url}/chat",
        json={
            "question": question,
            "session_id": session_id,
            "enable_trace": enable_trace,
        },
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def initialize_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", None)
    st.session_state.setdefault("prompt_seed", "")


def render_sidebar(base_url: str) -> None:
    st.sidebar.title("Demo Controls")
    st.sidebar.caption("Bedrock Agent + Knowledge Base RAG demo")

    st.sidebar.write("Example prompts")
    for prompt in SAMPLE_PROMPTS:
        if st.sidebar.button(prompt, use_container_width=True):
            st.session_state.prompt_seed = prompt

    st.sidebar.divider()

    if st.sidebar.button("Start new session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.session_state.prompt_seed = ""
        st.rerun()

    st.sidebar.write("Backend status")
    try:
        health = get_backend_health(base_url)
    except requests.RequestException as exc:
        st.sidebar.error(f"Backend unavailable: {exc}")
        return

    if health["ok"]:
        st.sidebar.success(health["message"])
    else:
        st.sidebar.error(health["message"])

    st.sidebar.write(f"Region: `{health.get('aws_region') or 'n/a'}`")
    st.sidebar.write(f"Agent ID: `{health.get('agent_id') or 'n/a'}`")
    st.sidebar.write(f"Alias ID: `{health.get('agent_alias_id') or 'n/a'}`")
    st.sidebar.write(f"Current session: `{st.session_state.session_id or 'new session'}`")


def render_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("trace_count") is not None:
                st.caption(f"Trace events: {message['trace_count']}")


def main() -> None:
    st.set_page_config(
        page_title="Bedrock Agent RAG Demo",
        page_icon=":mag:",
        layout="wide",
    )
    initialize_state()

    st.title("Bedrock Agent RAG Demo")
    st.write("Ask questions against your AWS Bedrock Agent and attached Knowledge Base through a FastAPI backend.")

    with st.sidebar:
        backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL)
        enable_trace = st.checkbox("Enable trace capture", value=False)

    render_sidebar(backend_url)

    render_messages()

    prompt = st.chat_input(
        "Ask a Knowledge Base question...",
        key=f"chat_input_{len(st.session_state.messages)}",
    )
    seeded_prompt = st.session_state.prompt_seed
    if seeded_prompt:
        prompt = seeded_prompt
        st.session_state.prompt_seed = ""

    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Querying Bedrock Agent..."):
            try:
                response = send_chat(
                    base_url=backend_url,
                    question=prompt,
                    session_id=st.session_state.session_id,
                    enable_trace=enable_trace,
                )
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Request failed: {detail}")
                return
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
                return

        st.markdown(response["answer"] or "[No text response returned by agent]")
        st.caption(f"Trace events: {response['trace_count']}")

    st.session_state.session_id = response["session_id"]
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response["answer"] or "[No text response returned by agent]",
            "trace_count": response["trace_count"],
        }
    )


if __name__ == "__main__":
    main()
