# sentence_transformers هو مكتبة قوية لبناء نماذج تحويل الجمل واستخدامها في مهام مثل البحث عن التشابه، التصنيف، والتجميع.
# util توفر وظائف مساعدة لحساب التشابه بين المتجهات. (cosine similarity)
from sentence_transformers import SentenceTransformer, util

# تحميل النموذج مرة واحدة عند بدء تشغيل التطبيق
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
# paraphrase => to find similar meanings in different texts
# multilingual => supports multiple languages
# MiniLM-L12-v2 => model size and version (small size)

def find_all_equivalences(old_courses_df, new_courses_df):
  """
  هذه الدالة تجد أفضل مطابقة لكل مادة قديمة من قائمة المواد الجديدة
  باستخدام تقنية المعالجة المجمعة (Batch Processing) لتحقيق أقصى سرعة.
  """
  # all descriptions of old and new courses as lists
  old_descriptions = old_courses_df['description'].tolist()
  new_descriptions = new_courses_df['description'].tolist()


  # تحويل كل أوصاف المواد القديمة إلى متجهات رقمية مرة واحدة
  print("Encoding old course descriptions...")
  old_embeddings = model.encode(old_descriptions, convert_to_tensor=True, show_progress_bar=True)
  
  # تحويل كل أوصاف المواد الجديدة إلى متجهات رقمية مرة واحدة
  print("Encoding new course descriptions...")
  new_embeddings = model.encode(new_descriptions, convert_to_tensor=True, show_progress_bar=True)


  # حساب درجة التشابه بين كل متجهات القديم وكل متجهات الجديد مرة واحدة
  # النتيجة تكون مصفوفة (Matrix) من الدرجات
  print("Calculating similarity scores...")
  cosine_scores = util.cos_sim(old_embeddings, new_embeddings)

  #  ايجاد أفضل النتائج
  all_equivalences = [] # مصفوفة الناتج
  # المرور على كل مادة قديمة (كل صف في مصفوفة النتائج)
  for i in range(len(old_courses_df)):
    # الحصول على درجات تشابه المادة القديمة رقم 'i' مع كل المواد الجديدة
    scores_for_old_course = cosine_scores[i]
    
    # إيجاد فهرس (index) أعلى درجة تشابه
    best_match_index = scores_for_old_course.argmax().item()
    
    # الحصول على قيمة أعلى درجة تشابه
    best_score = scores_for_old_course[best_match_index].item()

    # الحصول على بيانات المادة الجديدة الأعلى تشابهاً
    best_match_course = new_courses_df.iloc[best_match_index]

    # إضافة نتيجة المعادلة هذه إلى القائمة النهائية
    all_equivalences.append({
      "old_course_code": old_courses_df.iloc[i]['course_code'],
      "old_course_name": old_courses_df.iloc[i]['course_name'],
      "grade": old_courses_df.iloc[i].get('grade', 'N/A'), # إذا كان هناك عمود 'grade' في البيانات القديمة، استخدمه، وإلا ضع 'N/A'
      "new_course_code": best_match_course['course_code'],
      "new_course_name": best_match_course['course_name'],
      "similarity_score": best_score,
      "new_credit_hours": best_match_course['credit_hours']
    })
    
  return all_equivalences


# دالة مساعدة لإيجاد أفضل تطابق لاسم عمود معين
def find_best_column_match(target_name, source_column_names):
  """
  تجد أفضل مطابقة لاسم عمود مستهدف من قائمة أسماء الأعمدة المتوفرة.
  """
  if not source_column_names:
    return None, 0.0

  # تحويل الاسم المستهدف والأسماء المتوفرة إلى تمثيلات رقمية
  target_embedding = model.encode(target_name, convert_to_tensor=True)
  source_embeddings = model.encode(source_column_names, convert_to_tensor=True)
  
  # حساب التشابه
  cosine_scores = util.cos_sim(target_embedding, source_embeddings)
  
  # إيجاد أفضل تطابق وأعلى درجة تشابه
  best_match_index = cosine_scores[0].argmax().item()
  best_match_name = source_column_names[best_match_index]
  best_score = cosine_scores[0, best_match_index].item()
  
  return best_match_name, best_score