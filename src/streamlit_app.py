import asyncio
import os
import urllib.parse
import uuid
from collections.abc import AsyncGenerator
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from client import AgentClient, AgentClientError
from schema import ChatHistory, ChatMessage
from schema.task_data import TaskData, TaskDataStatus
from voice import VoiceManager

# A Streamlit app for interacting with the langgraph agent via a simple chat interface.
# The app has three main functions which are all run async:

# - main() - sets up the streamlit app and high level structure
# - draw_messages() - draws a set of chat messages - either replaying existing messages
#   or streaming new ones.
# - handle_feedback() - Draws a feedback widget and records feedback from the user.

# The app heavily uses AgentClient to interact with the agent's FastAPI endpoints.


APP_TITLE = "Agent Service Toolkit"
APP_ICON = "🧰"
USER_ID_COOKIE = "user_id"


def get_or_create_user_id() -> str:
    """Get the user ID from session state or URL parameters, or create a new one if it doesn't exist."""
    # Check if user_id exists in session state
    if USER_ID_COOKIE in st.session_state:
        return st.session_state[USER_ID_COOKIE]

    # Try to get from URL parameters using the new st.query_params
    if USER_ID_COOKIE in st.query_params:
        user_id = st.query_params[USER_ID_COOKIE]
        st.session_state[USER_ID_COOKIE] = user_id
        return user_id

    # Generate a new user_id if not found
    user_id = str(uuid.uuid4())

    # Store in session state for this session
    st.session_state[USER_ID_COOKIE] = user_id

    # Also add to URL parameters so it can be bookmarked/shared
    st.query_params[USER_ID_COOKIE] = user_id

    return user_id


