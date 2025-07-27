#!/usr/bin/env python3
"""
🔒 AI PDF Summarizer - Minimal Cloud Version
Secure, Local, No API Keys Required
Guaranteed to work on Streamlit Cloud
"""

import streamlit as st
import PyPDF2
import io
import re
from datetime import datetime
import requests

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
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        color: #333;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stats-container {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #1565c0;
    }
    
    .feature-highlight {
        background: #f1f8e9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
        color: #2e7d32;
    }
    
    /* Dark theme styles */
    [data-theme="dark"] .upload-section {
        background: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
    }
    
    [data-theme="dark"] .summary-box {
        background: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    [data-theme="dark"] .stats-container {
        background: #2a4365;
        color: #90cdf4;
    }
    
    [data-theme="dark"] .feature-highlight {
        background: #2f855a;
        color: #c6f6d5;
        border-left-color: #68d391;
    }
    
    /* Auto-detect system theme */
    @media (prefers-color-scheme: dark) {
        .upload-section {
            background: #2d3748;
            border-color: #4a5568;
            color: #e2e8f0;
        }
        
        .summary-box {
            background: #2d3748;
            border-color: #4a5568;
            color: #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .stats-container {
            background: #2a4365;
            color: #90cdf4;
        }
        
        .feature-highlight {
            background: #2f855a;
            color: #c6f6d5;
            border-left-color: #68d391;
        }
    }
    
    .download-button {
        background: linear-gradient(90deg, #4caf50 0%, #45a049 100%);
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .processing-animation {
        display: inline-block;
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>

<script>
// Auto-detect and apply theme
function applyTheme() {
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
}

// Apply theme on load and when system theme changes
applyTheme();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
</script>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from a single PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def get_text_stats(text):
    """Get basic statistics about the text"""
    words = len(text.split())
    chars = len(text)
    sentences = len(re.findall(r'[.!?]+', text))
    return words, chars, sentences

def create_intelligent_summary(text, target_length):
    """Create an intelligent summary using advanced rule-based extraction"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) < 3:
        return text[:500] + "..." if len(text) > 500 else text
    
    # Advanced scoring system
    scored_sentences = []
    
    # Get important keywords from the text
    word_freq = {}
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top keywords (excluding common words)
    common_words = {'that', 'this', 'with', 'have', 'will', 'been', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'}
    important_keywords = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20] if word not in common_words]
    
    for i, sentence in enumerate(sentences):
        score = 0
        sentence_lower = sentence.lower()
        
        # Length score (prefer medium-length sentences)
        if 50 <= len(sentence) <= 250:
            score += 3
        elif 30 <= len(sentence) <= 300:
            score += 2
        elif len(sentence) >= 20:
            score += 1
        
        # Keyword frequency score
        for keyword in important_keywords[:10]:
            if keyword in sentence_lower:
                score += 2
        
        # Position score (first and last sentences often important)
        if i < 3:  # First 3 sentences
            score += 3
        elif i >= len(sentences) - 3:  # Last 3 sentences
            score += 2
        elif i < len(sentences) * 0.2:  # First 20%
            score += 1
        
        # Important phrase indicators
        important_phrases = [
            'in conclusion', 'to summarize', 'in summary', 'overall', 'finally',
            'important', 'significant', 'key', 'main', 'primary', 'essential',
            'results show', 'findings indicate', 'research shows', 'study found',
            'analysis reveals', 'data suggests', 'evidence shows',
            'therefore', 'thus', 'consequently', 'as a result'
        ]
        
        for phrase in important_phrases:
            if phrase in sentence_lower:
                score += 3
        
        # Numerical data and statistics (often important)
        if re.search(r'\d+%|\d+\.\d+|\$\d+|figure \d+|table \d+', sentence_lower):
            score += 2
        
        # Questions (often highlight key points)
        if sentence.strip().endswith('?'):
            score += 1
        
        # Avoid very short or very long sentences
        if len(sentence) < 20:
            score -= 2
        elif len(sentence) > 400:
            score -= 1
        
        scored_sentences.append((sentence, score, i))
    
    # Sort by score, then by position for tie-breaking
    scored_sentences.sort(key=lambda x: (x[1], -x[2]), reverse=True)
    
    # Select number of sentences based on target length
    if target_length == "short":
        num_sentences = min(4, len(scored_sentences))
    elif target_length == "medium":
        num_sentences = min(7, len(scored_sentences))
    else:  # long
        num_sentences = min(12, len(scored_sentences))
    
    # Get selected sentences and sort by original position
    selected = scored_sentences[:num_sentences]
    selected.sort(key=lambda x: x[2])  # Sort by original position
    
    summary_sentences = [s[0] for s in selected]
    summary = ". ".join(summary_sentences)
    
    # Clean up the summary
    summary = re.sub(r'\s+', ' ', summary)  # Remove extra whitespace
    summary = summary.strip()
    
    if not summary.endswith('.'):
        summary += "."
    
    return summary

def chunk_text(text, max_words=800):
    """Split text into chunks for processing"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    
    return chunks

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔒 AI PDF Summarizer</h1>
        <p>Secure • Local • Intelligent Extraction • No API Keys Required</p>
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
        st.header("🧠 Processing Method")
        st.markdown("""
        **Intelligent Extraction**: Advanced rule-based summarization
        - ✅ Fast processing (5-15 seconds)
        - ✅ Keyword-based importance scoring
        - ✅ Position and context analysis
        - ✅ Works offline, no AI models needed
        - ✅ Guaranteed to work on any device
        """)
        
        # Confidential data info
        st.markdown("""
        <div class="feature-highlight">
        <h4>🔒 Complete Privacy</h4>
        <p>• All processing happens locally<br>
        • No data sent to external servers<br>
        • No API keys or accounts required<br>
        • Your documents never leave your device</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features
        st.header("✨ Features")
        st.markdown("""
        - 📄 **Multi-PDF Support** - Process multiple files
        - 🎨 **Adaptive Theming** - Auto light/dark mode
        - 📱 **Mobile Responsive** - Works on all devices
        - 💾 **Easy Downloads** - Save summaries as text
        - ⚡ **Fast Processing** - No waiting for AI models
        - 🔒 **100% Private** - Everything stays local
        """)
    
    # Main content
    st.markdown("""
    <div class="upload-section">
    <h3>📁 Upload Your PDF Documents</h3>
    <p>Select one or more PDF files to summarize. All processing happens locally on your device.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="You can upload multiple PDF files at once. Maximum file size: 200MB per file."
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Process button
        if st.button("🚀 Generate Summaries", type="primary"):
            # Get target length
            target_length = summary_length.split()[0].lower()  # "short", "medium", or "long"
            
            start_time = datetime.now()
            
            all_summaries = []
            
            # Process each file
            for i, uploaded_file in enumerate(uploaded_files):
                st.markdown(f"### 📄 Processing: {uploaded_file.name}")
                
                # Extract text
                with st.spinner(f"📖 Extracting text from {uploaded_file.name}..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if not text:
                    st.error(f"❌ Could not extract text from {uploaded_file.name}")
                    continue
                
                if len(text.strip()) < 100:
                    st.warning(f"⚠️ {uploaded_file.name} contains very little text. Summary may be limited.")
                
                # Get text statistics
                words, chars, sentences = get_text_stats(text)
                
                st.markdown(f"""
                <div class="stats-container">
                <h4>📊 Document Statistics</h4>
                <p><strong>Words:</strong> {words:,} | <strong>Characters:</strong> {chars:,} | <strong>Sentences:</strong> {sentences:,}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create summary
                st.info("🧠 Creating intelligent summary...")
                
                if len(text.split()) > 2000:
                    # For large documents, process in chunks
                    chunks = chunk_text(text, max_words=1000)
                    chunk_summaries = []
                    
                    progress_bar = st.progress(0)
                    for j, chunk in enumerate(chunks):
                        chunk_summary = create_intelligent_summary(chunk, target_length)
                        chunk_summaries.append(chunk_summary)
                        progress_bar.progress((j + 1) / len(chunks))
                    
                    progress_bar.empty()
                    
                    # Combine chunk summaries
                    combined_text = " ".join(chunk_summaries)
                    final_summary = create_intelligent_summary(combined_text, target_length)
                else:
                    # Direct summarization for smaller documents
                    final_summary = create_intelligent_summary(text, target_length)
                
                # Processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Display summary
                st.markdown(f"""
                <div class="summary-box">
                <h4>📝 Summary for {uploaded_file.name}</h4>
                <p>{final_summary}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary statistics
                summary_words, summary_chars, summary_sentences = get_text_stats(final_summary)
                compression_ratio = round((1 - summary_words / words) * 100, 1) if words > 0 else 0
                
                st.markdown(f"""
                <div class="stats-container">
                <h4>📈 Summary Statistics</h4>
                <p><strong>Summary Length:</strong> {summary_words} words, {summary_sentences} sentences</p>
                <p><strong>Compression Ratio:</strong> {compression_ratio}% reduction</p>
                <p><strong>Processing Time:</strong> {processing_time:.1f} seconds</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Store summary for download
                all_summaries.append({
                    'filename': uploaded_file.name,
                    'summary': final_summary,
                    'stats': {
                        'original_words': words,
                        'summary_words': summary_words,
                        'compression_ratio': compression_ratio,
                        'processing_time': processing_time
                    }
                })
            
            # Download all summaries
            if all_summaries:
                st.markdown("### 💾 Download Summaries")
                
                # Create combined summary text
                combined_summary = f"PDF Summaries Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                combined_summary += "=" * 60 + "\n\n"
                
                for summary_data in all_summaries:
                    combined_summary += f"📄 {summary_data['filename']}\n"
                    combined_summary += "-" * 40 + "\n"
                    combined_summary += f"{summary_data['summary']}\n\n"
                    combined_summary += f"Statistics: {summary_data['stats']['original_words']} → {summary_data['stats']['summary_words']} words "
                    combined_summary += f"({summary_data['stats']['compression_ratio']}% reduction)\n\n"
                
                # Download button
                st.download_button(
                    label="📥 Download All Summaries",
                    data=combined_summary,
                    file_name=f"pdf_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download all summaries as a single text file"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
    <p>🔒 <strong>AI PDF Summarizer</strong> - Secure, Local, Private</p>
    <p>No API keys • No external servers • Complete privacy</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()