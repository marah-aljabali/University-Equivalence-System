# sentence_transformers is a powerful library for generating sentence embeddings and calculating similarities.
# It provides pre-trained models that can be used for various NLP tasks, including finding equivalences between course descriptions.
#utility functions for the equivalences app
from sentence_transformers import SentenceTransformer, util
import streamlit as st

# تعريف دالة لتحميل الموديل وتخزينه مؤقتاً
# هذا يجعل التطبيق يحمل الموديل مرة واحدة فقط ويحتفظ به في الذاكرة
@st.cache_resource
def load_ai_model():
    """
    Loads the multilingual sentence transformer model.
    Cached to avoid reloading on every interaction.
    """
    print("Loading AI Model...")
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_model():
    """Helper to get the cached model instance."""
    return load_ai_model()

def find_all_equivalences(old_courses_df, new_courses_df):
  """
  Finds best matches using the loaded model.
  """
  # استدعاء الموديل من الذاكرة المؤقتة
  model = get_model()
  
  # استخراج الأوصاف وتحويلها إلى تمثيلات عددية
  old_descriptions = old_courses_df['description'].tolist()
  new_descriptions = new_courses_df['description'].tolist()

  print("Encoding old course descriptions...")
  old_embeddings = model.encode(old_descriptions, convert_to_tensor=True, show_progress_bar=True)
  
  print("Encoding new course descriptions...")
  new_embeddings = model.encode(new_descriptions, convert_to_tensor=True, show_progress_bar=True)


  # حساب تشابه الكوساين بين التمثيلات
  print("Calculating similarity scores...")
  cosine_scores = util.cos_sim(old_embeddings, new_embeddings)

  all_equivalences = [] 
  for i in range(len(old_courses_df)):
    scores_for_old_course = cosine_scores[i] # الحصول على درجات التشابه للدورة القديمة الحالية مع جميع الدورات الجديدة
    best_match_index = scores_for_old_course.argmax().item()  # الحصول على مؤشر أفضل تطابق
    best_score = scores_for_old_course[best_match_index].item() # الحصول على درجة التشابه الأفضل
    best_match_course = new_courses_df.iloc[best_match_index] # الحصول على بيانات الدورة الجديدة المطابقة

    all_equivalences.append({
      "old_course_code": old_courses_df.iloc[i]['course_code'],
      "old_course_name": old_courses_df.iloc[i]['course_name'],
      "grade": old_courses_df.iloc[i].get('grade', 'N/A'), # الحصول على الدرجة إذا كانت موجودة، وإلا إرجاع 'N/A'
      "new_course_code": best_match_course['course_code'],
      "new_course_name": best_match_course['course_name'],
      "similarity_score": best_score,
      "new_credit_hours": best_match_course['credit_hours']
    })
    
  return all_equivalences

def find_best_column_match(target_name, source_column_names):
  """
  Finds the best matching column name using the AI model.
  """
  model = get_model() # استخدام الموديل المحمل
  
  if not source_column_names:
    return None, 0.0

  # تحويل اسم العمود الهدف إلى تمثيل عددي
  target_embedding = model.encode(target_name, convert_to_tensor=True)
  # تحويل أسماء الأعمدة المصدر إلى تمثيلات عددية
  source_embeddings = model.encode(source_column_names, convert_to_tensor=True)
  # حساب تشابه الكوساين بين التمثيل الهدف وتمثيلات الأعمدة المصدر
  cosine_scores = util.cos_sim(target_embedding, source_embeddings)
  
  best_match_index = cosine_scores[0].argmax().item() # الحصول على مؤشر أفضل تطابق
  best_match_name = source_column_names[best_match_index] # الحصول على اسم العمود المطابق
  best_score = cosine_scores[0, best_match_index].item() # الحصول على درجة التشابه الأفضل
  
  return best_match_name, best_score