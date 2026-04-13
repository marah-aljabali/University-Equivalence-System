import streamlit as st
import pandas as pd
import re
from ai_engine import find_all_equivalences, find_best_column_match

# ─────────────────────────────────────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Section Card ── */
.scard {
    background: #fff;
    border-radius: 16px;
    padding: 24px 24px 16px;
    box-shadow: 0 4px 24px rgba(15,31,61,.10);
    margin-bottom: 22px;
}
.scard-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: #0f1f3d;
    padding-bottom: 10px;
    border-bottom: 2px solid #f1f5f9;
    margin-bottom: 16px;
}

/* ── Info Box ── */
.info-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    font-size: .9rem;
    color: #1e40af;
    margin-bottom: 20px;
}

/* ── Upload Area ── */
[data-testid="stFileUploader"] {
    background: #f8fafc !important;
    border-radius: 14px !important;
    border: 2px dashed #cbd5e1 !important;
    padding: 20px !important;
}

/* ── Table Styling ── */
.high-sim-row { background-color: rgba(13,148,136,.08) !important; } 
.low-sim-row { background-color: #fff !important; }

/* ── Buttons ── */
.stButton > button {
    background: #0d9488 !important;
    color: #fff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Back Button Style */
.back-btn-container { margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)


def uploade_best_match():
    
    # ─── زر العودة للصفحة الرئيسية ───
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

    # Upload Section
    st.markdown('<div class="scard"><div class="scard-title">📂 Upload Study Plans</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Old Plan (CSV)**")
        old_file = st.file_uploader("Choose file...", type=["csv"], key="old", label_visibility="collapsed")

    with col2:
        st.markdown("**New Plan (CSV)**")
        new_file = st.file_uploader("Choose file...", type=["csv"], key="new", label_visibility="collapsed")

    # Filter Section
    st.markdown('<div class="scard"><div class="scard-title">🔍 Filters</div>', unsafe_allow_html=True)
    grade_filter = st.text_input(
        "Filter by Grade (Optional)",
        placeholder="e.g. >= 80, or 70-90",
        help="Leave empty to include all grades."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Action Button
    if st.button("Start Processing", type="primary", use_container_width=True):
        if old_file is not None and new_file is not None:
            try:
                # Read
                old_courses_df = pd.read_csv(old_file)
                new_courses_df = pd.read_csv(new_file)
                
                with st.spinner("Analyzing files structure..."):
                    st.info("Mapping columns for Old Plan...")
                    old_courses_df, old_success = smart_column_mapping_old(old_courses_df)
                    
                    st.info("Mapping columns for New Plan...")
                    new_courses_df, new_success = smart_column_mapping_new(new_courses_df)
                
                if not (old_success and new_success):
                    st.error("Cannot proceed due to missing required columns.")
                    return
                    
                st.success(
                    f"✅ Loaded {len(old_courses_df)} old courses and {len(new_courses_df)} new courses."
                )

                # Filtering Logic
                eligible_old_courses = old_courses_df.copy()
                if grade_filter:
                    try:
                        # التأكد من تحويل العلامة لأرقام للفلترة
                        eligible_old_courses['grade'] = pd.to_numeric(eligible_old_courses['grade'], errors='coerce')
                        
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
                            st.warning("Invalid filter format.")
                        
                        if not eligible_old_courses.empty:
                            st.success(f"Filtered to {len(eligible_old_courses)} courses.")
                        else:
                            st.warning("No courses matched. Using original list.")
                            eligible_old_courses = old_courses_df.copy()
                    except:
                        st.warning("Error parsing filter. Using all courses.")

                # AI Processing
                with st.spinner("Running AI Semantic Matching..."):
                    all_equivalences = find_all_equivalences(eligible_old_courses, new_courses_df)

                best_match_per_old = {}
                for eq in all_equivalences:
                    old_code = eq['old_course_code']
                    if (old_code not in best_match_per_old or eq['similarity_score'] > best_match_per_old[old_code]['similarity_score']):
                        best_match_per_old[old_code] = eq

                best_equivalences = list(best_match_per_old.values())
                best_equivalences_sorted = sorted(best_equivalences, key=lambda x: x['similarity_score'], reverse=True)

                # 30 Hour Limit Logic
                MAX_HOURS = 30
                total_hours = 0
                highlighted_pairs = set()

                for eq in best_equivalences_sorted:
                    if total_hours + eq['new_credit_hours'] <= MAX_HOURS:
                        total_hours += eq['new_credit_hours']
                        highlighted_pairs.add((eq['old_course_code'], eq['new_course_code']))
                    else:
                        break

                if not best_equivalences_sorted:
                    st.info("No equivalences found.")
                    return

                # Results Display
                st.markdown('<div class="scard"><div class="scard-title">📊 Equivalency Results</div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>Summary:</strong> Found matches for {len(best_equivalences)} courses. 
                    Highlighted rows represent the top <strong>{total_hours} credit hours</strong> selected.
                </div>
                """, unsafe_allow_html=True)

                results_df = pd.DataFrame(best_equivalences)
                display_df = results_df.rename(columns={
                    'old_course_code': 'Old Code', 'old_course_name': 'Old Name',
                    'new_course_code': 'New Code', 'new_course_name': 'New Name',
                    'new_credit_hours': 'Credits', 'similarity_score': 'Similarity', 'grade': 'Grade'
                })
                display_df['Similarity'] = (display_df['Similarity'] * 100).round(2).astype(str) + '%'
                
                # تحويل العلامة لعدد صحيح في العرض (إذا كانت NaN ستظهر كـ <NA> وهو مقبول في Pandas)
                display_df['Grade'] = pd.to_numeric(display_df['Grade'], errors='coerce').astype('Int64')

                def highlight_rows(row):
                    pair = (row['Old Code'], row['New Code'])
                    if pair in highlighted_pairs:
                        return ['background-color: #d1fae5'] * len(row) 
                    return [''] * len(row)

                styled_df = display_df.style.apply(highlight_rows, axis=1)
                st.dataframe(styled_df, use_container_width=True, height=400)

                csv = display_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 Download Report (CSV)", data=csv, file_name="equivalency_report.csv", mime="text/csv")
                
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please upload both files.")
    else:
        st.markdown('</div>', unsafe_allow_html=True) 


# --- Mapping Functions ---
def smart_column_mapping_old(df):
    required_columns = ['course_code', 'course_name', 'description', 'credit_hours', 'grade']
    target_definitions = {
        'course_code': 'course code or identifier',
        'course_name': 'course title or name',
        'description': 'course description or details',
        'credit_hours': 'credit hours or units',
        'grade': 'student grade or mark'
    }
    available_source_columns = df.columns.tolist()
    mapping = {}
    missing_columns = []
    SIMILARITY_THRESHOLD = 0 
    
    for req_col in required_columns:
        if not available_source_columns: continue
        target_phrase = target_definitions[req_col]
        best_match, score = find_best_column_match(target_phrase, available_source_columns)
        
        if score >= SIMILARITY_THRESHOLD:
            mapping[best_match] = req_col
            available_source_columns.remove(best_match)
        else:
            missing_columns.append(req_col)
    
    if missing_columns:
        st.error(f"Missing columns: {missing_columns}")
        return df, False
    
    df = df.rename(columns=mapping)
    
    # --- إصلاح العلامات: تحويل العمود لأرقام صحيحة ---
    if 'grade' in df.columns:
        df['grade'] = pd.to_numeric(df['grade'], errors='coerce').astype('Int64')
        
    return df, True

def smart_column_mapping_new(df):
    required_columns = ['course_code', 'course_name', 'description', 'credit_hours']
    target_definitions = {
        'course_code': 'course code or identifier',
        'course_name': 'course title or name',
        'description': 'course description',
        'credit_hours': 'credit hours or units',
    }
    available_source_columns = df.columns.tolist()
    mapping = {}
    missing_columns = []
    SIMILARITY_THRESHOLD = 0 
    
    for req_col in required_columns:
        if not available_source_columns: continue
        target_phrase = target_definitions[req_col]
        best_match, score = find_best_column_match(target_phrase, available_source_columns)
        
        if score >= SIMILARITY_THRESHOLD:
            mapping[best_match] = req_col
            available_source_columns.remove(best_match)
        else:
            missing_columns.append(req_col)
    
    if missing_columns:
        st.error(f"Missing columns: {missing_columns}")
        return df, False
    
    df = df.rename(columns=mapping)
    return df, True