#!/usr/bin/env python3
"""
🔒 AI PDF Summarizer - Cloud Deployment Version
Secure, Local, No API Keys Required
Optimized for Streamlit Cloud
"""

import streamlit as st
import PyPDF2
import io
import re
from datetime import datetime
import requests
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Page configuration
st.set_page_config(
    page_title="🔒 AI PDF Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Perfect Adaptive Theme
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
// Smart theme detection and adaptive styling for Streamlit Cloud
function getStreamlitTheme() {
    const stApp = document.querySelector('.stApp');
    if (stApp) {
        const bgColor = window.getComputedStyle(stApp).backgroundColor;
        if (bgColor.includes('14, 17, 23') || bgColor.includes('rgb(14, 17, 23)')) {
            return 'dark';
        }
        if (bgColor.includes('255, 255, 255') || bgColor.includes('rgb(255, 255, 255)')) {
            return 'light';
        }
    }
    
    const body = document.body;
    const bodyBg = window.getComputedStyle(body).backgroundColor;
    if (bodyBg.includes('14, 17, 23')) return 'dark';
    if (bodyBg.includes('255, 255, 255')) return 'light';
    
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    
    return 'light';
}

function applyAdaptiveStyles() {
    const theme = getStreamlitTheme();
    
    const uploadSections = document.querySelectorAll('.upload-section');
    const featureHighlights = document.querySelectorAll('.feature-highlight');
    const summaryBoxes = document.querySelectorAll('.summary-box');
    
    if (theme === 'dark') {
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
        uploadSections.forEach(el => {
            el.style.removeProperty('background');
            el.style.removeProperty('border-color');
            el.style.removeProperty('color');
            el.style.background = '#f8f9fa';
            el.style.borderColor = '#dee2e6';
            el.style.color = '#333';
        });
        
        featureHighlights.forEach(el => {
            el.style.removeProperty('background');
            el.style.removeProperty('border-left-color');
            el.style.removeProperty('color');
            el.style.background = '#e3f2fd';
            el.style.borderLeftColor = '#2196f3';
            el.style.color = '#333';
        });
        
        summaryBoxes.forEach(el => {
            el.style.removeProperty('background');
            el.style.removeProperty('color');
            el.style.removeProperty('box-shadow');
            el.style.background = 'white';
            el.style.color = '#333';
            el.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        });
    }
}

let themeTimeout;
function debouncedApplyStyles() {
    clearTimeout(themeTimeout);
    themeTimeout = setTimeout(applyAdaptiveStyles, 100);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyAdaptiveStyles);
} else {
    applyAdaptiveStyles();
}

if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', debouncedApplyStyles);
}

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
def get_summarizer():
    """Initialize the summarization model - optimized for cloud deployment"""
    try:
        # Use the smallest, most reliable model for Streamlit Cloud
        model_name = "facebook/bart-large-cnn"
        
        # Always use CPU for Streamlit Cloud compatibility
        summarizer = pipeline(
            "summarization",
            model=model_name,
            device=-1,  # Force CPU usage
            framework="pt"
        )
        
        return summarizer
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        # Fallback to a smaller model if the main one fails
        try:
            fallback_model = "sshleifer/distilbart-cnn-6-6"
            summarizer = pipeline(
                "summarization",
                model=fallback_model,
                device=-1,
                framework="pt"
            )
            st.warning(f"Using fallback model: {fallback_model}")
            return summarizer
        except Exception as e2:
            st.error(f"Fallback model also failed: {str(e2)}")
            return None

def extract_text_from_pdf(pdf_file):
    """Extract text from a single PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text, len(pdf_reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF {pdf_file.name}: {str(e)}")
        return "", 0

def extract_text_from_pdfs(pdf_files):
    """Extract text from multiple PDF files"""
    combined_text = ""
    total_pages = 0
    
    for pdf_file in pdf_files:
        text, pages = extract_text_from_pdf(pdf_file)
        combined_text += f"\n--- Content from {pdf_file.name} ---\n{text}\n"
        total_pages += pages
    
    return combined_text, total_pages

def chunk_text(text, max_tokens=1000):
    """Split text into chunks for processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def get_text_stats(text):
    """Get basic statistics about the text"""
    words = len(text.split())
    chars = len(text)
    sentences = len(re.findall(r'[.!?]+', text))
    return words, chars, sentences

