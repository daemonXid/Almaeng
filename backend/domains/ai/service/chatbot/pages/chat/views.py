"""
🌐 Chatbot Views

Full-page Claude-style chatbot with persistent history.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# ✅ DAEMON Rule: Import from interface.py only
from ...interface import ask_question


def chat_page(request: HttpRequest, session_id: int | None = None) -> HttpResponse:
    """
    Simple Chat Interface (세션 기반)
    
    앱인토스 출시 시 Toss 사용자 ID로 히스토리 관리 예정
    현재는 세션 기반 단순 구현
    """
    # 세션에서 채팅 히스토리 가져오기
    messages = request.session.get("chat_messages", [])
    
    context = {
        "messages": messages,
        "session_id": None,
        "sessions": [],
    }
    
    return render(request, "ai/service/chatbot/pages/chat/simple_chat.html", context)


@require_http_methods(["POST"])
def send_message(request: HttpRequest, session_id: int | None = None) -> HttpResponse:
    """
    Handle message submission (HTMX, 세션 기반)
    """
    content = request.POST.get("message", "").strip()
    if not content:
        return HttpResponse("")

    # Gemini로 키워드 추출
    from domains.integrations.gemini.interface import extract_keywords
    
    try:
        keyword_result = extract_keywords(content)
        keywords = keyword_result.keywords if keyword_result.keywords else []
    except Exception:
        keywords = []
    
    # Get AI Response
    try:
        response = ask_question(
            question=content,
            system_instruction="당신은 알맹AI의 쇼핑 도우미입니다. 친근하게 상품을 추천해주세요. 답변 끝에 관련 검색 키워드 3개를 추출하여 '키워드: A, B, C' 형식으로 제공하세요.",
        )
        answer = response.answer
        sources = response.sources or []
        
        # AI 답변에서도 키워드 추출
        ai_keywords = []
        if "키워드:" in answer or "검색어:" in answer:
            # 키워드 라인 찾기
            for delimiter in ["키워드:", "검색어:"]:
                if delimiter in answer:
                    keyword_line = answer.split(delimiter)[-1].strip()
                    ai_keywords = [k.strip() for k in keyword_line.split(",")[:3]]
                    # 키워드 라인 제거
                    answer = answer.split(delimiter)[0].strip()
                    break
        
        # Gemini 추출 키워드와 AI 답변 키워드 합치기
        all_keywords = list(dict.fromkeys(keywords + ai_keywords))[:5]  # 중복 제거, 최대 5개
        
    except Exception as e:
        answer = f"죄송합니다. 오류가 발생했습니다: {e}"
        sources = []
        all_keywords = keywords

    # 세션에 저장
    messages = request.session.get("chat_messages", [])
    messages.append({"role": "user", "content": content})
    messages.append({"role": "assistant", "content": answer, "sources": sources, "keywords": all_keywords})
    request.session["chat_messages"] = messages[-20:]  # 최근 20개만 유지
    request.session.modified = True

    # Render message bubbles
    return render(
        request, "_message_fragment.html", {
            "user_message": content, 
            "ai_message": answer, 
            "sources": sources,
            "keywords": all_keywords
        }
    )


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


