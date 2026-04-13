import streamlit as st
import pandas as pd
from ai_engine import find_all_equivalences

# ─────────────────────────────────────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Section Card ── */
.scard {
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 24px rgba(15,31,61,.10);
    margin-bottom: 20px;
}
.scard-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: #0f1f3d;
    margin-bottom: 15px;
    border-bottom: 2px solid #f1f5f9;
    padding-bottom: 10px;
}

/* ── Buttons ── */
.stButton > button {
    background: #0d9488 !important;
    color: #fff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


def enter_data():
    
    # ─── زر العودة للصفحة الرئيسية ───
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

    # Initialize Session State for lists
    if 'old_courses_list' not in st.session_state:
        st.session_state.old_courses_list = []
    if 'new_courses_list' not in st.session_state:
        st.session_state.new_courses_list = []

    tab1, tab2 = st.tabs(["Old Course Entry", "New Course Entry"])

    # ----- Old Course Tab -----
    with tab1:
        st.markdown('<div class="scard"><div class="scard-title">Old Course Form</div>', unsafe_allow_html=True)
        
        # Show list
        if st.session_state.old_courses_list:
            st.write(f"**Added ({len(st.session_state.old_courses_list)}):**")
            # عرض القائمة الحالية للتأكد
            st.dataframe(pd.DataFrame(st.session_state.old_courses_list), use_container_width=True)

        with st.form("old_course_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                old_course_code = st.text_input("Course Code")
                old_course_name = st.text_input("Course Name")
            with col2:
                old_credit_hours = st.number_input("Credit Hours", min_value=0, max_value=6, value=3)
                # تغيير حقل العلامة ليكون رقمياً مباشرة لضمان عدم وجود فواصل
                old_grade = st.number_input("Grade", min_value=0, max_value=100, value=0, step=1)
            
            old_description = st.text_area("Course Description", height=100)
            
            submitted_old = st.form_submit_button("Add Course", use_container_width=True)

            if submitted_old and old_course_code:
                st.session_state.old_courses_list.append({
                    'course_code': old_course_code,
                    'course_name': old_course_name,
                    'description': old_description,
                    'credit_hours': old_credit_hours,
                    'grade': int(old_grade) # التخزين كعدد صحيح
                })
                st.success("Added!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # ------ New Course Tab ------
    with tab2:
        st.markdown('<div class="scard"><div class="scard-title">New Course Form</div>', unsafe_allow_html=True)
        
        if st.session_state.new_courses_list:
            st.write(f"**Added ({len(st.session_state.new_courses_list)}):**")
            st.dataframe(pd.DataFrame(st.session_state.new_courses_list), use_container_width=True)

        with st.form("new_course_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_course_code = st.text_input("Course Code")
                new_course_name = st.text_input("Course Name")
            with col2:
                new_credit_hours = st.number_input("Credit Hours", min_value=0, max_value=6, value=3)
            
            new_description = st.text_area("Course Description", height=100)

            submitted_new = st.form_submit_button("Add Course", use_container_width=True)

            if submitted_new and new_course_code:
                st.session_state.new_courses_list.append({
                    'course_code': new_course_code,
                    'course_name': new_course_name,
                    'description': new_description,
                    'credit_hours': new_credit_hours
                })
                st.success("Added!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Analysis Section
    st.markdown('<div class="scard" style="text-align:center; padding: 40px;">', unsafe_allow_html=True)
    st.markdown('<div class="scard-title">Ready to Analyze?</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
        if not st.session_state.old_courses_list or not st.session_state.new_courses_list:
            st.warning("Please add at least one course to each list.")
        else:
            with st.spinner("AI is working..."):
                old_courses_df = pd.DataFrame(st.session_state.old_courses_list)
                new_courses_df = pd.DataFrame(st.session_state.new_courses_list)

                all_equivalences = find_all_equivalences(old_courses_df, new_courses_df)

                if all_equivalences:
                    results_df = pd.DataFrame(all_equivalences)
                    
                    display_df = results_df.rename(columns={
                        'old_course_code': 'Old Code', 'old_course_name': 'Old Name',
                        'new_course_code': 'New Code', 'new_course_name': 'New Name',
                        'similarity_score': 'Match %', 'new_credit_hours': 'Credits'
                    })
                    display_df['Match %'] = (display_df['Match %'] * 100).round(2).astype(str) + '%'
                    
                    # التأكد من عرض العلامة كعدد صحيح
                    if 'grade' in display_df.columns:
                         display_df['grade'] = pd.to_numeric(display_df['grade'], errors='coerce').astype('Int64')

                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("No matches found.")
    
    st.markdown('</div>', unsafe_allow_html=True)