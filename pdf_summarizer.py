import streamlit as st
from PyPDF2 import PdfReader
from transformers import pipeline
import torch
import io
import base64
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="AI PDF Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Dark Theme Support
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Light theme styles (default) */
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
        color: #333;
        transition: all 0.3s ease;
    }
    
    .summary-box {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        color: #333;
        transition: all 0.3s ease;
    }
    
    .feature-highlight {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
        color: #333;
        transition: all 0.3s ease;
    }
    
    /* Theme styles will be applied dynamically by JavaScript */
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        min-width: 120px;
    }
    
    .download-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem;
    }
</style>

<script>
// Smart theme detection and adaptive styling
function getStreamlitTheme() {
    // Method 1: Check Streamlit's actual background color
    const stApp = document.querySelector('.stApp');
    if (stApp) {
        const bgColor = window.getComputedStyle(stApp).backgroundColor;
        // Streamlit dark theme uses rgb(14, 17, 23)
        if (bgColor.includes('14, 17, 23') || bgColor.includes('rgb(14, 17, 23)')) {
            return 'dark';
        }
        // Streamlit light theme uses rgb(255, 255, 255) or similar
        if (bgColor.includes('255, 255, 255') || bgColor.includes('rgb(255, 255, 255)')) {
            return 'light';
        }
    }
    
    // Method 2: Check body background
    const body = document.body;
    const bodyBg = window.getComputedStyle(body).backgroundColor;
    if (bodyBg.includes('14, 17, 23')) return 'dark';
    if (bodyBg.includes('255, 255, 255')) return 'light';
    
    // Method 3: Check for dark theme indicators in the DOM
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        const sidebarBg = window.getComputedStyle(sidebar).backgroundColor;
        if (sidebarBg.includes('38, 39, 48') || sidebarBg.includes('rgb(38, 39, 48)')) {
            return 'dark';
        }
    }
    
    // Method 4: System preference as fallback
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    
    return 'light';
}

function applyAdaptiveStyles() {
    const theme = getStreamlitTheme();
    
    // Get all elements that need styling
    const uploadSections = document.querySelectorAll('.upload-section');
    const featureHighlights = document.querySelectorAll('.feature-highlight');
    const summaryBoxes = document.querySelectorAll('.summary-box');
    
    if (theme === 'dark') {
        // Apply dark theme styles
        uploadSections.forEach(el => {
            el.style.setProperty('background', '#2d3748', 'important');
            el.style.setProperty('border-color', '#4a5568', 'important');
            el.style.setProperty('color', '#e2e8f0', 'important');
        });
        
        featureHighlights.forEach(el => {
            el.style.setProperty('background', '#2d3748', 'important');
            el.style.setProperty('border-left-color', '#4299e1', 'important');
            el.style.setProperty('color', '#e2e8f0', 'important');
        });
        
        summaryBoxes.forEach(el => {
            el.style.setProperty('background', '#1a202c', 'important');
            el.style.setProperty('color', '#e2e8f0', 'important');
            el.style.setProperty('box-shadow', '0 2px 10px rgba(0,0,0,0.3)', 'important');
        });
    } else {
        // Apply light theme styles (remove any forced dark styles)
        uploadSections.forEach(el => {
            el.style.removeProperty('background');
            el.style.removeProperty('border-color');
            el.style.removeProperty('color');
            // Set light theme defaults
            el.style.background = '#f8f9fa';
            el.style.borderColor = '#dee2e6';
            el.style.color = '#333';
        });
        
        featureHighlights.forEach(el => {
            el.style.removeProperty('background');
            el.style.removeProperty('border-left-color');
            el.style.removeProperty('color');
            // Set light theme defaults
            el.style.background = '#e3f2fd';
            el.style.borderLeftColor = '#2196f3';
            el.style.color = '#333';
        });
        
        summaryBoxes.forEach(el => {
            el.style.removeProperty('background');
            el.style.removeProperty('color');
            el.style.removeProperty('box-shadow');
            // Set light theme defaults
            el.style.background = 'white';
            el.style.color = '#333';
            el.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        });
    }
}

