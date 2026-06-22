import inspect
import json
import logging
import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from langchain_core._api import LangChainBetaWarning
from langchain_core.messages import AIMessage, AIMessageChunk, AnyMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langfuse import Langfuse  # type: ignore[import-untyped]
from langfuse.langchain import (
    CallbackHandler,  # type: ignore[import-untyped]
)
from langgraph.types import Command, Interrupt
from langsmith import Client as LangsmithClient
from langsmith import uuid7

from agents import DEFAULT_AGENT, AgentGraph, get_agent, get_all_agent_info, load_agent
from agents.card_review_agent import run_card_review_file_analysis
from card_system.answer_checker import check_answer
from card_system.review_planner import generate_review_plan
from card_system.storage import (
    CardSystemStorageError,
    DEFAULT_USER_ID,
    create_document,
    get_document,
    get_study_summary,
    init_card_system_db,
    list_documents,
    list_knowledge_cards,
    list_quiz_questions,
    list_wrong_questions,
    save_answer_record,
    save_knowledge_cards,
    save_quiz_questions,
    save_review_plan,
)
from core import settings
from memory import initialize_database, initialize_store
from schema import (
    AnalyzeFileResponse,
    ChatHistory,
    ChatHistoryInput,
    ChatMessage,
    CreateDocumentRequest,
    Feedback,
    FeedbackResponse,
    GenerateCardsRequest,
    GenerateCardsResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
    GenerateReviewPlanRequest,
    GenerateReviewPlanResponse,
    KnowledgeCard,
    KnowledgeCardList,
    QuizQuestion,
    QuizQuestionList,
    ServiceMetadata,
    StreamInput,
    SubmitAnswerResponse,
    UserInput,
)
from schema.quiz import AnswerSubmission
from service.utils import (
    convert_message_content_to_string,
    langchain_to_chat_message,
    remove_tool_calls,
)

warnings.filterwarnings("ignore", category=LangChainBetaWarning)
logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate idiomatic operation IDs for OpenAPI client generation."""
    return route.name


def verify_bearer(
    http_auth: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(HTTPBearer(description="Please provide AUTH_SECRET api key.", auto_error=False)),
    ],
) -> None:
    if not settings.AUTH_SECRET:
        return
    auth_secret = settings.AUTH_SECRET.get_secret_value()
    if not http_auth or http_auth.credentials != auth_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Configurable lifespan that initializes the appropriate database checkpointer, store,
    and agents with async loading - for example for starting up MCP clients.
    """
    try:
        # Initialize both checkpointer (for short-term memory) and store (for long-term memory)
        async with initialize_database() as saver, initialize_store() as store:
            # Set up both components
            if hasattr(saver, "setup"):  # ignore: union-attr
                await saver.setup()
            # Only setup store for Postgres as InMemoryStore doesn't need setup
            if hasattr(store, "setup"):  # ignore: union-attr
                await store.setup()

            # Configure agents with both memory components and async loading
            agents = get_all_agent_info()
            for a in agents:
                try:
                    await load_agent(a.key)
                    logger.info(f"Agent loaded: {a.key}")
                except Exception as e:
                    logger.error(f"Failed to load agent {a.key}: {e}")
                    # Continue with other agents rather than failing startup

                agent = get_agent(a.key)
                # Set checkpointer for thread-scoped memory (conversation history)
                agent.checkpointer = saver
                # Set store for long-term memory (cross-conversation knowledge)
                agent.store = store
            yield
    except Exception as e:
        logger.error(f"Error during database/store/agents initialization: {e}")
        raise


app = FastAPI(lifespan=lifespan, generate_unique_id_function=custom_generate_unique_id)
router = APIRouter(dependencies=[Depends(verify_bearer)])


def _storage_exception(e: CardSystemStorageError) -> HTTPException:
    return HTTPException(status_code=503, detail=str(e))


def _storage_user_id(user_id: str) -> str:
    try:
        return str(UUID(user_id))
    except (TypeError, ValueError):
        return DEFAULT_USER_ID


async def _ensure_card_system_db() -> None:
    try:
        await init_card_system_db()
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e


def _row_to_card(row: dict[str, Any]) -> KnowledgeCard:
    data = dict(row)
    data["id"] = str(data["id"])
    data["document_id"] = str(data["document_id"])
    return KnowledgeCard(**data)


