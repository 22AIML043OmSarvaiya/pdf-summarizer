#!/usr/bin/env python3
"""
Deployment helper script for AI PDF Summarizer
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import streamlit
        import PyPDF2
        import transformers
        import torch
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

def install_requirements():
    """Install requirements"""
    if not check_requirements():
        print("\n📦 Installing requirements...")
        run_command("pip install -r requirements.txt", "Installing dependencies")
        
        if not check_requirements():
            print("❌ Failed to install all requirements")
            return False
    
    return True

def test_app():
    """Test the application"""
    print("\n🧪 Testing application...")
    
    # Check if the main file exists
    if not os.path.exists("pdf_summarizer.py"):
        print("❌ pdf_summarizer.py not found")
        return False
    
    # Try to import the main modules
    try:
        import streamlit as st
        print("✅ Streamlit import successful")
        return True
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False

def run_local():
    """Run the application locally"""
    print("\n🚀 Starting local development server...")
    print("📱 Your app will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run(["streamlit", "run", "pdf_summarizer.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")

def build_docker():
    """Build Docker image"""
    print("\n🐳 Building Docker image...")
    
    if not os.path.exists("Dockerfile"):
        print("❌ Dockerfile not found")
        return False
    
    result = run_command("docker build -t pdf-summarizer .", "Building Docker image")
    return result is not None

def run_docker():
    """Run Docker container"""
    print("\n🐳 Starting Docker container...")
    print("📱 Your app will be available at: http://localhost:8501")
    
    try:
        subprocess.run([
            "docker", "run", "-p", "8501:8501", 
            "--name", "pdf-summarizer-app", 
            "pdf-summarizer"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Stopping container...")
        subprocess.run(["docker", "stop", "pdf-summarizer-app"], check=True)
        subprocess.run(["docker", "rm", "pdf-summarizer-app"], check=True)

def show_deployment_info():
    """Show deployment information"""
    print("""
🚀 DEPLOYMENT OPTIONS:

1. 🖥️  LOCAL DEVELOPMENT:
   python deploy.py --local
   
2. 🐳 DOCKER:
   python deploy.py --docker
   
3. ☁️  STREAMLIT CLOUD:
   - Push code to GitHub
   - Visit https://share.streamlit.io/
   - Connect repository and deploy
   
4. 🌐 HEROKU:
   - Install Heroku CLI
   - heroku create your-app-name
   - git push heroku main
   
5. 📦 MANUAL DEPLOYMENT:
   - Install requirements: pip install -r requirements.txt
   - Run app: streamlit run pdf_summarizer.py

📋 REQUIREMENTS:
   - Python 3.8+
   - 2GB+ RAM
   - Internet (first run only)

🔗 USEFUL LINKS:
   - Streamlit Cloud: https://share.streamlit.io/
   - Documentation: https://docs.streamlit.io/
   - Docker Hub: https://hub.docker.com/
    """)

def main():
    """Main deployment function"""
    print("🤖 AI PDF Summarizer - Deployment Helper")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        show_deployment_info()
        return
    
    command = sys.argv[1].lower()
    
    if command == "--local":
        if install_requirements() and test_app():
            run_local()
    
    elif command == "--docker":
        if build_docker():
            run_docker()
    
    elif command == "--test":
        install_requirements()
        test_app()
    
    elif command == "--install":
        install_requirements()
    
    elif command == "--help":
        show_deployment_info()
    
    else:
        print(f"❌ Unknown command: {command}")
        show_deployment_info()

if __name__ == "__main__":
    main()