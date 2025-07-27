#!/usr/bin/env python3
"""
Setup script for Llama integration with PDF Summarizer
"""

import subprocess
import sys
import os
import requests
import time
from pathlib import Path

def run_command(command, description, shell=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        if isinstance(command, list):
            result = subprocess.run(command, check=True, capture_output=True, text=True, shell=shell)
        else:
            result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Ollama is not installed")
    return False

def install_ollama():
    """Install Ollama"""
    print("\n🦙 Installing Ollama...")
    
    # Check if running on Windows
    if os.name == 'nt':
        print("📥 Please install Ollama manually on Windows:")
        print("1. Visit: https://ollama.ai/download")
        print("2. Download and run the Windows installer")
        print("3. Restart this script after installation")
        input("Press Enter after installing Ollama...")
        return check_ollama_installed()
    else:
        # Linux/Mac installation
        result = run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama"
        )
        return result is not None

def start_ollama_service():
    """Start Ollama service"""
    print("\n🚀 Starting Ollama service...")
    
    try:
        # Check if already running
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is already running")
            return True
    except:
        pass
    
    # Start Ollama service
    if os.name == 'nt':
        # Windows
        try:
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        except:
            print("❌ Failed to start Ollama service")
            print("Please start Ollama manually by running 'ollama serve' in a new terminal")
            return False
    else:
        # Linux/Mac
        try:
            subprocess.Popen(["ollama", "serve"])
        except:
            print("❌ Failed to start Ollama service")
            return False
    
    # Wait for service to start
    print("⏳ Waiting for Ollama service to start...")
    for i in range(30):
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                print("✅ Ollama service started successfully")
                return True
        except:
            time.sleep(1)
    
    print("❌ Ollama service failed to start within 30 seconds")
    return False

def install_llama_models():
    """Install recommended Llama models"""
    print("\n🦙 Installing Llama models...")
    
    models = [
        ("llama2:7b", "Llama 2 7B - Good balance of speed and quality"),
        ("llama2:13b", "Llama 2 13B - Better quality, slower (optional)"),
        ("llama3:8b", "Llama 3 8B - Latest version, excellent quality")
    ]
    
    installed_models = []
    
    for model, description in models:
        print(f"\n📦 {description}")
        choice = input(f"Install {model}? (y/n/s to skip all): ").lower()
        
        if choice == 's':
            break
        elif choice == 'y':
            print(f"⬇️ Downloading {model} (this may take several minutes)...")
            result = run_command(f"ollama pull {model}", f"Installing {model}")
            if result:
                installed_models.append(model)
                print(f"✅ {model} installed successfully")
            else:
                print(f"❌ Failed to install {model}")
    
    return installed_models

def test_llama_integration():
    """Test Llama integration"""
    print("\n🧪 Testing Llama integration...")
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            llama_models = [model['name'] for model in models if 'llama' in model['name'].lower()]
            
            if llama_models:
                print(f"✅ Found {len(llama_models)} Llama models:")
                for model in llama_models:
                    print(f"   - {model}")
                
                # Test summarization
                test_model = llama_models[0]
                print(f"\n🔬 Testing summarization with {test_model}...")
                
                test_text = "Artificial intelligence is transforming how we work and live. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions. This technology is being applied in healthcare, finance, transportation, and many other fields."
                
                test_response = requests.post('http://localhost:11434/api/generate',
                    json={
                        'model': test_model,
                        'prompt': f"Summarize this text in 2-3 sentences: {test_text}",
                        'stream': False
                    },
                    timeout=60
                )
                
                if test_response.status_code == 200:
                    summary = test_response.json().get('response', '').strip()
                    print(f"✅ Test successful! Summary: {summary[:100]}...")
                    return True
                else:
                    print(f"❌ Test failed: HTTP {test_response.status_code}")
            else:
                print("❌ No Llama models found")
        else:
            print("❌ Cannot connect to Ollama service")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    return False

def install_python_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    packages = ["requests", "accelerate", "bitsandbytes"]
    
    for package in packages:
        result = run_command(f"pip install {package}", f"Installing {package}")
        if not result:
            print(f"⚠️ Failed to install {package}, but continuing...")

def main():
    """Main setup function"""
    print("🦙 Llama Integration Setup for PDF Summarizer")
    print("=" * 60)
    
    print("\nThis script will help you set up Llama models for better PDF summarization.")
    print("Llama models provide superior results for confidential data.")
    
    # Step 1: Install Python dependencies
    install_python_dependencies()
    
    # Step 2: Check/Install Ollama
    if not check_ollama_installed():
        if not install_ollama():
            print("\n❌ Ollama installation failed. Please install manually.")
            return
    
    # Step 3: Start Ollama service
    if not start_ollama_service():
        print("\n❌ Could not start Ollama service. Please start manually with 'ollama serve'")
        return
    
    # Step 4: Install Llama models
    installed_models = install_llama_models()
    
    if not installed_models:
        print("\n⚠️ No models were installed. You can install them later with:")
        print("   ollama pull llama2:7b")
        print("   ollama pull llama3:8b")
    
    # Step 5: Test integration
    if test_llama_integration():
        print("\n🎉 Llama integration setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Run your PDF summarizer: streamlit run pdf_summarizer.py")
        print("2. Select a Llama model from the dropdown in the sidebar")
        print("3. Upload your PDFs and enjoy superior summarization!")
        
        print("\n💡 Tips:")
        print("- Llama models are slower but provide much better quality")
        print("- Use Llama 2 7B for good balance of speed and quality")
        print("- Use Llama 3 8B for best quality")
        print("- Keep Ollama service running in the background")
    else:
        print("\n❌ Setup completed but testing failed.")
        print("Please check that Ollama is running: ollama serve")

if __name__ == "__main__":
    main()