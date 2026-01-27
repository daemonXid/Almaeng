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
    Handle message submission (HTMX, 대화형 상담)
    
    ✅ Multi-turn 대화:
    - 이전 대화 컨텍스트 유지
    - 추가 질문에 맥락있게 답변
    """
    content = request.POST.get("message", "").strip()
    if not content:
        return HttpResponse("")

    # 사용자 프로필 가져오기 (개인화 추천)
    user_age = request.POST.get("user_age", "")
    user_gender = request.POST.get("user_gender", "")
    
    # 프로필 컨텍스트 생성
    profile_context = ""
    if user_age or user_gender:
        profile_context = "\n\n[사용자 정보: "
        if user_age:
            profile_context += f"{user_age}세, "
        if user_gender == "male":
            profile_context += "남성"
        elif user_gender == "female":
            profile_context += "여성"
        profile_context += "]"

    # 영양제 질문인지 확인
    nutrition_keywords = ["영양제", "비타민", "미네랄", "보충제", "건강", "피로", "면역", "오메가", "프로바이오틱스", "유산균", "칼슘", "철분", "아연", "마그네슘", "단백질", "콜라겐", "루테인", "홍삼", "BCAA", "글루타민", "관절", "눈", "간", "장", "혈당", "콜레스테롤"]
    is_nutrition_question = any(kw in content for kw in nutrition_keywords)
    
    if not is_nutrition_question:
        # 영양제 관련 질문이 아니면 거부
        answer = "죄송합니다. 저는 **영양제 전문 상담 AI**입니다. 영양제, 건강보조식품에 대한 질문만 답변해드릴 수 있어요. 😊\n\n예를 들어 이렇게 물어보세요:\n- 피로할 때 좋은 영양제는?\n- 눈 건강에 좋은 루테인 추천해줘\n- 관절 건강을 위한 MSM"
        keywords = []
        all_keywords = []
    else:
        # 이전 대화 컨텍스트 가져오기 (Multi-turn)
        messages = request.session.get("chat_messages", [])
        conversation_context = ""
        if messages:
            # 최근 3개 대화만 컨텍스트로 사용
            recent_messages = messages[-6:]  # user + assistant 쌍 3개
            context_parts = []
            for msg in recent_messages:
                role = "사용자" if msg["role"] == "user" else "AI"
                context_parts.append(f"{role}: {msg['content'][:100]}")
            conversation_context = "\n".join(context_parts)
        
        # Gemini로 키워드 추출
        from domains.integrations.gemini.interface import extract_keywords
        
        try:
            keyword_result = extract_keywords(content)
            keywords = keyword_result.keywords if keyword_result.keywords else []
        except Exception:
            keywords = []
        
        # Get AI Response (대화 컨텍스트 포함)
        try:
            full_prompt = content
            if conversation_context:
                full_prompt = f"[이전 대화]\n{conversation_context}\n\n[현재 질문]\n{content}"
            if profile_context:
                full_prompt += profile_context
            
            response = ask_question(
                question=full_prompt,
                system_instruction="""당신은 알맹AI의 영양제 전문 상담 AI입니다.

**역할**:
- 영양제와 건강보조식품에 대해서만 답변
- 5060 세대도 쉽게 이해할 수 있도록 친근하고 간단하게 설명
- 전문 용어는 쉬운 말로 풀어서 설명
- 이전 대화를 기억하고 맥락있게 답변
- 영양제 조합 분석 (함께 먹으면 좋은 것, 피해야 할 조합)

**답변 형식**:
1. 질문에 대한 간단한 설명 (2-3문장)
2. 추천 영양제 (구체적인 성분명)
3. 복용 시간 및 주의사항 (간단히)
4. 함께 먹으면 좋은 조합 (있다면)
5. 마지막 줄에 반드시: "키워드: 성분1, 성분2, 성분3, ..." (최대 12개)

**조합 분석 예시**:
- "비타민D와 칼슘은 함께 드시면 흡수율이 높아집니다."
- "철분은 커피/차와 함께 드시면 흡수가 방해됩니다."
- "오메가3는 혈액 순환을 돕는 은행잎과 함께 주의하세요."

**대화 예시**:
사용자: "피로할 때 좋은 영양제는?"
AI: "비타민B 컴플렉스를 추천드립니다..."
사용자: "그럼 언제 먹는게 좋아요?" (추가 질문)
AI: "비타민B는 아침 식사 후에 드시는 것이 가장 좋습니다..." (맥락 유지)
사용자: "마그네슘도 같이 먹어도 되나요?" (조합 질문)
AI: "네! 비타민B와 마그네슘은 함께 드시면 시너지 효과가 있습니다..." (조합 분석)
""",
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
                        ai_keywords = [k.strip() for k in keyword_line.split(",")[:12]]
                        # 키워드 라인 제거
                        answer = answer.split(delimiter)[0].strip()
                        break
            
            # Gemini 추출 키워드와 AI 답변 키워드 합치기
            all_keywords = list(dict.fromkeys(keywords + ai_keywords))[:12]  # 중복 제거, 최대 12개
            
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