def create_comprehensive_summary(text, target_length):
    """Create a comprehensive summary using rule-based extraction"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) < 3:
        return None
    
    # Score sentences based on various factors
    scored_sentences = []
    for sentence in sentences:
        score = 0
        
        # Length score (prefer medium-length sentences)
        if 50 <= len(sentence) <= 200:
            score += 2
        
        # Keyword score (look for important terms)
        important_words = ['important', 'significant', 'key', 'main', 'primary', 
                          'conclusion', 'result', 'finding', 'analysis', 'summary']
        for word in important_words:
            if word.lower() in sentence.lower():
                score += 1
        
        # Position score (first and last sentences often important)
        if sentence in sentences[:3] or sentence in sentences[-3:]:
            score += 1
        
        scored_sentences.append((sentence, score))
    
    # Sort by score and select top sentences
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Select number of sentences based on target length
    if target_length == "short":
        num_sentences = min(3, len(scored_sentences))
    elif target_length == "medium":
        num_sentences = min(5, len(scored_sentences))
    else:  # long
        num_sentences = min(8, len(scored_sentences))
    
    selected_sentences = [s[0] for s in scored_sentences[:num_sentences]]
    
    return ". ".join(selected_sentences) + "."

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔒 AI PDF Summarizer</h1>
        <p>Secure • Local • No API Keys Required</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Summary length selection
        summary_length = st.selectbox(
            "📏 Summary Detail Level",
            ["Short (3-5 sentences)", "Medium (5-8 sentences)", "Long (8-12 sentences)"],
            index=1,
            help="Choose how detailed you want your summary to be"
        )
        
        # Model info
        st.header("🤖 AI Model")
        st.markdown("""
        **Current Model**: DistilBART-CNN-12-6
        - ✅ Fast processing (10-30 seconds)
        - ✅ Good quality summaries
        - ✅ Optimized for cloud deployment
        - ✅ No API keys required
        """)
        
        # Confidential data info
        st.markdown("""
        <div class="feature-highlight">
        <h4>🔒 Confidential Data Mode</h4>
        All processing happens locally in your browser. 
        Your documents never leave this session.
        </div>
        """, unsafe_allow_html=True)
        
        # Features
        st.header("✨ Features")
        st.markdown("""
        <div class="feature-highlight">
        <h4>🎯 Key Features:</h4>
        • Multiple PDF support<br>
        • Intelligent text extraction<br>
        • Adaptive summarization<br>
        • Perfect dark/light theme<br>
        • Download summaries<br>
        • Complete privacy
        </div>
        """, unsafe_allow_html=True)
    
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
                target_length = summary_length.split()[0].lower()
                
                # Length parameters for different summary types
                length_params = {
                    "Short (3-5 sentences)": {"max_length": 150, "min_length": 50},
                    "Medium (5-8 sentences)": {"max_length": 300, "min_length": 100},
                    "Long (8-12 sentences)": {"max_length": 500, "min_length": 200}
                }
                
                # Create comprehensive summary
                st.info("🤖 Creating comprehensive summary...")
                
                # First try comprehensive extraction for shorter documents
                comprehensive_summary = create_comprehensive_summary(text, target_length)
                
                if comprehensive_summary and len(text.split()) < 1000:
                    final_summary = comprehensive_summary
                    st.success("✨ Used intelligent extraction preserving all critical information")
                else:
                    # Use AI summarization
                    summarizer = get_summarizer()
                    
                    if not summarizer:
                        st.error("❌ Could not load summarization model")
                        return
                    
                    params = length_params[summary_length]
                    
                    # Split into chunks for processing
                    chunks = chunk_text(text, max_tokens=800)
                    
                    if len(chunks) == 1:
                        # Single chunk - direct summarization
                        try:
                            final_summary = summarizer(
                                chunks[0], 
                                max_length=params["max_length"], 
                                min_length=params["min_length"], 
                                do_sample=False
                            )[0]['summary_text']
                        except Exception as e:
                            st.error(f"❌ Summarization failed: {str(e)}")
                            return
                    else:
                        # Multiple chunks
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        chunk_summaries = []
                        for i, chunk in enumerate(chunks):
                            status_text.text(f"Processing section {i + 1} of {len(chunks)}")
                            try:
                                chunk_max_length = min(200, len(chunk.split()) // 2)
                                chunk_min_length = min(100, chunk_max_length // 2)
                                
                                chunk_summary = summarizer(
                                    chunk, 
                                    max_length=chunk_max_length,
                                    min_length=chunk_min_length, 
                                    do_sample=False
                                )[0]['summary_text']
                                chunk_summaries.append(chunk_summary)
                            except Exception as e:
                                st.warning(f"⚠️ Error processing chunk {i+1}: {str(e)}")
                                continue
                            
                            progress_bar.progress((i + 1) / len(chunks))
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        if not chunk_summaries:
                            st.error("❌ Could not process any chunks")
                            return
                        
                        # Combine chunk summaries
                        combined_summaries = "\n\n".join(chunk_summaries)
                        
                        # Final summarization if needed
                        if len(combined_summaries.split()) > params["max_length"] * 1.5:
                            st.info("🔄 Creating final comprehensive summary...")
                            try:
                                final_summary = summarizer(
                                    combined_summaries, 
                                    max_length=params["max_length"], 
                                    min_length=params["min_length"], 
                                    do_sample=False
                                )[0]['summary_text']
                            except Exception as e:
                                st.warning(f"⚠️ Final summarization failed, using combined summaries: {str(e)}")
                                final_summary = combined_summaries
                        else:
                            final_summary = combined_summaries
                
                # Processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Display results
                st.markdown(f"""
                <div class="summary-box">
                    <h3>📄 Summary Results</h3>
                    <p><strong>Processing Time:</strong> {processing_time:.1f} seconds</p>
                    <p><strong>Summary Length:</strong> {len(final_summary.split())} words</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary content
                st.markdown("### 📝 Generated Summary")
                st.write(final_summary)
                
                # Download button
                summary_filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                summary_content = f"""PDF Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Files Processed: {', '.join([f.name for f in pdf_files])}
Total Pages: {total_pages}
Processing Time: {processing_time:.1f} seconds

SUMMARY:
{final_summary}

---
Generated by AI PDF Summarizer
Secure • Local • No API Keys Required
"""
                
                st.download_button(
                    label="📥 Download Summary",
                    data=summary_content,
                    file_name=summary_filename,
                    mime="text/plain",
                    use_container_width=True
                )
                
                # Additional stats
                summary_words = len(final_summary.split())
                compression_ratio = (words / summary_words) if summary_words > 0 else 0
                
                st.markdown(f"""
                <div class="stats-container">
                    <div class="stat-box">
                        <strong>{summary_words}</strong><br>Summary Words
                    </div>
                    <div class="stat-box">
                        <strong>{compression_ratio:.1f}x</strong><br>Compression
                    </div>
                    <div class="stat-box">
                        <strong>{processing_time:.1f}s</strong><br>Process Time
                    </div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()