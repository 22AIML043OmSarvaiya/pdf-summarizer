#!/usr/bin/env python3
"""
Test script to check Llama/Ollama connection
"""

import requests
import json

def test_ollama_connection():
    """Test if Ollama is running and has models"""
    print("🦙 Testing Ollama Connection...")
    print("=" * 50)
    
    try:
        # Test connection
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama service is running!")
            
            # Get available models
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"\n📦 Found {len(models)} models:")
                llama_models = []
                
                for model in models:
                    model_name = model['name']
                    size = model.get('size', 0) / (1024**3)  # Convert to GB
                    print(f"   - {model_name} ({size:.1f} GB)")
                    
                    if 'llama' in model_name.lower():
                        llama_models.append(model_name)
                
                if llama_models:
                    print(f"\n🦙 Llama models available: {len(llama_models)}")
                    
                    # Test summarization with first Llama model
                    test_model = llama_models[0]
                    print(f"\n🧪 Testing summarization with {test_model}...")
                    
                    test_text = """
                    The quarterly financial report shows significant growth in revenue. 
                    Sales increased by 25% compared to last quarter, reaching $2.5 million. 
                    The marketing department spent $300,000 on advertising campaigns. 
                    Customer acquisition cost decreased by 15% to $45 per customer. 
                    The board of directors approved a budget increase for Q4. 
                    Key performance indicators show positive trends across all departments.
                    """
                    
                    prompt = f"""You are an expert document analyst. Create a comprehensive summary of this financial data that preserves all numbers, percentages, and key details:

{test_text}

Summary:"""
                    
                    try:
                        response = requests.post('http://localhost:11434/api/generate',
                            json={
                                'model': test_model,
                                'prompt': prompt,
                                'stream': False,
                                'options': {
                                    'temperature': 0.3,
                                    'max_tokens': 200
                                }
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            summary = result.get('response', '').strip()
                            
                            print("✅ Summarization test successful!")
                            print(f"\n📝 Generated Summary:")
                            print("-" * 40)
                            print(summary)
                            print("-" * 40)
                            
                            # Check if important details are preserved
                            preserved_details = []
                            if "25%" in summary: preserved_details.append("Revenue growth %")
                            if "2.5 million" in summary or "$2.5" in summary: preserved_details.append("Revenue amount")
                            if "300,000" in summary or "$300" in summary: preserved_details.append("Marketing spend")
                            if "15%" in summary: preserved_details.append("Cost reduction %")
                            if "45" in summary or "$45" in summary: preserved_details.append("Customer cost")
                            
                            print(f"\n🎯 Detail Preservation Check:")
                            print(f"   Preserved: {len(preserved_details)}/5 key details")
                            for detail in preserved_details:
                                print(f"   ✅ {detail}")
                            
                            if len(preserved_details) >= 4:
                                print("\n🎉 Excellent! Llama is preserving confidential data details!")
                            elif len(preserved_details) >= 2:
                                print("\n👍 Good! Llama is working but could preserve more details.")
                            else:
                                print("\n⚠️ Llama needs tuning for better detail preservation.")
                                
                        else:
                            print(f"❌ Summarization failed: HTTP {response.status_code}")
                    
                    except Exception as e:
                        print(f"❌ Summarization test failed: {str(e)}")
                
                else:
                    print("\n⚠️ No Llama models found. Install with:")
                    print("   ollama pull llama2:7b")
                    print("   ollama pull llama3:8b")
            
            else:
                print("\n❌ No models installed. Install with:")
                print("   ollama pull llama2:7b")
        
        else:
            print(f"❌ Ollama connection failed: HTTP {response.status_code}")
            print("Make sure Ollama is running: ollama serve")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama service")
        print("\n🔧 Setup Instructions:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Start service: ollama serve")
        print("3. Install model: ollama pull llama2:7b")
        print("4. Run this test again")
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def show_integration_status():
    """Show current integration status"""
    print("\n" + "="*50)
    print("🔧 PDF Summarizer Integration Status")
    print("="*50)
    
    # Check if app is running
    try:
        response = requests.get('http://localhost:8505', timeout=2)
        if response.status_code == 200:
            print("✅ PDF Summarizer app is running at: http://localhost:8505")
        else:
            print("⚠️ PDF Summarizer app status unknown")
    except:
        print("❌ PDF Summarizer app is not running")
        print("   Start with: streamlit run pdf_summarizer.py")
    
    # Check Ollama status
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            llama_count = len([m for m in models if 'llama' in m['name'].lower()])
            if llama_count > 0:
                print(f"✅ Ollama is running with {llama_count} Llama models")
                print("🎯 Your app can use Llama for superior summarization!")
            else:
                print("⚠️ Ollama is running but no Llama models installed")
                print("   Install with: ollama pull llama2:7b")
        else:
            print("❌ Ollama service not responding")
    except:
        print("❌ Ollama service not running")
        print("   Start with: ollama serve")
    
    print("\n🎯 Next Steps:")
    print("1. Open: http://localhost:8505")
    print("2. Look for 'AI Model Selection' in sidebar")
    print("3. Choose Llama model if available")
    print("4. Upload your confidential PDFs")
    print("5. Experience superior summarization!")

if __name__ == "__main__":
    test_ollama_connection()
    show_integration_status()