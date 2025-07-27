@echo off
echo 🚀 Deploying AI PDF Summarizer to GitHub...
echo.

echo 📋 Checking files...
if not exist "app.py" (
    echo ❌ app.py not found!
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ requirements.txt not found!
    pause
    exit /b 1
)

echo ✅ All required files found!
echo.

echo 📝 Initializing git repository...
git init

echo 📦 Adding files to git...
git add .

echo 💾 Creating commit...
git commit -m "Deploy: AI PDF Summarizer with Llama integration and perfect theming"

echo.
echo 🌐 Ready to push to GitHub!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_REPO_URL
echo 4. Run: git push -u origin main
echo 5. Deploy on Streamlit Cloud: https://share.streamlit.io
echo.

pause