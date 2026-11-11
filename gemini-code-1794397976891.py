import streamlit as st
import re

st.set_page_config(page_title="국어 서·논술형 자동 채점 시스템", layout="wide")

st.title("📝 국어 서·논술형 3번 자동 채점 시스템")
st.markdown("---")

# ==========================================
# 채점 로직 함수 정의
# ==========================================

def grade_question_1(ans_a, ans_b):
    score_a = 0.0
    score_b = 0.0
    feedback_a = ""
    feedback_b = ""

    # 키워드 정의
    a_valid_keywords = ["공부", "학업", "교과서", "학습", "수업"]
    a_wrong_keywords = ["일상", "여가", "나들이", "소풍", "놀이", "휴식"]

    b_valid_keywords = ["일상", "여가", "나들이", "소풍", "놀이", "삶", "다양한"]
    b_wrong_keywords = ["공부만", "학업 전용", "교과서 전용"]

    # ㉠ 채점
    ans_a_clean = ans_a.strip()
    if not ans_a_clean:
        feedback_a = "답안이 작성되지 않았습니다."
    elif any(kw in ans_a_clean for kw in a_wrong_keywords):
        feedback_a = "오개념 감점: ㉠에 일상/여가 관련 성격이 잘못 기술되었습니다."
    elif any(kw in ans_a_clean for kw in a_valid_keywords):
        score_a = 1.5
        feedback_a = "정답: 가방을 학업/공부의 도구로 보는 관점이 정확히 드러났습니다."
    else:
        feedback_a = "부분 감점/오답: 학업 및 공부와 관련된 수단임을 명확히 표현해야 합니다."

    # ㉡ 채점
    ans_b_clean = ans_b.strip()
    if not ans_b_clean:
        feedback_b = "답안이 작성되지 않았습니다."
    elif any(kw in ans_b_clean for kw in b_wrong_keywords):
        feedback_b = "오개념 감점: ㉡에 학업 전용 특성이 잘못 기술되었습니다."
    elif any(kw in ans_b_clean for kw in b_valid_keywords):
        score_b = 1.5
        feedback_b = "정답: 가방을 일상/여가/나들이의 도구로 보는 관점이 정확히 드러났습니다."
    else:
        feedback_b = "부분 감점/오답: 일상이나 여가, 나들이의 수단임을 명확히 표현해야 합니다."

    return score_a, feedback_a, score_b, feedback_b


def grade_question_2(ans_text):
    score_format = 0.0
    score_intent = 0.0
    score_evidence = 0.0

    fb_format = ""
    fb_intent = ""
    fb_evidence = ""

    text = ans_text.strip()

    if not text:
        return 0.0, "❌ 답안 미작성", "❌ 답안 미작성", "❌ 답안 미작성"

    # 문장 틀 정규표현식 검사
    # 틀: 광고를 본 사람이 (A) 하게 하려 한다. 그렇게 생각한 근거는 광고의 (B) 때문이다.
    pattern = r"광고를\s*본\s*사람이\s*(.+?)\s*하게\s*하려\s*한다\.\s*그렇게\s*생각한\s*근거는\s*광고의\s*(.+?)\s*때문이다\.?"
    match = re.search(pattern, text)

    if not match:
        fb_format = "❌ 문장 틀 미준수: 제시된 조건의 문장 구조를 정확히 따라 작성해야 합니다."
        part_intent = text
        part_evidence = text
    else:
        score_format = 1.0
        fb_format = "⭕ 문장 틀 준수 (+1.0점)"
        part_intent = match.group(1)
        part_evidence = match.group(2)

    # 1. 의도(A) 검사
    intent_keywords = ["사게", "구매", "살 수 있게", "선택", "사도록", "구입"]
    if any(kw in part_intent for kw in intent_keywords):
        score_intent = 1.0
        fb_intent = "⭕ 의도 작성 완벽: 소비 유도/구매 목적이 명확히 드러남 (+1.0점)"
    else:
        fb_intent = "❌ 의도 감점: 광고를 본 사람이 가방을 '구매하게/사게' 하려는 결론 의도가 부족합니다."

    # 2. 근거(B) 검사 (수정 전 광고 근거 필수)
    before_ad_keywords = ["교과서", "거뜬히", "35L", "수납", "공부", "오늘", "내일", "멋진", "더 나은", "열심히"]
    after_ad_keywords = ["돗자리", "나들이", "월요일", "공원", "물병", "간식"]

    if any(kw in part_evidence for kw in after_ad_keywords):
        fb_evidence = "❌ 근거 0점 (오개념/조건 위반): '수정 전 광고'가 아닌 '수정 후 광고'의 내용을 근거로 제시했습니다."
        score_evidence = 0.0
    elif any(kw in part_evidence for kw in before_ad_keywords):
        score_evidence = 1.0
        fb_evidence = "⭕ 근거 작성 완벽: 수정 전 광고의 문구/시각 자료를 적절히 인용함 (+1.0점)"
    else:
        fb_evidence = "❌ 근거 감점: 수정 전 광고에 나타난 시각 자료나 문구(교과서 수납, 공부 관련 문구 등)를 명시해야 합니다."

    total_q2 = score_format + score_intent + score_evidence
    return total_q2, fb_format, fb_intent, fb_evidence


