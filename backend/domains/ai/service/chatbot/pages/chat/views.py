"""
🌐 Chatbot Views

Full-page Claude-style chatbot with persistent history.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from domains.ai.service.chatbot.models import ChatMessage, ChatSession

# ✅ DAEMON Rule: Import from interface.py only
from ...interface import ask_question


def chat_page(request: HttpRequest, session_id: int | None = None) -> HttpResponse:
    """
    Main Chat Interface (Claude Style)
    """
    context = {}

    # Load Sidebar History (Only for logged-in users)
    if request.user.is_authenticated:
        sessions = ChatSession.objects.filter(user=request.user, is_active=True)
        context["sessions"] = sessions

        # Load Active Session
        if session_id:
            active_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            context["active_session"] = active_session
            context["messages"] = active_session.messages.all()
        else:
            # New Chat State
            context["active_session"] = None
            context["messages"] = []

    return render(request, "chat_page.html", context)


@require_http_methods(["POST"])
def send_message(request: HttpRequest, session_id: int | None = None) -> HttpResponse:
    """
    Handle message submission (HTMX)
    """
    content = request.POST.get("message", "").strip()
    if not content:
        return HttpResponse("")

    # 1. Get or Create Session
    session = None
    if session_id and request.user.is_authenticated:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    elif request.user.is_authenticated:
        # Create new session on first message
        # Use first 30 chars as title
        title = content[:30] + "..." if len(content) > 30 else content
        session = ChatSession.objects.create(user=request.user, title=title)

    # 2. Save User Message (if session exists)
    if session:
        ChatMessage.objects.create(session=session, role="user", content=content)

    # 3. Get AI Response
    try:
        # ✅ DAEMON Pattern: Use interface function
        response = ask_question(
            question=content,
            system_instruction="당신은 알맹AI의 쇼핑 도우미입니다. 친근하게 상품을 추천해주세요.",
        )
        answer = response.answer
        sources = response.sources or []
    except Exception as e:
        answer = f"죄송합니다. 오류가 발생했습니다: {e}"
        sources = []

    # 4. Save AI Message
    if session:
        ChatMessage.objects.create(session=session, role="assistant", content=answer, sources=sources)

    # 5. Render Response Fragment
    # If it was a new session, we need to redirect to the new URL to update history list
    # But HTMX handles this better with OOB or client-side redirect.
    # For simplicity, if new session, return header to redirect.
    if session and not session_id:
        response_obj = HttpResponse()
        response_obj["HX-Redirect"] = f"/chatbot/{session.id}/"
        return response_obj

    # Render message bubbles (User + AI)
    return render(
        request, "_message_fragment.html", {"user_message": content, "ai_message": answer, "sources": sources}
    )


@login_required
def new_chat(request: HttpRequest) -> HttpResponse:
    """Redirect to clean chat page"""
    return redirect("ai_chatbot:chat_home")


# ============================================
# 앱인토스용 Simple Chat (세션 저장 없음)
# ============================================

def simple_chat_page(request: HttpRequest) -> HttpResponse:
    """Simple AI chat page (앱인토스용)"""
    return render(request, "chatbot/pages/chat/simple_chat.html")


@require_http_methods(["POST"])
def simple_chat_send(request: HttpRequest) -> HttpResponse:
    """
    Send message to AI and get response with keywords

    Flow:
    1. User asks: "피로할 때 좋은 영양제는?"
    2. AI responds with explanation + keywords
    3. User clicks keyword → redirect to search
    """
    user_message = request.POST.get("message", "").strip()

    if not user_message:
        return HttpResponse("")

    # Get AI response
    try:
        # Gemini AI with keyword extraction

        response = ask_question(
            question=user_message,
            system_instruction="당신은 영양제 전문 상담사입니다. 간결하고 정확하게 답변하세요.",
        )

        answer = response.answer

        # Extract keywords from response
        keywords = []
        if "키워드:" in answer:
            keyword_line = answer.split("키워드:")[-1].strip()
            keywords = [k.strip() for k in keyword_line.split(",")[:3]]
            # Remove keyword line from answer
            answer = answer.split("키워드:")[0].strip()

    except Exception as e:
        answer = f"죄송합니다. 오류가 발생했습니다: {e!s}"
        keywords = []

    # Return HTML fragment
    return render(
        request,
        "chatbot/pages/chat/_ai_response.html",
        {
            "answer": answer,
            "keywords": keywords,
        }
    )


@require_http_methods(["DELETE"])
@login_required
def delete_session(request: HttpRequest, session_id: int) -> HttpResponse:
    """Delete a chat session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.is_active = False  # Soft delete
    session.save()
    return HttpResponse("")  # Helper to remove element in UI