def _row_to_question(row: dict[str, Any]) -> QuizQuestion:
    data = dict(row)
    data["id"] = str(data["id"])
    data["card_id"] = str(data["card_id"])
    return QuizQuestion(**data)


async def _run_card_review_agent(text: str) -> dict[str, Any]:
    try:
        agent = get_agent("card_review_agent")
        config = RunnableConfig(
            configurable={"thread_id": str(uuid4()), "user_id": "card-system-api"}
        )
        state = await agent.ainvoke({"messages": [HumanMessage(content=text)]}, config=config)
    except Exception as e:
        logger.error("Card review agent failed: %s", e)
        raise HTTPException(status_code=502, detail="Card review agent failed") from e

    if state.get("errors"):
        raise HTTPException(status_code=422, detail="; ".join(state["errors"]))
    return state


async def _get_question_or_404(question_id: str) -> QuizQuestion:
    try:
        rows = await list_quiz_questions()
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e
    for row in rows:
        if str(row["id"]) == question_id:
            return _row_to_question(row)
    raise HTTPException(status_code=404, detail="question_id not found")


async def _get_cards_or_404(card_id: str | None = None) -> list[KnowledgeCard]:
    try:
        rows = await list_knowledge_cards()
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e
    cards = [_row_to_card(row) for row in rows]
    if card_id:
        cards = [card for card in cards if card.id == card_id]
        if not cards:
            raise HTTPException(status_code=404, detail="card_id not found")
    if not cards:
        raise HTTPException(status_code=404, detail="No knowledge cards found")
    return cards


@router.get("/info")
async def info() -> ServiceMetadata:
    models = list(settings.AVAILABLE_MODELS)
    models.sort()
    return ServiceMetadata(
        agents=get_all_agent_info(),
        models=models,
        default_agent=DEFAULT_AGENT,
        default_model=settings.DEFAULT_MODEL,
    )


@router.post(
    "/card-system/documents",
    summary="Create a learning document",
)
async def create_card_system_document(input: CreateDocumentRequest) -> dict[str, Any]:
    """Create a learning document from text content."""
    if not input.content.strip():
        raise HTTPException(status_code=422, detail="content cannot be empty")
    await _ensure_card_system_db()
    try:
        return await create_document(
            title=input.title or input.content.splitlines()[0][:80] or "学习资料",
            content=input.content,
            file_path=input.file_path,
        )
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e


@router.get(
    "/card-system/documents",
    summary="List learning documents",
)
async def list_card_system_documents() -> list[dict[str, Any]]:
    """List learning documents."""
    await _ensure_card_system_db()
    try:
        return await list_documents()
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e


