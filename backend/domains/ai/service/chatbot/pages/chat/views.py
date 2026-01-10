"""
🌐 Chatbot Views

HTMX views for the chat interface (캐치 🐤).
"""

from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods

from domains.ai.service.chatbot.gemini_service import ask_supplement_question


@require_http_methods(["POST"])
def send_message(request: HttpRequest) -> HttpResponse:
    """
    Handle chat message submission.
    Returns HTMX fragment with response.
    """
    question = request.POST.get("message", "").strip()

    if not question:
        return HttpResponse(
            """<div class="flex gap-3 mb-4">
                <img src="/static/images/catch_mascot.png" alt="캐치" class="w-8 h-8 rounded-full object-cover shrink-0">
                <div class="flex-1 p-3 rounded-xl bg-gray-100 dark:bg-gray-800 text-sm">
                    <p>질문을 입력해주세요! 🐤</p>
                </div>
            </div>"""
        )

    try:
        # Get AI response
        response = ask_supplement_question(question)

        # Build sources HTML if available
        sources_html = ""
        if response.sources:
            source_items = "".join(
                [
                    f'<span class="px-2 py-1 bg-emerald-100 dark:bg-emerald-900/50 rounded text-xs">{s["name"]}</span>'
                    for s in response.sources[:3]
                ]
            )
            sources_html = f'<div class="flex gap-2 mt-2 flex-wrap">{source_items}</div>'

        return HttpResponse(f"""
            <div class="flex gap-3 mb-4">
                <img src="/static/images/catch_mascot.png" alt="캐치" class="w-8 h-8 rounded-full object-cover shrink-0">
                <div class="flex-1 p-3 rounded-xl bg-gray-100 dark:bg-gray-800 text-sm">
                    <p class="whitespace-pre-wrap">{response.answer}</p>
                    {sources_html}
                </div>
            </div>
        """)
    except Exception as e:
        return HttpResponse(f"""
            <div class="flex gap-3 mb-4">
                <img src="/static/images/catch_mascot.png" alt="캐치" class="w-8 h-8 rounded-full object-cover shrink-0">
                <div class="flex-1 p-3 rounded-xl bg-red-100 dark:bg-red-900/50 text-sm text-red-800 dark:text-red-200">
                    <p>앗, 잠시 문제가 생겼어요! 🐤</p>
                    <p class="text-xs mt-1 opacity-70">{e!s}</p>
                </div>
            </div>
        """)


@require_http_methods(["GET"])
def get_messages(request: HttpRequest) -> HttpResponse:
    """
    Load chat history (placeholder for now).
    """
    return HttpResponse("")


def chat_page(request: HttpRequest) -> HttpResponse:
    """Main chat page (if accessed directly)."""
    from django.shortcuts import redirect

    return redirect("/")


def stream_message(request: HttpRequest) -> HttpResponse:
    """Streaming placeholder."""
    return HttpResponse("Streaming not implemented")


def search(request: HttpRequest) -> HttpResponse:
    """Search placeholder."""
    return HttpResponse("")
