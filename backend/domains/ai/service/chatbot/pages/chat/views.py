"""
🌐 Chatbot Views

HTMX views for the chat interface.
"""

from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from ...interface import ask_question, index_project, search_project, stream_question


def chat_page(request: HttpRequest) -> HttpResponse:
    """Main chat page."""
    # Ensure project is indexed
    index_project()

    return render(request, "ai/chatbot/pages/chat/chat.html")


@require_http_methods(["POST"])
def send_message(request: HttpRequest) -> HttpResponse:
    """
    Handle chat message submission.
    Returns HTMX fragment with response.
    """
    question = request.POST.get("question", "").strip()

    if not question:
        return render(
            request,
            "ai/chatbot/pages/chat/_message.html",
            {"role": "assistant", "content": "질문을 입력해주세요."},
        )

    # Get AI response
    response = ask_question(question)

    return render(
        request,
        "ai/chatbot/pages/chat/_message.html",
        {
            "role": "assistant",
            "content": response.answer,
            "sources": response.sources,
        },
    )


@require_http_methods(["GET"])
def stream_message(request: HttpRequest) -> StreamingHttpResponse:
    """
    Stream AI response chunks using SSE.
    """
    question = request.GET.get("question", "").strip()

    def event_stream():
        if not question:
            yield "data: <div>질문을 입력해주세요.</div>\n\n"
            return

        yield "data: <div class='chat-message assistant'>\n\n"
        for chunk in stream_question(question):
            yield f"data: {chunk}\n\n"
        yield "data: </div>\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    return response


@require_http_methods(["POST"])
def search(request: HttpRequest) -> HttpResponse:
    """
    Search project files.
    Returns HTMX fragment with results.
    """
    query = request.POST.get("query", "").strip()

    if not query:
        return HttpResponse("")

    results = search_project(query)

    return render(
        request,
        "chatbot/_search_results.html",
        {"results": results},
    )
