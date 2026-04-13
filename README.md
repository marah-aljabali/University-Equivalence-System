<h1>🎓 Academic Plan Equivalency Tool</h1>
An AI-powered web application designed to automate the process of comparing and matching courses between old and new study plans. Using advanced Semantic Search (NLP), it intelligently identifies equivalent courses based on content description rather than just names, helping academic advisors and students save hours of manual work.

<h2>✨ Features</h2>
🤖 AI-Powered Matching: Uses sentence-transformers to understand the semantic meaning of course descriptions for accurate matching.</br>
📂 CSV Upload: Upload study plans in CSV format; the system automatically maps columns (Code, Name, Credits, Description, Grade).</br>
✏️ Manual Entry: A user-friendly form to enter courses manually for quick testing or small batches.</br>
⚖️ Smart Limits: Automatically enforces a credit hour limit (default: 30 hours) and selects the best matches based on similarity scores.</br>
🎨 Professional UI: Clean, modern, and responsive design inspired by EduPredict, ensuring a great user experience.</br>
📊 Export Results: Download the final equivalency report as a CSV file with highlighted matches.</br>

<h2>🛠️ Tech Stack</h2>
Backend/Core: Python 3.8+ </br>
Frontend Framework: Streamlit </br>
Machine Learning: Sentence-Transformers (Hugging Face), Pandas, Scikit-Learn </br>
Data Handling: Pandas, NumPy </br>

<h2>🚀 Installation & Setup</h2>
Follow these steps to run the project locally on your machine. </br>
1. Clone the Repository </br>
2. Create Virtual Environment (Recommended) </br>
python -m venv venv </br>
source venv/bin/activate  # On Windows use: venv\Scripts\activate </br>
3. Install Dependencies </br>
pip install -r requirements.txt </br>
4. Run the Application </br>
streamlit run app.py </br>
Note: The first time you run the app, it will automatically download the pre-trained AI model (paraphrase-multilingual-MiniLM-L12-v2) from Hugging Face. This may take a few minutes depending on your internet connection.

<h2>📖 Usage Guide</h2>
<h3>Method 1: Upload Files (Batch Processing)</h3>
Click "Upload Files" from the main menu. </br>
Upload your Old Plan (CSV) and New Plan (CSV). </br>
The system will attempt to auto-detect columns. </br>
(Optional) Apply a Grade Filter (e.g., >= 80). </br>
Click "Start Processing" to view matches. </br>
<h3>Method 2: Enter Data (Manual Testing)</h3>
Click "Enter Data". </br>
Use the forms to add old and new courses one by one. </br>
Click "Start Analysis" to see the AI matching results. </br>

<h2>Understanding the Results</h2> 
- Similarity Score: A percentage indicating how closely the course descriptions match. </br>
- Highlighted Rows: These are the courses selected within the 30-credit limit. </br>
- Credits: The number of credit hours for the new course.

<h2>📁 Project Structure</h2>
├── app.py                      # Main application entry point & Navigation </br>
├── ai_engine.py                # Core AI logic (Embeddings & Similarity) </br>
├── uploade_best_match.py       # Logic for handling CSV uploads </br>
├── enter_data.py               # Logic for manual data entry </br>
├── requirements.txt            # Python dependencies </br>
└── README.md                   # This file </br>

<h3>🤝 Contributing</h3>
Contributions are welcome! If you have a suggestion that would make this better, please fork the repo and create a pull request.

<h3>🙏 Acknowledgments</h3>
The AI model used is paraphrase-multilingual-MiniLM-L12-v2 by Sentence-Transformers. </br>
Built with Streamlit. </br>