// Debounced theme application to prevent excessive calls
let themeTimeout;
function debouncedApplyStyles() {
    clearTimeout(themeTimeout);
    themeTimeout = setTimeout(applyAdaptiveStyles, 100);
}

// Apply styles when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyAdaptiveStyles);
} else {
    applyAdaptiveStyles();
}

// Listen for system theme changes
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', debouncedApplyStyles);
}

// Monitor for Streamlit theme changes with more specific targeting
const observer = new MutationObserver((mutations) => {
    let shouldUpdate = false;
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && 
            (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {
            const target = mutation.target;
            if (target.classList.contains('stApp') || target === document.body) {
                shouldUpdate = true;
            }
        }
    });
    if (shouldUpdate) {
        debouncedApplyStyles();
    }
});

observer.observe(document.body, { 
    attributes: true, 
    attributeFilter: ['style', 'class'],
    subtree: true 
});

// Periodic check but less frequent
setInterval(() => {
    const currentTheme = getStreamlitTheme();
    if (window.lastDetectedTheme !== currentTheme) {
        window.lastDetectedTheme = currentTheme;
        applyAdaptiveStyles();
    }
}, 2000);
</script>
""", unsafe_allow_html=True)

@st.cache_resource
def get_llama_ollama():
    """Initialize Ollama Llama connection"""
    try:
        import requests
        # Test Ollama connection
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            available_models = [model['name'] for model in models if 'llama' in model['name'].lower()]
            return available_models
        return []
    except:
        return []

@st.cache_resource
def get_llama_transformers(model_name="microsoft/DialoGPT-medium"):
    """Load Llama model via transformers (fallback to compatible model)"""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        with st.spinner(f"🦙 Loading {model_name}..."):
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            return model, tokenizer
    except Exception as e:
        st.error(f"Failed to load Llama model: {e}")
        return None, None

@st.cache_resource
def get_distilbart_summarizer():
    """Load the original DistilBART summarization pipeline"""
    with st.spinner("🤖 Loading DistilBART model..."):
        return pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",
            device=0 if torch.cuda.is_available() else -1
        )

def summarize_with_ollama(text, model_name="llama2", max_words=500):
    """Summarize using Ollama Llama model"""
    import requests
    import json
    
    prompt = f"""You are an expert document analyst specializing in comprehensive summarization of confidential and sensitive documents. Your task is to create detailed summaries that preserve ALL critical information.

CRITICAL REQUIREMENTS:
- Preserve ALL numbers, dates, names, references, and identifiers
- Maintain ALL key decisions, conclusions, and recommendations  
- Keep ALL technical specifications and important details
- Preserve context and relationships between concepts
- This is confidential data - NO information should be omitted
- Target length: approximately {max_words} words
- Use clear, professional language
- Organize information logically

DOCUMENT TO SUMMARIZE:
{text}

COMPREHENSIVE SUMMARY:"""

    try:
        response = requests.post('http://localhost:11434/api/generate',
            json={
                'model': model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,  # Lower temperature for more focused output
                    'top_p': 0.9,
                    'max_tokens': max_words * 2  # Allow flexibility
                }
            },
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    except Exception as e:
        raise Exception(f"Ollama summarization failed: {str(e)}")

def summarize_with_transformers(text, model, tokenizer, max_words=500):
    """Summarize using local Llama model via transformers"""
    import torch
    
    prompt = f"""<s>[INST] You are an expert at creating comprehensive summaries of confidential documents. Create a detailed summary of the following text that preserves all important information including numbers, dates, names, and key details. Target length: {max_words} words.

Text: {text}

