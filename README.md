🎓 Academic Plan Equivalency Tool
An AI-powered web application designed to automate the process of comparing and matching courses between old and new study plans. Using advanced Semantic Search (NLP), it intelligently identifies equivalent courses based on content description rather than just names, helping academic advisors and students save hours of manual work.

✨ Features
🤖 AI-Powered Matching: Uses sentence-transformers to understand the semantic meaning of course descriptions for accurate matching.
📂 CSV Upload: Upload study plans in CSV format; the system automatically maps columns (Code, Name, Credits, Description, Grade).
✏️ Manual Entry: A user-friendly form to enter courses manually for quick testing or small batches.
⚖️ Smart Limits: Automatically enforces a credit hour limit (default: 30 hours) and selects the best matches based on similarity scores.
🎨 Professional UI: Clean, modern, and responsive design inspired by EduPredict, ensuring a great user experience.
📊 Export Results: Download the final equivalency report as a CSV file with highlighted matches.

🛠️ Tech Stack
Backend/Core: Python 3.8+
Frontend Framework: Streamlit
Machine Learning: Sentence-Transformers (Hugging Face), Pandas, Scikit-Learn
Data Handling: Pandas, NumPy

🚀 Installation & Setup
Follow these steps to run the project locally on your machine.
1. Clone the Repository
git clone https://github.com/your-username/academic-equivalency-tool.gitcd academic-equivalency-tool
2. Create Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Run the Application
streamlit run app.py
Note: The first time you run the app, it will automatically download the pre-trained AI model (paraphrase-multilingual-MiniLM-L12-v2) from Hugging Face. This may take a few minutes depending on your internet connection.

📖 Usage Guide
Method 1: Upload Files (Batch Processing)
Click "Upload Files" from the main menu.
Upload your Old Plan (CSV) and New Plan (CSV).
The system will attempt to auto-detect columns.
(Optional) Apply a Grade Filter (e.g., >= 80).
Click "Start Processing" to view matches.
Method 2: Enter Data (Manual Testing)
Click "Enter Data".
Use the forms to add old and new courses one by one.
Click "Start Analysis" to see the AI matching results.
Understanding the Results
Similarity Score: A percentage indicating how closely the course descriptions match.
Highlighted Rows: These are the courses selected within the 30-credit limit.
Credits: The number of credit hours for the new course.

📁 Project Structure.
├── app.py                      # Main application entry point & Navigation
├── ai_engine.py                # Core AI logic (Embeddings & Similarity)
├── uploade_best_match.py       # Logic for handling CSV uploads
├── enter_data.py               # Logic for manual data entry
├── requirements.txt            # Python dependencies
└── README.md                   # This file

🤝 Contributing
Contributions are welcome! If you have a suggestion that would make this better, please fork the repo and create a pull request.

🙏 Acknowledgments
The AI model used is paraphrase-multilingual-MiniLM-L12-v2 by Sentence-Transformers.
Built with Streamlit.