@router.post(
    "/card-system/agent/analyze-file",
    response_model=AnalyzeFileResponse,
    summary="Analyze an uploaded learning file with CardReviewAgent",
)
async def analyze_card_system_file(
    file: UploadFile = File(...),
    user_id: str = Form("default_user"),
    learning_goal: str | None = Form(None),
    card_count: int = Form(8),
    quiz_count: int = Form(5),
    review_days: int = Form(7),
) -> AnalyzeFileResponse:
    """Upload a learning file and run CardReviewAgent's full study workflow."""
    filename = file.filename or "learning-material.txt"
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=422, detail="file cannot be empty")
    if card_count < 1 or quiz_count < 1 or review_days < 1:
        raise HTTPException(status_code=422, detail="card_count, quiz_count and review_days must be positive")

    async def save_agent_memory(state: dict[str, Any]) -> dict[str, Any]:
        parsed = state["parsed_document"]
        cards = state["cards"]
        quizzes = state["quizzes"]
        review_plan = state["review_plan_model"]
        storage_user_id = _storage_user_id(user_id)

        try:
            await init_card_system_db()
            document = await create_document(
                title=str(parsed["filename"])[:120] or "CardReviewAgent 学习资料",
                content=str(parsed["text"]),
                file_path=str(parsed["filename"]),
                user_id=storage_user_id,
            )
            document_id = str(document["id"])
            for card in cards.cards:
                card.document_id = document_id
            await save_knowledge_cards(document_id, cards)
            await save_quiz_questions(quizzes)
            review_record = await save_review_plan(
                review_plan,
                title="CardReviewAgent 复习计划",
                user_id=storage_user_id,
            )
            return {"document": document, "review_record": review_record}
        except CardSystemStorageError as e:
            logger.warning("CardReviewAgent memory fallback: %s", e)
            return {
                "document": {
                    "id": str(uuid4()),
                    "title": parsed["filename"],
                    "content": parsed["text"],
                    "file_path": parsed["filename"],
                },
                "fallback": True,
                "error": str(e),
            }

    try:
        result = await run_card_review_file_analysis(
            filename=filename,
            file_bytes=file_bytes,
            user_id=user_id,
            learning_goal=learning_goal,
            card_count=card_count,
            quiz_count=quiz_count,
            review_days=review_days,
            memory_saver=save_agent_memory,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error("CardReviewAgent file analysis failed: %s", e)
        raise HTTPException(status_code=502, detail="CardReviewAgent file analysis failed") from e

    return AnalyzeFileResponse(**result)


@router.post(
    "/card-system/cards/generate",
    response_model=GenerateCardsResponse,
    summary="Generate knowledge cards",
)
async def generate_card_system_cards(input: GenerateCardsRequest) -> GenerateCardsResponse:
    """Generate knowledge cards from an existing document or direct text."""
    await _ensure_card_system_db()

    if input.document_id:
        try:
            document = await get_document(input.document_id)
        except CardSystemStorageError as e:
            raise _storage_exception(e) from e
        if not document:
            raise HTTPException(status_code=404, detail="document_id not found")
        content = str(document["content"])
    elif input.text and input.text.strip():
        try:
            document = await create_document(
                title=input.title or input.text.splitlines()[0][:80] or "学习资料",
                content=input.text,
            )
        except CardSystemStorageError as e:
            raise _storage_exception(e) from e
        content = input.text
    else:
        raise HTTPException(status_code=422, detail="document_id or non-empty text is required")

    state = await _run_card_review_agent(content)
    cards = state.get("cards")
    if not isinstance(cards, KnowledgeCardList):
        raise HTTPException(status_code=502, detail="Card review agent did not return cards")

    document_id = str(document["id"])
    for card in cards.cards:
        card.document_id = document_id

    try:
        await save_knowledge_cards(document_id, cards)
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e

    return GenerateCardsResponse(document=document, cards=cards)


@router.get(
    "/card-system/cards",
    summary="List knowledge cards",
)
async def list_card_system_cards(document_id: str | None = None) -> list[dict[str, Any]]:
    """List knowledge cards, optionally filtered by document ID."""
    await _ensure_card_system_db()
    if document_id:
        try:
            document = await get_document(document_id)
        except CardSystemStorageError as e:
            raise _storage_exception(e) from e
        if not document:
            raise HTTPException(status_code=404, detail="document_id not found")
    try:
        return await list_knowledge_cards(document_id=document_id)
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e


@router.post(
    "/card-system/quiz/generate",
    response_model=GenerateQuizResponse,
    summary="Generate quiz questions",
)
async def generate_card_system_quiz(input: GenerateQuizRequest) -> GenerateQuizResponse:
    """Generate quiz questions from stored knowledge cards."""
    await _ensure_card_system_db()
    cards = await _get_cards_or_404(input.card_id)
    questions = QuizQuestionList(
        questions=[
            QuizQuestion(
                card_id=card.id,
                question_type="short_answer",
                question=f"请简要说明：{card.title}",
                options=[],
                answer=card.summary,
                explanation=card.explanation,
                difficulty="medium",
                related_card_title=card.title,
            )
            for card in cards
        ]
    )
    try:
        await save_quiz_questions(questions)
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e
    return GenerateQuizResponse(questions=questions)


@router.get(
    "/card-system/quiz",
    summary="List quiz questions",
)
async def list_card_system_quiz(card_id: str | None = None) -> list[dict[str, Any]]:
    """List quiz questions, optionally filtered by card ID."""
    await _ensure_card_system_db()
    if card_id:
        await _get_cards_or_404(card_id)
    try:
        return await list_quiz_questions(card_id=card_id)
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e


@router.post(
    "/card-system/quiz/submit",
    response_model=SubmitAnswerResponse,
    summary="Submit and check an answer",
)
async def submit_card_system_answer(input: AnswerSubmission) -> SubmitAnswerResponse:
    """Submit an answer and automatically check it."""
    if not input.user_answer.strip():
        raise HTTPException(status_code=422, detail="user_answer cannot be empty")
    await _ensure_card_system_db()
    question = await _get_question_or_404(input.question_id)
    try:
        result = await check_answer(question, input)
        record = await save_answer_record(input, result)
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e
    except Exception as e:
        logger.error("Answer checking failed: %s", e)
        raise HTTPException(status_code=502, detail="Answer checking failed") from e
    return SubmitAnswerResponse(result=result, record=record)


@router.get(
    "/card-system/wrong-questions",
    summary="List wrong questions",
)
async def list_card_system_wrong_questions() -> list[dict[str, Any]]:
    """List wrong questions for the default user."""
    await _ensure_card_system_db()
    try:
        return await list_wrong_questions()
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e


@router.post(
    "/card-system/review-plan/generate",
    response_model=GenerateReviewPlanResponse,
    summary="Generate a review plan",
)
async def generate_card_system_review_plan(
    input: GenerateReviewPlanRequest,
) -> GenerateReviewPlanResponse:
    """Generate and save a review plan from weak points or wrong questions."""
    await _ensure_card_system_db()
    weak_points = input.weak_points
    if weak_points is None:
        try:
            wrong_questions = await list_wrong_questions()
        except CardSystemStorageError as e:
            raise _storage_exception(e) from e
        weak_points = [
            str(item.get("related_knowledge") or item.get("question") or "")
            for item in wrong_questions
        ]

    try:
        plan = await generate_review_plan(weak_points or [])
        record = await save_review_plan(plan, title=input.title or "知识卡片复习计划")
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e
    except Exception as e:
        logger.error("Review plan generation failed: %s", e)
        raise HTTPException(status_code=502, detail="Review plan generation failed") from e

    return GenerateReviewPlanResponse(plan=plan, record=record)


@router.get(
    "/card-system/study-summary",
    summary="Get study summary",
)
async def get_card_system_study_summary() -> dict[str, Any]:
    """Get aggregate study statistics."""
    await _ensure_card_system_db()
    try:
        summary = await get_study_summary()
    except CardSystemStorageError as e:
        raise _storage_exception(e) from e
    return summary.model_dump()


async def _handle_input(user_input: UserInput, agent: AgentGraph) -> tuple[dict[str, Any], UUID]:
    """
    Parse user input and handle any required interrupt resumption.
    Returns kwargs for agent invocation and the run_id.
    """
    run_id = uuid7()
    thread_id = user_input.thread_id or str(uuid4())
    user_id = user_input.user_id or str(uuid4())

    configurable = {"thread_id": thread_id, "user_id": user_id}
    if user_input.model is not None:
        configurable["model"] = user_input.model

    callbacks: list[Any] = []
    if settings.LANGFUSE_TRACING:
        # Initialize Langfuse CallbackHandler for Langchain (tracing)
        langfuse_handler = CallbackHandler()

        callbacks.append(langfuse_handler)

    if user_input.agent_config:
        # Check for reserved keys (including 'model' even if not in configurable)
        reserved_keys = {"thread_id", "user_id", "model"}
        if overlap := reserved_keys & user_input.agent_config.keys():
            raise HTTPException(
                status_code=422,
                detail=f"agent_config contains reserved keys: {overlap}",
            )
        configurable.update(user_input.agent_config)

    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
        callbacks=callbacks,
    )

    # Check for interrupts that need to be resumed
    state = await agent.aget_state(config=config)
    interrupted_tasks = [
        task for task in state.tasks if hasattr(task, "interrupts") and task.interrupts
    ]

    input: Command | dict[str, Any]
    if interrupted_tasks:
        # assume user input is response to resume agent execution from interrupt
        input = Command(resume=user_input.message)
    else:
        input = {"messages": [HumanMessage(content=user_input.message)]}

    kwargs = {
        "input": input,
        "config": config,
    }

    return kwargs, run_id