# ==========================================
# Streamlit UI 구성
# ==========================================

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 문제 및 답안 입력")
    
    st.markdown("### [서·논술형 3-(1)] (3점)")
    st.caption("㉠, ㉡에 들어갈 적절한 표현을 쓰시오.")
    ans_1_a = st.text_input("㉠ 답안:", placeholder="예: 공부하는 도구")
    ans_1_b = st.text_input("㉡ 답안:", placeholder="예: 일상생활에서 쓰는 나들이 도구")

    st.markdown("---")
    
    st.markdown("### [서·논술형 3-(2)] (3점)")
    st.caption("아래 문장 틀에 맞추어 서술하시오.")
    st.info("💡 **문장 틀:** 광고를 본 사람이 ( A ) 하게 하려 한다. 그렇게 생각한 근거는 광고의 ( B ) 때문이다.")
    
    # 예시 답안(value)을 지우고 빈칸 상태로 두고 placeholder로 힌트만 제공
    ans_2 = st.text_area(
        "답안 전체 입력:", 
        value="", 
        placeholder="광고를 본 사람이 (   ) 하게 하려 한다. 그렇게 생각한 근거는 광고의 (   ) 때문이다.", 
        height=120
    )

    submit_btn = st.button("🚀 자동 채점 실행", type="primary")

with col2:
    st.subheader("📊 채점 결과 및 피드백")
    
    if submit_btn:
        # 1번 문항 채점
        score_1_a, fb_1_a, score_1_b, fb_1_b = grade_question_1(ans_1_a, ans_1_b)
        total_1 = score_1_a + score_1_b

        # 2번 문항 채점
        total_2, fb_fmt, fb_int, fb_evi = grade_question_2(ans_2)

        grand_total = total_1 + total_2

        # 총점 표시
        st.metric(label="총점", value=f"{grand_total} / 6.0 점")
        st.progress(grand_total / 6.0)

        # 문항 1 결과
        with st.expander("📌 (1)번 문항 상세 채점 (3.0점 만점)", expanded=True):
            st.write(f"**㉠ 점수:** {score_1_a} / 1.5점")
            st.caption(fb_1_a)
            st.write(f"**㉡ 점수:** {score_1_b} / 1.5점")
            st.caption(fb_1_b)

        # 문항 2 결과
        with st.expander("📌 (2)번 문항 상세 채점 (3.0점 만점)", expanded=True):
            st.write(f"**총점:** {total_2} / 3.0점")
            st.markdown(f"- **문장 틀 검사:** {fb_fmt}")
            st.markdown(f"- **제작자 의도 검사:** {fb_int}")
            st.markdown(f"- **근거 제시 검사:** {fb_evi}")
