import streamlit as st
import pandas as pd
import re # استيراد مكتبة التعابير النمطية لتحليل نص العلامة
from ai_engine import find_all_equivalences, find_best_column_match


def uploade_best_match():
  st.header("Upload Files")
  col1, col2 = st.columns(2)

  with col1:
    st.subheader("Old Study Plan")
    old_file = st.file_uploader(
      "Upload CSV file for the old plan",
      type=["csv"], 
      key="old" 
    )

  with col2:
    st.subheader("New Study Plan")
    new_file = st.file_uploader(
      "Upload CSV file for the new plan",
      type=["csv"], 
      key="new"
    )
  
  # --- إضافة خانة فلترة العلامات ---
  st.subheader("Filter by Grade (Optional)")
  grade_filter = st.text_input(
    "Enter grade criteria (e.g., >= 80, 70-90, or leave empty to include all)",
    help="Use operators like >=, <=, or a range (e.g., 80-90)."
  )

  if st.button("Start Processing", type="primary", use_container_width=True):
    if old_file is not None and new_file is not None:
      try:
        # read 
        old_courses_df = pd.read_csv(old_file)
        new_courses_df = pd.read_csv(new_file)
        
        st.subheader("Analyse old file: ")
        old_courses_df, old_success = smart_column_mapping_old(old_courses_df)
        
        st.subheader("Analyse new file: ")
        new_courses_df, new_success = smart_column_mapping_new(new_courses_df)
        
        if not (old_success and new_success):
          st.error("Cannot proceed due to missing required columns.")
          return
          
        st.success(
          f"Loaded {len(old_courses_df)} old courses and "
          f"{len(new_courses_df)} new courses."
        )

        # --- منطق فلترة العلامات ---
        eligible_old_courses = old_courses_df.copy()
        if grade_filter:
          st.info(f"Applying grade filter: '{grade_filter}'")
          try:
            # تحويل عمود العلامات إلى أرقام
            eligible_old_courses['grade'] = pd.to_numeric(eligible_old_courses['grade'], errors='coerce')
            
            # تحليل نص الفلتر
            if '>=' in grade_filter:
              threshold = float(grade_filter.split('>=')[1].strip())
              eligible_old_courses = eligible_old_courses[eligible_old_courses['grade'] >= threshold]

            elif '<=' in grade_filter:
              threshold = float(grade_filter.split('<=')[1].strip())
              eligible_old_courses = eligible_old_courses[eligible_old_courses['grade'] <= threshold]

            elif '-' in grade_filter:
              low, high = map(float, grade_filter.split('-'))
              eligible_old_courses = eligible_old_courses[(eligible_old_courses['grade'] >= low) & (eligible_old_courses['grade'] <= high)]

            else:
              st.warning("Invalid grade format. Please use >=, <=, or a range (e.g., 80-90). Showing all results.")
            
            if eligible_old_courses.empty:
              st.warning("No courses met the specified grade criteria. Showing all results without grade filter.")
              eligible_old_courses = old_courses_df.copy() # الرجوع للقائمة الأصلية
            else:
              st.success(f"Filtered down to {len(eligible_old_courses)} courses based on grade.")

          except (ValueError, IndexError):
            st.warning("Could not parse the grade filter. Please check the format. Showing all results.")
            eligible_old_courses = old_courses_df.copy() # الرجوع للقائمة الأصلية

        progress_bar = st.progress(0, text="Analyzing...")

        # ------AI Processing --------
        # نستخدم القائمة التي تمت فلترتها (أو الأصلية إذا لم يتم الفلترة)
        all_equivalences = find_all_equivalences(
          eligible_old_courses,
          new_courses_df
        )

        progress_bar.progress(50, text="Selecting best match per old course...")

        best_match_per_old = {}
        for eq in all_equivalences:
          old_code = eq['old_course_code']
          if (
            old_code not in best_match_per_old or
            eq['similarity_score'] > best_match_per_old[old_code]['similarity_score']
          ):
            best_match_per_old[old_code] = eq

        best_equivalences = list(best_match_per_old.values())
        progress_bar.progress(70, text="Applying 30 credit hours limit...")

        best_equivalences_sorted = sorted(
          best_equivalences,
          key=lambda x: x['similarity_score'],
          reverse=True
        )

        MAX_HOURS = 30
        total_hours = 0
        highlighted_pairs = set()

        for eq in best_equivalences_sorted:
          if total_hours + eq['new_credit_hours'] <= MAX_HOURS:
            total_hours += eq['new_credit_hours']
            highlighted_pairs.add((eq['old_course_code'], eq['new_course_code']))
          else:
            break

        progress_bar.progress(100, text="Analysis completed!")

        if not best_equivalences_sorted:
          st.info("No equivalences were found.")
          return

        results_df = pd.DataFrame(best_equivalences_sorted)
        display_df = results_df.rename(columns={
          'old_course_code': 'Old Course Code',
          'old_course_name': 'Old Course Name',
          'new_course_code': 'New Course Code',
          'new_course_name': 'New Course Name',
          'new_credit_hours': 'Equivalent Credit Hours',
          'similarity_score': 'Similarity Score',
          'grade': 'Grade'
        })

        display_df['Similarity Score'] = (display_df['Similarity Score'] * 100).round(2).astype(str) + '%'

        def highlight_top_30(row):
          pair = (row['Old Course Code'], row['New Course Code'])
          if pair in highlighted_pairs:
            return ['background-color: #FFF3B0'] * len(row)
          return [''] * len(row)

        styled_df = display_df.style.apply(highlight_top_30, axis=1)

        st.success(
          f"Best equivalence selected for each old course. "
          f"Highlighted rows represent the top {total_hours} credit hours."
        )

        st.dataframe(styled_df, use_container_width=True)

        display_df['Included in 30 Credit Hours'] = display_df.apply(
          lambda row: 'Yes'
          if (row['Old Course Code'], row['New Course Code']) in highlighted_pairs
          else 'No',
          axis=1
        )

        csv = display_df.to_csv(index=False,encoding='utf-8-sig').encode('utf-8-sig')

        st.download_button(
          label="Download Equivalency Report (CSV)",
          data=csv,
          file_name="academic_equivalence_report.csv",
          mime="text/csv"
        )

      except Exception as e:
        st.error(f"An error occurred: {e}")
    else:
      st.warning(
        "Please upload both the old and new study plan files to proceed."
      )