@router.post("/{agent_id}/invoke", operation_id="invoke_with_agent_id")
@router.post("/invoke")
async def invoke(user_input: UserInput, agent_id: str = DEFAULT_AGENT) -> ChatMessage:
    """
    Invoke an agent with user input to retrieve a final response.

    If agent_id is not provided, the default agent will be used.
    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to messages for recording feedback.
    Use user_id to persist and continue a conversation across multiple threads.
    """
    # NOTE: Currently this only returns the last message or interrupt.
    # In the case of an agent outputting multiple AIMessages (such as the background step
    # in interrupt-agent, or a tool step in research-assistant), it's omitted. Arguably,
    # you'd want to include it. You could update the API to return a list of ChatMessages
    # in that case.
    agent: AgentGraph = get_agent(agent_id)
    kwargs, run_id = await _handle_input(user_input, agent)

    try:
        response_events: list[tuple[str, Any]] = await agent.ainvoke(**kwargs, stream_mode=["updates", "values"])  # type: ignore # fmt: skip
        response_type, response = response_events[-1]
        if response_type == "values":
            # Normal response, the agent completed successfully
            output = langchain_to_chat_message(response["messages"][-1])
        elif response_type == "updates" and "__interrupt__" in response:
            # The last thing to occur was an interrupt
            # Return the value of the first interrupt as an AIMessage
            output = langchain_to_chat_message(
                AIMessage(content=response["__interrupt__"][0].value)
            )
        else:
            raise ValueError(f"Unexpected response type: {response_type}")

        output.run_id = str(run_id)
        return output
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")


