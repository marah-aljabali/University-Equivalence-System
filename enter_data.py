import streamlit as st
import pandas as pd
from ai_engine import find_all_equivalences

def enter_data():
  st.title("Data Entry Form")
  
  # تهيئة القوائم في session_state إذا لم تكن موجودة
  if 'old_courses_list' not in st.session_state:
    st.session_state.old_courses_list = []
  if 'new_courses_list' not in st.session_state:
    st.session_state.new_courses_list = []

  tab1, tab2 = st.tabs(["Old Course Entry", "New Course Entry"])

  # ----- Old Course Tab -----
  with tab1:
    st.header("Old Course Information")
    
    # عرض المواد المضافة حتى الآن
    if st.session_state.old_courses_list:
        st.write(f"**Added Courses ({len(st.session_state.old_courses_list)}):**")
        st.dataframe(pd.DataFrame(st.session_state.old_courses_list))

    with st.form("old_course_form", clear_on_submit=True):
      old_course_code = st.text_input("Old Course Code")
      old_course_name = st.text_input("Old Course Name")
      old_description = st.text_input("Old Course Description")
      old_credit_hours = st.number_input("Old Course Credit Hours", min_value=0, max_value=120)
      # إضافة حقل العلامة هنا لأن الموديل يحتاجه في المعادلة
      old_grade = st.text_input("Old Grade (e.g., 85)", value="85") 
      
      submitted_old = st.form_submit_button("Add Old Course")

      if submitted_old and old_course_code:
        st.session_state.old_courses_list.append({
          'course_code': old_course_code,
          'course_name': old_course_name,
          'description': old_description,
          'credit_hours': old_credit_hours,
          'grade': old_grade # إضافة العلامة للقائمة
        })
        st.success(f"Added: {old_course_code}")
        st.rerun() # إعادة تحميل الصفحة لتحديث العرض

  # ------ New Course Tab ------
  with tab2:
    st.header("New Course Information")
    
    if st.session_state.new_courses_list:
        st.write(f"**Added Courses ({len(st.session_state.new_courses_list)}):**")
        st.dataframe(pd.DataFrame(st.session_state.new_courses_list))

    with st.form("new_course_form", clear_on_submit=True):
      new_course_code = st.text_input("New Course Code")
      new_course_name = st.text_input("New Course Name")
      new_description = st.text_input("New Course Description")
      new_credit_hours = st.number_input("New Course Credit Hours", min_value=0, max_value=120)

      submitted_new = st.form_submit_button("Add New Course")

      if submitted_new and new_course_code:
        st.session_state.new_courses_list.append({
          'course_code': new_course_code,
          'course_name': new_course_name,
          'description': new_description,
          'credit_hours': new_credit_hours
        })
        st.success(f"Added: {new_course_code}")
        st.rerun()

  st.markdown("---")
  
  # زر التحليل
  if st.button("Start Analysis", type="primary", use_container_width=True):
    if not st.session_state.old_courses_list or not st.session_state.new_courses_list:
        st.warning("Please add at least one Old Course and one New Course.")
    else:
        with st.spinner("Analyzing..."):
            # تحويل القوائم إلى DataFrames
            old_courses_df = pd.DataFrame(st.session_state.old_courses_list)
            new_courses_df = pd.DataFrame(st.session_state.new_courses_list)

            # استدعاء دالة الذكاء الاصطناعي
            all_equivalences = find_all_equivalences(
              old_courses_df,
              new_courses_df
            )

            st.subheader("Equivalency Results")
            if all_equivalences:
                results_df = pd.DataFrame(all_equivalences)
                
                # تنسيق النتائج للعرض
                display_df = results_df.rename(columns={
                    'old_course_code': 'Old Code',
                    'old_course_name': 'Old Name',
                    'new_course_code': 'New Code',
                    'new_course_name': 'New Name',
                    'similarity_score': 'Similarity %'
                })
                display_df['Similarity %'] = (display_df['Similarity %'] * 100).round(2).astype(str) + '%'
                
                st.dataframe(display_df, use_container_width=True)
                st.success("Analysis completed successfully.")
            else:
                st.info("No matches found.")