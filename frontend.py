import streamlit as st
import backend as be

st.title("RPG 캐릭터/무기 생성기")

left_col, right_col = st.columns(2)

# --- 캐릭터 생성 (왼쪽) ---
with left_col:
    st.subheader("캐릭터 생성")
    name = st.text_input("캐릭터 이름", value="엘라", key="char_name")
    char_desc = st.text_area("캐릭터 설명", value="용감하고 빠른 도적. 치명타와 회피에 능함.", key="char_desc")
    if st.button("캐릭터 스탯 생성", key="make_char"):
        with st.spinner("캐릭터 스탯 생성 중..."):
            result = be.generate_character_stat(name, char_desc)
            st.success("캐릭터 스탯 결과:")
            st.code(result, language="json")

# --- 무기 생성 (오른쪽) ---
with right_col:
    st.subheader("무기 생성")
    weapon_desc = st.text_area("무기 설명", value="작고 날카로운 단검. 독 효과를 가짐.", key="weapon_desc")
    if st.button("무기 정보 생성", key="make_weapon"):
        with st.spinner("무기 정보 생성 중..."):
            result = be.generate_weapon_stat(weapon_desc)
            st.success("무기 JSON 결과:")
            st.code(result, language="json")