async def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        menu_items={},
    )

    # Hide the streamlit upper-right chrome
    st.html(
        """
        <style>
        [data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
            }
        </style>
        """,
    )
    if st.get_option("client.toolbarMode") != "minimal":
        st.set_option("client.toolbarMode", "minimal")
        await asyncio.sleep(0.1)
        st.rerun()

    # Get or create user ID
    user_id = get_or_create_user_id()

    if "agent_client" not in st.session_state:
        load_dotenv()
        agent_url = os.getenv("AGENT_URL")
        if not agent_url:
            host = os.getenv("HOST", "0.0.0.0")
            port = os.getenv("PORT", 8080)
            agent_url = f"http://{host}:{port}"
        try:
            with st.spinner("Connecting to agent service..."):
                st.session_state.agent_client = AgentClient(base_url=agent_url)
        except AgentClientError as e:
            st.error(f"Error connecting to agent service at {agent_url}: {e}")
            st.markdown("The service might be booting up. Try again in a few seconds.")
            st.stop()
    agent_client: AgentClient = st.session_state.agent_client

    # Initialize voice manager (once per session)
    if "voice_manager" not in st.session_state:
        st.session_state.voice_manager = VoiceManager.from_env()
    voice = st.session_state.voice_manager

    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = str(uuid.uuid4())
            messages = []
        else:
            try:
                messages: ChatHistory = agent_client.get_history(thread_id=thread_id).messages
            except AgentClientError:
                st.error("No message history found for this Thread ID.")
                messages = []
        st.session_state.messages = messages
        st.session_state.thread_id = thread_id

    # Config options
    with st.sidebar:
        st.header(f"{APP_ICON} {APP_TITLE}")

        ""
        "Full toolkit for running an AI agent service built with LangGraph, FastAPI and Streamlit"
        ""

        page = st.radio(
            "页面",
            options=["知识卡片系统", "聊天助手"],
            index=1,
        )

        if st.button(":material/chat: New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            # Clear saved audio when starting new chat
            if "last_audio" in st.session_state:
                del st.session_state.last_audio
            st.rerun()

        with st.popover(":material/settings: Settings", use_container_width=True):
            model_idx = agent_client.info.models.index(agent_client.info.default_model)
            model = st.selectbox("LLM to use", options=agent_client.info.models, index=model_idx)
            agent_list = [a.key for a in agent_client.info.agents]
            agent_idx = agent_list.index(agent_client.info.default_agent)
            agent_client.agent = st.selectbox(
                "Agent to use",
                options=agent_list,
                index=agent_idx,
            )
            use_streaming = st.toggle("Stream results", value=True)
            # Audio toggle with callback: clears cached audio when toggled off
            enable_audio = st.toggle(
                "Enable audio generation",
                value=True,
                disabled=not voice or not voice.tts,
                help="Configure VOICE_TTS_PROVIDER in .env to enable"
                if not voice or not voice.tts
                else None,
                on_change=lambda: st.session_state.pop("last_audio", None)
                if not st.session_state.get("enable_audio", True)
                else None,
                key="enable_audio",
            )

            # Display user ID (for debugging or user information)
            st.text_input("User ID (read-only)", value=user_id, disabled=True)

        @st.dialog("Architecture")
        def architecture_dialog() -> None:
            st.image(
                "https://github.com/JoshuaC215/agent-service-toolkit/blob/main/media/agent_architecture.png?raw=true"
            )
            "[View full size on Github](https://github.com/JoshuaC215/agent-service-toolkit/blob/main/media/agent_architecture.png)"
            st.caption(
                "App hosted on [Streamlit Cloud](https://share.streamlit.io/) with FastAPI service running in [Azure](https://learn.microsoft.com/en-us/azure/app-service/)"
            )

        if st.button(":material/schema: Architecture", use_container_width=True):
            architecture_dialog()

        with st.popover(":material/policy: Privacy", use_container_width=True):
            st.write(
                "Prompts, responses and feedback in this app are anonymously recorded and saved to LangSmith for product evaluation and improvement purposes only."
            )

        @st.dialog("Share/resume chat")
        def share_chat_dialog() -> None:
            session = st.runtime.get_instance()._session_mgr.list_active_sessions()[0]
            st_base_url = urllib.parse.urlunparse(
                [session.client.request.protocol, session.client.request.host, "", "", "", ""]
            )
            # if it's not localhost, switch to https by default
            if not st_base_url.startswith("https") and "localhost" not in st_base_url:
                st_base_url = st_base_url.replace("http", "https")
            # Include both thread_id and user_id in the URL for sharing to maintain user identity
            chat_url = (
                f"{st_base_url}?thread_id={st.session_state.thread_id}&{USER_ID_COOKIE}={user_id}"
            )
            st.markdown(f"**Chat URL:**\n```text\n{chat_url}\n```")
            st.info("Copy the above URL to share or revisit this chat")

        if st.button(":material/upload: Share/resume chat", use_container_width=True):
            share_chat_dialog()

        "[View the source code](https://github.com/JoshuaC215/agent-service-toolkit)"
        st.caption(
            "Made with :material/favorite: by [Joshua](https://www.linkedin.com/in/joshua-k-carroll/) in Oakland"
        )

    if page == "知识卡片系统":
        render_card_system_page(agent_client)
        return

    # Draw existing messages
    messages: list[ChatMessage] = st.session_state.messages

    if len(messages) == 0:
        match agent_client.agent:
            case "chatbot":
                WELCOME = "Hello! I'm a simple chatbot. Ask me anything!"
            case "interrupt-agent":
                WELCOME = "Hello! I'm an interrupt agent. Tell me your birthday and I will predict your personality!"
            case "research-assistant":
                WELCOME = "Hello! I'm an AI-powered research assistant with web search and a calculator. Ask me anything!"
            case "rag-assistant":
                WELCOME = """Hello! I'm an AI-powered Company Policy & HR assistant with access to AcmeTech's Employee Handbook.
                I can help you find information about benefits, remote work, time-off policies, company values, and more. Ask me anything!"""
            case _:
                WELCOME = "Hello! I'm an AI agent. Ask me anything!"

        with st.chat_message("ai"):
            st.write(WELCOME)

    # draw_messages() expects an async iterator over messages
    async def amessage_iter() -> AsyncGenerator[ChatMessage, None]:
        for m in messages:
            yield m

    await draw_messages(amessage_iter())

    # Render saved audio for the last AI message (if it exists)
    # This ensures audio persists across st.rerun() calls
    if (
        voice
        and enable_audio
        and "last_audio" in st.session_state
        and st.session_state.last_message
        and len(messages) > 0
        and messages[-1].type == "ai"
    ):
        with st.session_state.last_message:
            audio_data = st.session_state.last_audio
            st.audio(audio_data["data"], format=audio_data["format"])

    # Generate new message if the user provided new input
    # Use voice manager if available, otherwise fall back to regular input
    # REQUIRED: Set VOICE_STT_PROVIDER, VOICE_TTS_PROVIDER, OPENAI_API_KEY
    # in app .env (NOT service .env) to enable voice features.
    if voice:
        user_input = voice.get_chat_input()
    else:
        user_input = st.chat_input()

    if user_input:
        messages.append(ChatMessage(type="human", content=user_input))
        st.chat_message("human").write(user_input)
        try:
            if use_streaming:
                stream = agent_client.astream(
                    message=user_input,
                    model=model,
                    thread_id=st.session_state.thread_id,
                    user_id=user_id,
                )
                await draw_messages(stream, is_new=True)
                # Generate TTS audio for streaming response
                # Note: draw_messages() stores the final message in st.session_state.messages
                # and the container reference in st.session_state.last_message
                if voice and enable_audio and st.session_state.messages:
                    last_msg = st.session_state.messages[-1]
                    # Only generate audio for AI responses with content
                    if last_msg.type == "ai" and last_msg.content:
                        # Use audio_only=True since text was already streamed by draw_messages()
                        voice.render_message(
                            last_msg.content,
                            container=st.session_state.last_message,
                            audio_only=True,
                        )
            else:
                response = await agent_client.ainvoke(
                    message=user_input,
                    model=model,
                    thread_id=st.session_state.thread_id,
                    user_id=user_id,
                )
                messages.append(response)
                # Render AI response with optional voice
                with st.chat_message("ai"):
                    if voice and enable_audio:
                        voice.render_message(response.content)
                    else:
                        st.write(response.content)
            st.rerun()  # Clear stale containers
        except AgentClientError as e:
            st.error(f"Error generating response: {e}")
            st.stop()

    # If messages have been generated, show feedback widget
    if len(messages) > 0 and st.session_state.last_message:
        with st.session_state.last_message:
            await handle_feedback()


async def draw_messages(
    messages_agen: AsyncGenerator[ChatMessage | str, None],
    is_new: bool = False,
) -> None:
    """
    Draws a set of chat messages - either replaying existing messages
    or streaming new ones.

    This function has additional logic to handle streaming tokens and tool calls.
    - Use a placeholder container to render streaming tokens as they arrive.
    - Use a status container to render tool calls. Track the tool inputs and outputs
      and update the status container accordingly.

    The function also needs to track the last message container in session state
    since later messages can draw to the same container. This is also used for
    drawing the feedback widget in the latest chat message.

    Args:
        messages_aiter: An async iterator over messages to draw.
        is_new: Whether the messages are new or not.
    """

    # Keep track of the last message container
    last_message_type = None
    st.session_state.last_message = None

    # Placeholder for intermediate streaming tokens
    streaming_content = ""
    streaming_placeholder = None

    # Iterate over the messages and draw them
    while msg := await anext(messages_agen, None):
        # str message represents an intermediate token being streamed
        if isinstance(msg, str):
            # If placeholder is empty, this is the first token of a new message
            # being streamed. We need to do setup.
            if not streaming_placeholder:
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")
                with st.session_state.last_message:
                    streaming_placeholder = st.empty()

            streaming_content += msg
            streaming_placeholder.write(streaming_content)
            continue
        if not isinstance(msg, ChatMessage):
            st.error(f"Unexpected message type: {type(msg)}")
            st.write(msg)
            st.stop()

        match msg.type:
            # A message from the user, the easiest case
            case "human":
                last_message_type = "human"
                st.chat_message("human").write(msg.content)

            # A message from the agent is the most complex case, since we need to
            # handle streaming tokens and tool calls.
            case "ai":
                # If we're rendering new messages, store the message in session state
                if is_new:
                    st.session_state.messages.append(msg)

                # If the last message type was not AI, create a new chat message
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")

                with st.session_state.last_message:
                    # If the message has content, write it out.
                    # Reset the streaming variables to prepare for the next message.
                    if msg.content:
                        if streaming_placeholder:
                            streaming_placeholder.write(msg.content)
                            streaming_content = ""
                            streaming_placeholder = None
                        else:
                            st.write(msg.content)

                    if msg.tool_calls:
                        # Create a status container for each tool call and store the
                        # status container by ID to ensure results are mapped to the
                        # correct status container.
                        call_results = {}
                        for tool_call in msg.tool_calls:
                            # Use different labels for transfer vs regular tool calls
                            if "transfer_to" in tool_call["name"]:
                                label = f"""💼 Sub Agent: {tool_call["name"]}"""
                            else:
                                label = f"""🛠️ Tool Call: {tool_call["name"]}"""

                            status = st.status(
                                label,
                                state="running" if is_new else "complete",
                            )
                            call_results[tool_call["id"]] = status

                        # Expect one ToolMessage for each tool call.
                        for tool_call in msg.tool_calls:
                            if "transfer_to" in tool_call["name"]:
                                status = call_results[tool_call["id"]]
                                status.update(expanded=True)
                                await handle_sub_agent_msgs(messages_agen, status, is_new)
                                break

                            # Only non-transfer tool calls reach this point
                            status = call_results[tool_call["id"]]
                            status.write("Input:")
                            status.write(tool_call["args"])
                            tool_result: ChatMessage = await anext(messages_agen)

                            if tool_result.type != "tool":
                                st.error(f"Unexpected ChatMessage type: {tool_result.type}")
                                st.write(tool_result)
                                st.stop()

                            # Record the message if it's new, and update the correct
                            # status container with the result
                            if is_new:
                                st.session_state.messages.append(tool_result)
                            if tool_result.tool_call_id:
                                status = call_results[tool_result.tool_call_id]
                            status.write("Output:")
                            status.write(tool_result.content)
                            status.update(state="complete")

            case "custom":
                # CustomData example used by the bg-task-agent
                # See:
                # - src/agents/utils.py CustomData
                # - src/agents/bg_task_agent/task.py
                try:
                    task_data: TaskData = TaskData.model_validate(msg.custom_data)
                except ValidationError:
                    st.error("Unexpected CustomData message received from agent")
                    st.write(msg.custom_data)
                    st.stop()

                if is_new:
                    st.session_state.messages.append(msg)

                if last_message_type != "task":
                    last_message_type = "task"
                    st.session_state.last_message = st.chat_message(
                        name="task", avatar=":material/manufacturing:"
                    )
                    with st.session_state.last_message:
                        status = TaskDataStatus()

                status.add_and_draw_task_data(task_data)

            # In case of an unexpected message type, log an error and stop
            case _:
                st.error(f"Unexpected ChatMessage type: {msg.type}")
                st.write(msg)
                st.stop()


async def handle_feedback() -> None:
    """Draws a feedback widget and records feedback from the user."""

    # Keep track of last feedback sent to avoid sending duplicates
    if "last_feedback" not in st.session_state:
        st.session_state.last_feedback = (None, None)

    latest_run_id = st.session_state.messages[-1].run_id
    feedback = st.feedback("stars", key=latest_run_id)

    # If the feedback value or run ID has changed, send a new feedback record
    if feedback is not None and (latest_run_id, feedback) != st.session_state.last_feedback:
        # Normalize the feedback value (an index) to a score between 0 and 1
        normalized_score = (feedback + 1) / 5.0

        agent_client: AgentClient = st.session_state.agent_client
        try:
            await agent_client.acreate_feedback(
                run_id=latest_run_id,
                key="human-feedback-stars",
                score=normalized_score,
                kwargs={"comment": "In-line human feedback"},
            )
        except AgentClientError as e:
            st.error(f"Error recording feedback: {e}")
            st.stop()
        st.session_state.last_feedback = (latest_run_id, feedback)
        st.toast("Feedback recorded", icon=":material/reviews:")


def render_card_system_page(agent_client: AgentClient) -> None:
    """Render the knowledge card workflow UI."""
    st.title("知识卡片生成与复习规划智能体系统")
    _init_card_system_state()

    tabs = st.tabs(["资料输入", "知识卡片", "自测练习", "错题本", "复习计划", "学习统计"])
    with tabs[0]:
        _render_document_tab(agent_client)
    with tabs[1]:
        _render_cards_tab(agent_client)
    with tabs[2]:
        _render_quiz_tab(agent_client)
    with tabs[3]:
        _render_wrong_questions_tab(agent_client)
    with tabs[4]:
        _render_review_plan_tab(agent_client)
    with tabs[5]:
        _render_study_summary_tab(agent_client)


def _init_card_system_state() -> None:
    defaults = {
        "card_documents": [],
        "card_cards": [],
        "card_quiz": [],
        "card_wrong_questions": [],
        "card_review_plan": None,
        "card_selected_document_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _friendly_call(label: str, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except AgentClientError as e:
        st.error(f"{label}失败：{e}")
    except Exception as e:
        st.error(f"{label}失败：{e}")
    return None


def _refresh_documents(agent_client: AgentClient) -> None:
    documents = _friendly_call("获取资料列表", agent_client.list_card_documents)
    if documents is not None:
        st.session_state.card_documents = documents


def _refresh_cards(agent_client: AgentClient, document_id: str | None = None) -> None:
    cards = _friendly_call("获取知识卡片", agent_client.list_cards, document_id)
    if cards is not None:
        st.session_state.card_cards = cards


def _refresh_quiz(agent_client: AgentClient) -> None:
    questions = _friendly_call("获取题目", agent_client.list_quiz)
    if questions is not None:
        st.session_state.card_quiz = questions


def _render_document_tab(agent_client: AgentClient) -> None:
    st.subheader("资料输入")
    title = st.text_input("资料标题", key="card_doc_title")
    content = st.text_area("粘贴学习资料文本", height=260, key="card_doc_content")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("创建资料", use_container_width=True):
            if not content.strip():
                st.warning("请先输入学习资料文本。")
            else:
                document = _friendly_call(
                    "创建资料",
                    agent_client.create_card_document,
                    title or None,
                    content,
                )
                if document:
                    st.session_state.card_selected_document_id = str(document["id"])
                    _refresh_documents(agent_client)
                    st.success("资料已创建。")

    with col2:
        if st.button("刷新资料列表", use_container_width=True):
            _refresh_documents(agent_client)

    with col3:
        if st.button("生成知识卡片", use_container_width=True):
            selected_id = st.session_state.card_selected_document_id
            result = None
            if selected_id:
                result = _friendly_call("生成知识卡片", agent_client.generate_cards, selected_id)
            elif content.strip():
                result = _friendly_call(
                    "生成知识卡片",
                    agent_client.generate_cards,
                    None,
                    content,
                    title or None,
                )
                if result:
                    st.session_state.card_selected_document_id = str(result["document"]["id"])
            else:
                st.warning("请选择已有资料或输入学习资料文本。")
            if result:
                st.session_state.card_cards = result["cards"]["cards"]
                _refresh_documents(agent_client)
                st.success("知识卡片已生成。")

    if st.button("载入资料列表", use_container_width=True):
        _refresh_documents(agent_client)

    documents = st.session_state.card_documents
    if documents:
        options = {f"{doc['title']} ({doc['id']})": str(doc["id"]) for doc in documents}
        current = st.selectbox("选择已有资料", options=list(options.keys()))
        st.session_state.card_selected_document_id = options[current]
        selected = next(
            doc for doc in documents if str(doc["id"]) == st.session_state.card_selected_document_id
        )
        st.caption(f"创建时间：{selected.get('created_at', '')}")
        st.text_area(
            "资料预览", value=selected.get("content", "")[:2000], height=180, disabled=True
        )


def _render_cards_tab(agent_client: AgentClient) -> None:
    st.subheader("知识卡片")
    if st.button("刷新知识卡片", use_container_width=True):
        _refresh_cards(agent_client, st.session_state.card_selected_document_id)

    cards = st.session_state.card_cards
    if not cards:
        st.info("暂无知识卡片，请先在“资料输入”中生成。")
        return

    for index, card in enumerate(cards, 1):
        with st.expander(f"{index}. {card.get('title', '未命名卡片')}", expanded=index == 1):
            st.markdown(f"**摘要：** {card.get('summary', '')}")
            st.markdown(f"**关键词：** {_join_list(card.get('keywords'))}")
            st.markdown(f"**详细解释：** {card.get('explanation', '')}")
            st.markdown(f"**示例：** {card.get('example') or '暂无'}")
            st.markdown(f"**易错点：** {_join_list(card.get('common_mistakes'))}")
            st.markdown(f"**关联知识点：** {_join_list(card.get('related_concepts'))}")


def _render_quiz_tab(agent_client: AgentClient) -> None:
    st.subheader("自测练习")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("根据知识卡片生成题目", use_container_width=True):
            result = _friendly_call("生成题目", agent_client.generate_quiz)
            if result:
                st.session_state.card_quiz = result["questions"]["questions"]
                st.success("题目已生成。")
    with col2:
        if st.button("刷新题目列表", use_container_width=True):
            _refresh_quiz(agent_client)

    questions = st.session_state.card_quiz
    if not questions:
        st.info("暂无题目，请先生成自测题。")
        return

    for index, question in enumerate(questions, 1):
        qid = str(question["id"])
        with st.expander(f"{index}. {question.get('question', '')}", expanded=index == 1):
            st.caption(
                f"题型：{question.get('question_type', '')} | 难度：{question.get('difficulty', '')}"
            )
            options = question.get("options") or []
            if options:
                answer = st.radio("选择答案", options=options, key=f"answer_{qid}")
            else:
                answer = st.text_area("输入答案", key=f"answer_{qid}", height=100)

            if st.button("提交答案", key=f"submit_{qid}"):
                if not str(answer).strip():
                    st.warning("请先填写答案。")
                    continue
                result = _friendly_call(
                    "提交答案", agent_client.submit_quiz_answer, qid, str(answer)
                )
                if result:
                    check = result["result"]
                    st.success("回答正确。" if check["is_correct"] else "回答不正确。")
                    st.markdown(f"**正确答案：** {check['correct_answer']}")
                    st.markdown(f"**解析：** {check['explanation']}")
                    st.markdown(f"**反馈：** {check['feedback']}")


def _render_wrong_questions_tab(agent_client: AgentClient) -> None:
    st.subheader("错题本")
    if st.button("刷新错题本", use_container_width=True):
        wrong_questions = _friendly_call("获取错题本", agent_client.list_wrong_questions)
        if wrong_questions is not None:
            st.session_state.card_wrong_questions = wrong_questions

    wrong_questions = st.session_state.card_wrong_questions
    if not wrong_questions:
        st.info("暂无错题。提交错误答案后会出现在这里。")
        return

    for item in wrong_questions:
        with st.expander(item.get("question", "错题")):
            st.markdown(f"**关联知识点：** {item.get('related_knowledge') or '暂无'}")
            st.markdown(f"**错误次数：** {item.get('error_count', 0)}")
            st.markdown(f"**正确答案：** {item.get('answer', '')}")
            st.markdown(f"**解析：** {item.get('explanation', '')}")


def _render_review_plan_tab(agent_client: AgentClient) -> None:
    st.subheader("复习计划")
    plan_days = st.radio("计划长度", options=[3, 7], horizontal=True)
    weak_points_text = st.text_area("薄弱点（可选，每行一个；留空则根据错题本生成）", height=120)

    if st.button("生成复习计划", use_container_width=True):
        weak_points = [line.strip() for line in weak_points_text.splitlines() if line.strip()]
        result = _friendly_call(
            "生成复习计划",
            agent_client.generate_review_plan,
            weak_points or None,
            f"{plan_days} 天复习计划",
        )
        if result:
            plan = result["plan"]
            plan["tasks"] = plan.get("tasks", [])[:plan_days]
            st.session_state.card_review_plan = plan
            st.success("复习计划已生成。")

    plan = st.session_state.card_review_plan
    if not plan:
        st.info("暂无复习计划。")
        return

    st.markdown(f"**薄弱点：** {_join_list(plan.get('weak_points'))}")
    for task in plan.get("tasks", []):
        st.markdown(f"### Day {task.get('day')}: {task.get('topic')}")
        st.markdown(f"- 任务：{task.get('task')}")
        st.markdown(f"- 原因：{task.get('reason')}")
        st.checkbox("完成状态", value=bool(task.get("is_completed")), disabled=True)


def _render_study_summary_tab(agent_client: AgentClient) -> None:
    st.subheader("学习统计")
    summary = None
    if st.button("刷新学习统计", use_container_width=True):
        summary = _friendly_call("获取学习统计", agent_client.get_study_summary)

    if not summary:
        st.info("点击刷新学习统计查看当前数据。")
        return

    cols = st.columns(6)
    cols[0].metric("资料数量", summary.get("document_count", 0))
    cols[1].metric("知识卡片数量", summary.get("card_count", 0))
    cols[2].metric("题目数量", summary.get("quiz_count", 0))
    cols[3].metric("答题数量", summary.get("answer_count", 0))
    cols[4].metric("错题数量", summary.get("wrong_count", 0))
    cols[5].metric("正确率", f"{summary.get('accuracy', 0) * 100:.1f}%")


def _join_list(value: Any) -> str:
    if isinstance(value, list):
        return "、".join(str(item) for item in value) or "暂无"
    if value:
        return str(value)
    return "暂无"


async def handle_sub_agent_msgs(messages_agen, status, is_new):
    """
    This function segregates agent output into a status container.
    It handles all messages after the initial tool call message
    until it reaches the final AI message.

    Enhanced to support nested multi-agent hierarchies with handoff back messages.

    Args:
        messages_agen: Async generator of messages
        status: the status container for the current agent
        is_new: Whether messages are new or replayed
    """
    nested_popovers = {}

    # looking for the transfer Success tool call message
    first_msg = await anext(messages_agen)
    if is_new:
        st.session_state.messages.append(first_msg)

    # Continue reading until we get an explicit handoff back
    while True:
        # Read next message
        sub_msg = await anext(messages_agen)

        # this should only happen is skip_stream flag is removed
        # if isinstance(sub_msg, str):
        #     continue

        if is_new:
            st.session_state.messages.append(sub_msg)

        # Handle tool results with nested popovers
        if sub_msg.type == "tool" and sub_msg.tool_call_id in nested_popovers:
            popover = nested_popovers[sub_msg.tool_call_id]
            popover.write("**Output:**")
            popover.write(sub_msg.content)
            continue

        # Handle transfer_back_to tool calls - these indicate a sub-agent is returning control
        if (
            hasattr(sub_msg, "tool_calls")
            and sub_msg.tool_calls
            and any("transfer_back_to" in tc.get("name", "") for tc in sub_msg.tool_calls)
        ):
            # Process transfer_back_to tool calls
            for tc in sub_msg.tool_calls:
                if "transfer_back_to" in tc.get("name", ""):
                    # Read the corresponding tool result
                    transfer_result = await anext(messages_agen)
                    if is_new:
                        st.session_state.messages.append(transfer_result)

            # After processing transfer back, we're done with this agent
            if status:
                status.update(state="complete")
            break

        # Display content and tool calls in the same nested status
        if status:
            if sub_msg.content:
                status.write(sub_msg.content)

            if hasattr(sub_msg, "tool_calls") and sub_msg.tool_calls:
                for tc in sub_msg.tool_calls:
                    # Check if this is a nested transfer/delegate
                    if "transfer_to" in tc["name"]:
                        # Create a nested status container for the sub-agent
                        nested_status = status.status(
                            f"""💼 Sub Agent: {tc["name"]}""",
                            state="running" if is_new else "complete",
                            expanded=True,
                        )

                        # Recursively handle sub-agents of this sub-agent
                        await handle_sub_agent_msgs(messages_agen, nested_status, is_new)
                    else:
                        # Regular tool call - create popover
                        popover = status.popover(f"{tc['name']}", icon="🛠️")
                        popover.write(f"**Tool:** {tc['name']}")
                        popover.write("**Input:**")
                        popover.write(tc["args"])
                        # Store the popover reference using the tool call ID
                        nested_popovers[tc["id"]] = popover


if __name__ == "__main__":
    asyncio.run(main())