# --- دالة للتعرف الذكي على أسماء الأعمدة وتحويلها الى الاسماء الاساسية ---
def smart_column_mapping_old(df):
  # الأعمدة الأساسية التي نبحث عنها
  required_columns = ['course_code', 'course_name', 'description', 'credit_hours', 'grade']

  # عبارات أكثر وضوحاً لمساعدة الذكاء الاصطناعي 
  target_definitions = {
    'course_code': 'course code or identifier',
    'course_name': 'course title or name',
    'description': 'course description or details or course content',
    'credit_hours': 'credit hours or units',
    'grade': 'student grade or mark or score'
  }
  # أسماء الأعمدة المتوفرة في الملف
  available_source_columns = df.columns.tolist()
  
  mapping = {}
  missing_columns = []
  
  # قيمة التشابه المقبولة
  SIMILARITY_THRESHOLD = 0 # لحتى أوسع البحث
  
  for req_col in required_columns:
    if not available_source_columns:
      missing_columns.append(req_col)
      continue
    
    # استخدام العبارة الواضحة للمساعدة في المطابقة
    target_phrase = target_definitions[req_col]
    best_match, score = find_best_column_match(target_phrase, available_source_columns)
    
    if score >= SIMILARITY_THRESHOLD:
      mapping[best_match] = req_col
      st.success(f"Mapped column **`{best_match}`** to **`{req_col}`** with similarity {score:.2f}.")
      available_source_columns.remove(best_match)
    else:
      missing_columns.append(req_col)
      st.warning(f"Missing required columns: {', '.join(missing_columns)}.")
  
  if missing_columns:
    st.error(f"could not find a good match for required column **`{req_col}`**.")
    return df, False
  
  df = df.rename(columns=mapping)
  st.info("Columns successfully mapped.")
  return df, True



# --- دالة للتعرف الذكي على أسماء الأعمدة في الخطة الجديدة وتحويلها الى الاسماء الاساسية ---
# الفرق بين الاثنتين هو شرط العمود grade )(مش ضروري يكون في الخطة الجديدة)
def smart_column_mapping_new(df):
  # الأعمدة الأساسية التي نبحث عنها
  required_columns = ['course_code', 'course_name', 'description', 'credit_hours']

  # عبارات أكثر وضوحاً لمساعدة الذكاء الاصطناعي 
  target_definitions = {
    'course_code': 'course code or identifier',
    'course_name': 'course title or name',
    'description': 'course description or details or course content',
    'credit_hours': 'credit hours or units',
  }
  # أسماء الأعمدة المتوفرة في الملف
  available_source_columns = df.columns.tolist()
  
  mapping = {}
  missing_columns = []
  
  # قيمة التشابه المقبولة
  SIMILARITY_THRESHOLD = 0 # لحتى أوسع البحث
  
  for req_col in required_columns:
    if not available_source_columns:
      missing_columns.append(req_col)
      continue
    
    # استخدام العبارة الواضحة للمساعدة في المطابقة
    target_phrase = target_definitions[req_col]
    best_match, score = find_best_column_match(target_phrase, available_source_columns)
    
    if score >= SIMILARITY_THRESHOLD:
      mapping[best_match] = req_col
      st.success(f"Mapped column **`{best_match}`** to **`{req_col}`** with similarity {score:.2f}.")
      available_source_columns.remove(best_match)
    else:
      missing_columns.append(req_col)
      st.warning(f"Missing required columns: {', '.join(missing_columns)}.")
  
  if missing_columns:
    st.error(f"could not find a good match for required column **`{req_col}`**.")
    return df, False
  
  df = df.rename(columns=mapping)
  st.info("Columns successfully mapped.")
  return df, True