async def message_generator(
    user_input: StreamInput, agent_id: str = DEFAULT_AGENT
) -> AsyncGenerator[str, None]:
    """
    Generate a stream of messages from the agent.

    This is the workhorse method for the /stream endpoint.
    """
    agent: AgentGraph = get_agent(agent_id)
    kwargs, run_id = await _handle_input(user_input, agent)

    try:
        # Process streamed events from the graph and yield messages over the SSE stream.
        async for stream_event in agent.astream(
            **kwargs, stream_mode=["updates", "messages", "custom"], subgraphs=True
        ):
            if not isinstance(stream_event, tuple):
                continue
            # Handle different stream event structures based on subgraphs
            if len(stream_event) == 3:
                # With subgraphs=True: (node_path, stream_mode, event)
                _, stream_mode, event = stream_event
            else:
                # Without subgraphs: (stream_mode, event)
                stream_mode, event = stream_event
            new_messages = []
            if stream_mode == "updates":
                for node, updates in event.items():
                    # A simple approach to handle agent interrupts.
                    # In a more sophisticated implementation, we could add
                    # some structured ChatMessage type to return the interrupt value.
                    if node == "__interrupt__":
                        interrupt: Interrupt
                        for interrupt in updates:
                            new_messages.append(AIMessage(content=interrupt.value))
                        continue
                    updates = updates or {}
                    update_messages = updates.get("messages", [])
                    # special cases for using langgraph-supervisor library
                    if "supervisor" in node or "sub-agent" in node:
                        # the only tools that come from the actual agent are the handoff and handback tools
                        if isinstance(update_messages[-1], ToolMessage):
                            if "sub-agent" in node and len(update_messages) > 1:
                                # If this is a sub-agent, we want to keep the last 2 messages - the handback tool, and it's result
                                update_messages = update_messages[-2:]
                            else:
                                # If this is a supervisor, we want to keep the last message only - the handoff result. The tool comes from the 'agent' node.
                                update_messages = [update_messages[-1]]
                        else:
                            update_messages = []
                    new_messages.extend(update_messages)

            if stream_mode == "custom":
                new_messages = [event]

            # LangGraph streaming may emit tuples: (field_name, field_value)
            # e.g. ('content', <str>), ('tool_calls', [ToolCall,...]), ('additional_kwargs', {...}), etc.
            # We accumulate only supported fields into `parts` and skip unsupported metadata.
            # More info at: https://langchain-ai.github.io/langgraph/cloud/how-tos/stream_messages/
            processed_messages = []
            current_message: dict[str, Any] = {}
            for message in new_messages:
                if isinstance(message, tuple):
                    key, value = message
                    # Store parts in temporary dict
                    current_message[key] = value
                else:
                    # Add complete message if we have one in progress
                    if current_message:
                        processed_messages.append(_create_ai_message(current_message))
                        current_message = {}
                    processed_messages.append(message)

            # Add any remaining message parts
            if current_message:
                processed_messages.append(_create_ai_message(current_message))

            for message in processed_messages:
                try:
                    chat_message = langchain_to_chat_message(message)
                    chat_message.run_id = str(run_id)
                except Exception as e:
                    logger.error(f"Error parsing message: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Unexpected error'})}\n\n"
                    continue
                # LangGraph re-sends the input message, which feels weird, so drop it
                if chat_message.type == "human" and chat_message.content == user_input.message:
                    continue
                yield f"data: {json.dumps({'type': 'message', 'content': chat_message.model_dump()})}\n\n"

            if stream_mode == "messages":
                if not user_input.stream_tokens:
                    continue
                msg, metadata = event
                if "skip_stream" in metadata.get("tags", []):
                    continue
                # For some reason, astream("messages") causes non-LLM nodes to send extra messages.
                # Drop them.
                if not isinstance(msg, AIMessageChunk):
                    continue
                content = remove_tool_calls(msg.content)
                if content:
                    # Empty content in the context of OpenAI usually means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content.
                    yield f"data: {json.dumps({'type': 'token', 'content': convert_message_content_to_string(content)})}\n\n"
    except Exception as e:
        logger.error(f"Error in message generator: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'Internal server error'})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


def _create_ai_message(parts: dict) -> AIMessage:
    sig = inspect.signature(AIMessage)
    valid_keys = set(sig.parameters)
    filtered = {k: v for k, v in parts.items() if k in valid_keys}
    return AIMessage(**filtered)


def _sse_response_example() -> dict[int | str, Any]:
    return {
        status.HTTP_200_OK: {
            "description": "Server Sent Event Response",
            "content": {
                "text/event-stream": {
                    "example": "data: {'type': 'token', 'content': 'Hello'}\n\ndata: {'type': 'token', 'content': ' World'}\n\ndata: [DONE]\n\n",
                    "schema": {"type": "string"},
                }
            },
        }
    }


@router.post(
    "/{agent_id}/stream",
    response_class=StreamingResponse,
    responses=_sse_response_example(),
    operation_id="stream_with_agent_id",
)
@router.post("/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def stream(user_input: StreamInput, agent_id: str = DEFAULT_AGENT) -> StreamingResponse:
    """
    Stream an agent's response to a user input, including intermediate messages and tokens.

    If agent_id is not provided, the default agent will be used.
    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to all messages for recording feedback.
    Use user_id to persist and continue a conversation across multiple threads.

    Set `stream_tokens=false` to return intermediate messages but not token-by-token.
    """
    return StreamingResponse(
        message_generator(user_input, agent_id),
        media_type="text/event-stream",
    )


@router.post("/feedback")
async def feedback(feedback: Feedback) -> FeedbackResponse:
    """
    Record feedback for a run to LangSmith.

    This is a simple wrapper for the LangSmith create_feedback API, so the
    credentials can be stored and managed in the service rather than the client.
    See: https://api.smith.langchain.com/redoc#tag/feedback/operation/create_feedback_api_v1_feedback_post
    """
    client = LangsmithClient()
    kwargs = feedback.kwargs or {}
    client.create_feedback(
        run_id=feedback.run_id,
        key=feedback.key,
        score=feedback.score,
        **kwargs,
    )
    return FeedbackResponse()


@router.post("/history")
async def history(input: ChatHistoryInput) -> ChatHistory:
    """
    Get chat history.
    """
    # TODO: Hard-coding DEFAULT_AGENT here is wonky
    agent: AgentGraph = get_agent(DEFAULT_AGENT)
    try:
        state_snapshot = await agent.aget_state(
            config=RunnableConfig(configurable={"thread_id": input.thread_id})
        )
        messages: list[AnyMessage] = state_snapshot.values["messages"]
        chat_messages: list[ChatMessage] = [langchain_to_chat_message(m) for m in messages]
        return ChatHistory(messages=chat_messages)
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")


@app.get("/health")
async def health_check():
    """Health check endpoint."""

    health_status = {"status": "ok"}

    if settings.LANGFUSE_TRACING:
        try:
            langfuse = Langfuse()
            health_status["langfuse"] = "connected" if langfuse.auth_check() else "disconnected"
        except Exception as e:
            logger.error(f"Langfuse connection error: {e}")
            health_status["langfuse"] = "disconnected"

    return health_status


app.include_router(router)