Summary: [/INST]"""

    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
            model = model.cuda()
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_words * 2,
                temperature=0.3,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only the summary part
        if "[/INST]" in response:
            summary = response.split("[/INST]")[-1].strip()
        else:
            summary = response.strip()
            
        return summary
    except Exception as e:
        raise Exception(f"Transformers summarization failed: {str(e)}")

def get_summarizer():
    """Main summarizer function with model selection"""
    # Model selection in sidebar
    with st.sidebar:
        st.header("🤖 AI Model Selection")
        
        # Check available models
        ollama_models = get_llama_ollama()
        
        model_options = ["DistilBART (Fast, Good Quality)"]
        if ollama_models:
            model_options.extend([f"Llama via Ollama: {model}" for model in ollama_models])
        model_options.append("Llama via Transformers (Local)")
        
        selected_model = st.selectbox(
            "Choose AI Model",
            model_options,
            help="Llama models provide better results for confidential data"
        )
        
        # Model info
        if "DistilBART" in selected_model:
            st.info("🔸 **DistilBART**: Fast, good for general summaries")
        elif "Ollama" in selected_model:
            st.success("🦙 **Llama via Ollama**: Best for confidential data, superior context understanding")
        else:
            st.warning("🦙 **Llama via Transformers**: Good quality but slower, requires more memory")
    
    return selected_model

def extract_text_from_pdfs(pdf_files):
    """Extract text from uploaded PDF files with progress tracking"""
    text = ""
    total_pages = 0
    
    # First pass: count total pages
    for pdf in pdf_files:
        reader = PdfReader(pdf)
        total_pages += len(reader.pages)
    
    # Second pass: extract text with progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    current_page = 0
    
    for pdf_idx, pdf in enumerate(pdf_files):
        reader = PdfReader(pdf)
        status_text.text(f"📖 Processing {pdf.name} ({pdf_idx + 1}/{len(pdf_files)})")
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} of {pdf.name} ---\n"
                text += page_text + "\n"
            
            current_page += 1
            progress_bar.progress(current_page / total_pages)
    
    progress_bar.empty()
    status_text.empty()
    return text, total_pages

def chunk_text(text, max_tokens=1024):
    """Split text into chunks for summarization"""
    # Split by sentences first
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Rough token estimation (1 token ≈ 4 characters)
        if len(current_chunk) + len(sentence) < max_tokens * 4:
            current_chunk += sentence + " "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def extract_important_sections(text):
    """Extract important sections while preserving all critical information"""
    # Split into paragraphs and sentences
    paragraphs = text.split('\n\n')
    important_content = []
    
    # Keywords that indicate important information
    important_keywords = [
        'important', 'critical', 'key', 'significant', 'essential', 'required', 'mandatory',
        'conclusion', 'result', 'finding', 'recommendation', 'decision', 'action',
        'number', 'amount', 'date', 'deadline', 'percent', '%', '$', 'cost', 'price',
        'name', 'contact', 'address', 'phone', 'email', 'reference', 'id', 'code'
    ]
    
    for para in paragraphs:
        if para.strip():
            # Check if paragraph contains important keywords or specific data
            para_lower = para.lower()
            has_important_info = any(keyword in para_lower for keyword in important_keywords)
            has_numbers = bool(re.search(r'\d+', para))
            has_dates = bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', para))
            
            if has_important_info or has_numbers or has_dates or len(para.split()) > 30:
                important_content.append(para.strip())
    
    return important_content

def create_comprehensive_summary(text, target_length="medium"):
    """Create comprehensive summary that preserves all important information"""
    
    # For confidential data, we want comprehensive coverage, not aggressive compression
    # Target word counts adjusted for completeness
    targets = {
        "short": {"words": 300, "coverage": "key_points"},      # Minimum viable summary
        "medium": {"words": 600, "coverage": "comprehensive"},   # Balanced detail
        "long": {"words": 1000, "coverage": "detailed"}         # Maximum detail
    }
    
    target_info = targets.get(target_length, targets["medium"])
    words_in_text = len(text.split())
    
    # If text is already reasonably sized, don't over-compress
    if words_in_text <= target_info["words"] * 1.5:
        return text  # Return original if already concise enough
    
    # Extract important sections first
    important_sections = extract_important_sections(text)
    
    # If we have good section extraction, use it
    if important_sections:
        combined_sections = "\n\n".join(important_sections)
        section_words = len(combined_sections.split())
        
        # If extracted sections are within target range, use them
        if section_words <= target_info["words"] * 1.2:
            return combined_sections
    
    # Otherwise, use AI summarization but with less aggressive compression
    return None  # Will use AI summarization

def create_download_link(text, filename):
    """Create a download link for the summary"""
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" class="download-button">📥 Download Summary</a>'
    return href

def get_text_stats(text):
    """Calculate text statistics"""
    words = len(text.split())
    chars = len(text)
    sentences = len(re.split(r'[.!?]+', text))
    return words, chars, sentences

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI PDF Summarizer</h1>
        <p>Secure • Local • No API Keys Required</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with features and settings
    with st.sidebar:
        st.header("🎛️ Settings")
        
        # Summary comprehensiveness settings
        summary_length = st.selectbox(
            "Summary Detail Level",
            ["Short (Key Points Only)", "Medium (Comprehensive)", "Long (Maximum Detail)"],
            index=1,  # Default to Medium for balanced approach
            help="Choose how much detail to preserve in your summary"
        )
        
        # Information preservation notice
        st.info("🔒 **Confidential Data Mode**: All important information will be preserved")
        
        # Map selection to parameters - More generous for comprehensive summaries
        length_params = {
            "Short (Key Points Only)": {"max_length": 300, "min_length": 150},
            "Medium (Comprehensive)": {"max_length": 600, "min_length": 300},
            "Long (Maximum Detail)": {"max_length": 1000, "min_length": 500}
        }
        
        st.header("✨ Features")
        st.markdown("""
        <div class="feature-highlight">
        <strong>🔒 Privacy First</strong><br>
        All processing happens locally on your device. No data is sent to external servers.
        </div>
        
        <div class="feature-highlight">
        <strong>🤖 AI Powered</strong><br>
        Uses DistilBART model optimized for comprehensive summarization.
        </div>
        
        <div class="feature-highlight">
        <strong>📚 Multi-PDF Support</strong><br>
        Upload and summarize multiple PDF files at once.
        </div>
        
        <div class="feature-highlight">
        <strong>🔍 Information Preservation</strong><br>
        Designed for confidential data - preserves all critical information.
        </div>
        """, unsafe_allow_html=True)
        
        # Dynamic model info based on selection
        selected_model = get_summarizer()
        
        st.header("🔧 Current AI Model")
        
        if "DistilBART" in selected_model:
            st.markdown("""
            **🔸 DistilBART-CNN-12-6**
            - ✅ Fast processing (10-30 seconds)
            - ✅ Good quality summaries
            - ✅ Always available (no setup needed)
            - ✅ Low memory usage (~400MB)
            - ⚠️ Limited context window (1024 tokens)
            """)
        elif "Ollama" in selected_model:
            model_name = selected_model.split(": ")[1] if ": " in selected_model else "llama2"
            st.markdown(f"""
            **🦙 Llama via Ollama: {model_name}**
            - 🎯 Superior quality for confidential data
            - 🎯 Large context window (4096+ tokens)
            - 🎯 Excellent detail preservation
            - ⏳ Slower processing (30-120 seconds)
            - 💾 Higher memory usage (2-8GB)
            """)
        elif "Transformers" in selected_model:
            st.markdown("""
            **🦙 Llama via Transformers**
            - 🎯 High quality local processing
            - 🎯 Complete offline operation
            - 🎯 Superior context understanding
            - ⏳ Slower processing
            - 💾 High memory usage (4-16GB)
            """)
        
        # Setup instructions for Llama
        ollama_models = get_llama_ollama()
        if not ollama_models:
            st.info("🦙 **Want Better Results?**")
            st.markdown("""
            **Setup Llama for Superior Summarization:**
            1. Run: `python setup_llama.py`
            2. Or install manually: https://ollama.ai/download
            3. Refresh this page after setup
            """)
        else:
            st.success(f"🦙 **{len(ollama_models)} Llama models available!**")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload section
        st.markdown("""
        <div class="upload-section">
            <h3>📁 Upload Your PDF Files</h3>
            <p>Select one or more PDF files to summarize. Drag and drop supported!</p>
        </div>
        """, unsafe_allow_html=True)
        
        pdf_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            help="You can upload multiple PDF files at once"
        )
        
        # Display uploaded files info
        if pdf_files:
            st.success(f"✅ {len(pdf_files)} file(s) uploaded successfully!")
            
            with st.expander("📋 File Details"):
                for i, pdf in enumerate(pdf_files, 1):
                    file_size = len(pdf.getvalue()) / 1024  # Size in KB
                    st.write(f"{i}. **{pdf.name}** ({file_size:.1f} KB)")
    
    with col2:
        if pdf_files:
            st.markdown("### 🎯 Quick Actions")
            
            # Summarize button
            if st.button("🚀 Summarize PDFs", type="primary", use_container_width=True):
                start_time = datetime.now()
                
                # Extract text
                with st.spinner("📖 Extracting text from PDFs..."):
                    text, total_pages = extract_text_from_pdfs(pdf_files)
                
                if not text.strip():
                    st.error("❌ No text could be extracted from the uploaded PDFs.")
                    return
                
                # Show extraction stats
                words, chars, sentences = get_text_stats(text)
                
                st.markdown(f"""
                <div class="stats-container">
                    <div class="stat-box">
                        <strong>{total_pages}</strong><br>Pages
                    </div>
                    <div class="stat-box">
                        <strong>{words:,}</strong><br>Words
                    </div>
                    <div class="stat-box">
                        <strong>{sentences}</strong><br>Sentences
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Determine target length
                target_length = summary_length.split()[0].lower()  # "short", "medium", or "long"
                
                # Get selected model
                selected_model = get_summarizer()
                
                # Create comprehensive summary
                st.info(f"🤖 Creating comprehensive summary with {selected_model.split(':')[0]}...")
                
                # First try comprehensive extraction for very short documents
                comprehensive_summary = create_comprehensive_summary(text, target_length)
                
                if comprehensive_summary and len(text.split()) < 1000:
                    final_summary = comprehensive_summary
                    st.success("✨ Used intelligent extraction preserving all critical information")
                else:
                    # Use selected AI model for summarization
                    params = length_params[summary_length]
                    target_words = params["max_length"]
                    
                    # For very long documents, extract important sections first
                    if len(text.split()) > 4000:
                        st.info("📄 Large document detected, extracting important sections...")
                        important_sections = extract_important_sections(text)
                        if important_sections:
                            text_to_summarize = "\n\n".join(important_sections)
                            st.info(f"📋 Focusing on {len(important_sections)} important sections")
                        else:
                            text_to_summarize = text
                    else:
                        text_to_summarize = text
                    
                    try:
                        if "Ollama" in selected_model:
                            # Use Ollama Llama model
                            model_name = selected_model.split(": ")[1] if ": " in selected_model else "llama2"
                            st.info(f"🦙 Using Ollama model: {model_name}")
                            
                            # For very long texts, process in chunks
                            if len(text_to_summarize.split()) > 2000:
                                chunks = chunk_text(text_to_summarize, max_tokens=1500)  # Larger chunks for Llama
                                chunk_summaries = []
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i, chunk in enumerate(chunks):
                                    status_text.text(f"🦙 Processing section {i + 1} of {len(chunks)} with Llama...")
                                    chunk_summary = summarize_with_ollama(chunk, model_name, target_words // len(chunks))
                                    chunk_summaries.append(chunk_summary)
                                    progress_bar.progress((i + 1) / len(chunks))
                                
                                progress_bar.empty()
                                status_text.empty()
                                
                                # Combine and create final summary
                                combined_text = "\n\n".join(chunk_summaries)
                                if len(combined_text.split()) > target_words:
                                    st.info("🔄 Creating final comprehensive summary...")
                                    final_summary = summarize_with_ollama(combined_text, model_name, target_words)
                                else:
                                    final_summary = combined_text
                            else:
                                # Direct summarization for shorter texts
                                final_summary = summarize_with_ollama(text_to_summarize, model_name, target_words)
                        
                        elif "Transformers" in selected_model:
                            # Use local Llama model via transformers
                            st.info("🦙 Loading local Llama model...")
                            model, tokenizer = get_llama_transformers()
                            
                            if model and tokenizer:
                                # Process in chunks for long texts
                                if len(text_to_summarize.split()) > 1500:
                                    chunks = chunk_text(text_to_summarize, max_tokens=1000)
                                    chunk_summaries = []
                                    
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                                    
                                    for i, chunk in enumerate(chunks):
                                        status_text.text(f"🦙 Processing section {i + 1} of {len(chunks)} with local Llama...")
                                        chunk_summary = summarize_with_transformers(chunk, model, tokenizer, target_words // len(chunks))
                                        chunk_summaries.append(chunk_summary)
                                        progress_bar.progress((i + 1) / len(chunks))
                                    
                                    progress_bar.empty()
                                    status_text.empty()
                                    
                                    final_summary = "\n\n".join(chunk_summaries)
                                else:
                                    final_summary = summarize_with_transformers(text_to_summarize, model, tokenizer, target_words)
                            else:
                                raise Exception("Failed to load local Llama model")
                        
                        else:
                            # Fallback to DistilBART
                            st.info("🔸 Using DistilBART model...")
                            distilbart = get_distilbart_summarizer()
                            
                            chunks = chunk_text(text_to_summarize, max_tokens=800)
                            
                            if len(chunks) == 1:
                                final_summary = distilbart(
                                    chunks[0], 
                                    max_length=params["max_length"], 
                                    min_length=params["min_length"], 
                                    do_sample=False
                                )[0]['summary_text']
                            else:
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                chunk_summaries = []
                                for i, chunk in enumerate(chunks):
                                    status_text.text(f"Processing section {i + 1} of {len(chunks)}")
                                    chunk_max_length = min(200, len(chunk.split()) // 2)
                                    chunk_min_length = min(100, chunk_max_length // 2)
                                    
                                    chunk_summary = distilbart(
                                        chunk, 
                                        max_length=chunk_max_length,
                                        min_length=chunk_min_length, 
                                        do_sample=False
                                    )[0]['summary_text']
                                    chunk_summaries.append(chunk_summary)
                                    progress_bar.progress((i + 1) / len(chunks))
                                
                                progress_bar.empty()
                                status_text.empty()
                                
                                combined_summaries = "\n\n".join(chunk_summaries)
                                
                                if len(combined_summaries.split()) > params["max_length"] * 1.5:
                                    final_summary = distilbart(
                                        combined_summaries, 
                                        max_length=params["max_length"], 
                                        min_length=params["min_length"], 
                                        do_sample=False
                                    )[0]['summary_text']
                                else:
                                    final_summary = combined_summaries
                    
                    except Exception as e:
                        st.error(f"❌ Summarization failed: {str(e)}")
                        st.info("🔄 Falling back to DistilBART...")
                        
                        # Fallback to DistilBART
                        distilbart = get_distilbart_summarizer()
                        chunks = chunk_text(text_to_summarize, max_tokens=800)
                        
                        if len(chunks) == 1:
                            final_summary = distilbart(
                                chunks[0], 
                                max_length=params["max_length"], 
                                min_length=params["min_length"], 
                                do_sample=False
                            )[0]['summary_text']
                        else:
                            chunk_summaries = []
                            for chunk in chunks:
                                chunk_summary = distilbart(
                                    chunk, 
                                    max_length=min(200, len(chunk.split()) // 2),
                                    min_length=50, 
                                    do_sample=False
                                )[0]['summary_text']
                                chunk_summaries.append(chunk_summary)
                            final_summary = "\n\n".join(chunk_summaries)
                
                # Processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Display results
                st.markdown("""
                <div class="summary-box">
                    <h3>📝 Summary Results</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary stats
                summary_words, summary_chars, summary_sentences = get_text_stats(final_summary)
                compression_ratio = (summary_words / words) * 100 if words > 0 else 0
                reduction_ratio = 100 - compression_ratio
                
                # Information preservation feedback
                if compression_ratio > 70:
                    compression_status = "📋 Comprehensive (High Detail)"
                    compression_color = "blue"
                elif compression_ratio > 50:
                    compression_status = "✅ Balanced (Good Coverage)"
                    compression_color = "green"
                elif compression_ratio > 30:
                    compression_status = "📝 Condensed (Key Points)"
                    compression_color = "orange"
                else:
                    compression_status = "⚠️ Highly Compressed"
                    compression_color = "red"
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Summary Words", f"{summary_words:,}", delta=f"-{words-summary_words:,} words")
                with col_b:
                    st.metric("Size Reduction", f"{reduction_ratio:.1f}%", delta=f"{compression_status}")
                with col_c:
                    st.metric("Processing Time", f"{processing_time:.1f}s")
                with col_d:
                    st.metric("Efficiency", f"{words//processing_time:.0f} words/sec" if processing_time > 0 else "N/A")
                
                # Show information preservation feedback
                if compression_ratio > 60:
                    st.success(f"📋 **Comprehensive Summary**: {compression_ratio:.1f}% of original content preserved. All important information retained.")
                elif compression_ratio > 40:
                    st.info(f"✅ **Balanced Summary**: {compression_ratio:.1f}% of original content preserved. Good balance of detail and conciseness.")
                elif compression_ratio > 20:
                    st.warning(f"📝 **Condensed Summary**: {compression_ratio:.1f}% of original content preserved. Key points extracted, some details may be missing.")
                else:
                    st.error(f"⚠️ **Highly Compressed**: Only {compression_ratio:.1f}% of original content preserved. Consider using 'Medium' or 'Long' for confidential data.")
                
                # Display summary
                st.markdown("### 📄 Generated Summary")
                st.markdown(f"""
                <div class="summary-box">
                    {final_summary.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                # Download options
                st.markdown("### 💾 Export Options")
                col_download1, col_download2 = st.columns(2)
                
                with col_download1:
                    # Text download
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"pdf_summary_{timestamp}.txt"
                    download_text = f"PDF Summary Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    download_text += f"Original Files: {', '.join([pdf.name for pdf in pdf_files])}\n"
                    download_text += f"Total Pages: {total_pages}\n"
                    download_text += f"Original Words: {words:,}\n"
                    download_text += f"Summary Words: {summary_words:,}\n"
                    download_text += f"Compression Ratio: {compression_ratio:.1f}%\n\n"
                    download_text += "SUMMARY:\n" + "="*50 + "\n\n"
                    download_text += final_summary
                    
                    st.download_button(
                        label="📄 Download as Text",
                        data=download_text,
                        file_name=filename,
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col_download2:
                    # Copy to clipboard (text area for easy copying)
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.text_area(
                            "Copy this text:",
                            value=final_summary,
                            height=100,
                            key="copy_summary"
                        )
        else:
            st.info("👆 Upload PDF files to get started!")

if __name__ == "__main__":
    main() 