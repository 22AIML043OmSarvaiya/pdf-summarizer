#!/usr/bin/env python3
"""
🔒 AI PDF Summarizer - Simplified Version
Secure, Local, No API Keys Required
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
""", unsafe_allow_html=True)

# Theme detection script
st.markdown("""
<script>
    // Auto-detect and apply theme
    function applyTheme() {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    }
    
    // Apply theme on load
    applyTheme();
    
    // Listen for theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
</script>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from a single PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
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

def create_extractive_summary(text, target_length):
    """Create a summary using extractive method"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) < 3:
        return text[:500] + "..." if len(text) > 500 else text
    
    # Score sentences based on various factors
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        
        # Length score (prefer medium-length sentences)
        if 50 <= len(sentence) <= 200:
            score += 2
        
        # Keyword score (look for important terms)
        important_words = ['important', 'significant', 'key', 'main', 'primary', 
                          'conclusion', 'result', 'finding', 'analysis', 'summary',
                          'therefore', 'however', 'moreover', 'furthermore', 'additionally']
        for word in important_words:
            if word.lower() in sentence.lower():
                score += 1
        
        # Position score (first and last sentences often important)
        if i < 3 or i >= len(sentences) - 3:
            score += 1
        
        # Frequency score (sentences with common words)
        words = sentence.lower().split()
        for word in words:
            if len(word) > 4 and text.lower().count(word) > 2:
                score += 0.5
        
        scored_sentences.append((sentence, score))
    
    # Sort by score and select top sentences
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Select number of sentences based on target length
    if target_length == "short":
        num_sentences = min(3, len(scored_sentences))
    elif target_length == "medium":
        num_sentences = min(6, len(scored_sentences))
    else:  # long
        num_sentences = min(10, len(scored_sentences))
    
    selected_sentences = [s[0] for s in scored_sentences[:num_sentences]]
    
    # Reorder sentences to maintain original flow
    original_order = []
    for sentence in sentences:
        if sentence in selected_sentences:
            original_order.append(sentence)
    
    return ". ".join(original_order) + "."

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
            ["Short (3 sentences)", "Medium (6 sentences)", "Long (10 sentences)"],
            index=1,
            help="Choose how detailed you want your summary to be"
        )
        
        # Model info
        st.header("🤖 Processing Method")
        st.markdown("""
        **Intelligent Extraction**
        - ✅ Fast processing (instant)
        - ✅ Key sentence identification
        - ✅ Context preservation
        - ✅ No external dependencies
        """)
        
        # Confidential data info
        st.markdown("""
        <div class="feature-highlight">
        <h4>🔒 Complete Privacy</h4>
        <p>• All processing happens locally<br>
        • No data sent to external servers<br>
        • No API keys required<br>
        • Your documents stay private</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features
        st.header("✨ Features")
        st.markdown("""
        - 📄 **Multi-PDF Support**
        - 🎨 **Adaptive Theming**
        - 📱 **Mobile Responsive**
        - 💾 **Download Summaries**
        - ⚡ **Instant Processing**
        - 🔒 **100% Private**
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="upload-section">
        <h3>📁 Upload Your PDFs</h3>
        <p>Select one or more PDF files to summarize</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload one or more PDF files (max 200MB each)"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
            
            # Show file details
            total_size = sum(len(file.getvalue()) for file in uploaded_files)
            st.info(f"📊 Total size: {total_size / (1024*1024):.1f} MB")
            
            if st.button("🚀 Generate Summary", type="primary"):
                start_time = datetime.now()
                
                # Process all files
                all_text = ""
                for i, file in enumerate(uploaded_files):
                    st.info(f"📖 Processing {file.name}...")
                    text = extract_text_from_pdf(file)
                    if text:
                        all_text += f"\n\n--- {file.name} ---\n\n{text}"
                    else:
                        st.warning(f"⚠️ Could not extract text from {file.name}")
                
                if not all_text.strip():
                    st.error("❌ No text could be extracted from the uploaded files")
                    return
                
                # Get text statistics
                words, chars, sentences = get_text_stats(all_text)
                
                # Show processing stats
                st.markdown(f"""
                <div class="stats-container">
                <h4>📊 Document Statistics</h4>
                <p><strong>Words:</strong> {words:,} | <strong>Characters:</strong> {chars:,} | <strong>Sentences:</strong> {sentences:,}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create summary
                target_length = summary_length.split()[0].lower()  # Extract "short", "medium", or "long"
                
                st.info("🤖 Creating intelligent summary...")
                final_summary = create_extractive_summary(all_text, target_length)
                
                # Processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Display results in second column
                with col2:
                    st.markdown("""
                    <div class="summary-box">
                    <h3>📝 Summary</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(final_summary)
                    
                    # Summary statistics
                    summary_words, summary_chars, summary_sentences = get_text_stats(final_summary)
                    compression_ratio = (1 - len(final_summary) / len(all_text)) * 100
                    
                    st.markdown(f"""
                    <div class="stats-container">
                    <h4>📈 Summary Statistics</h4>
                    <p><strong>Summary Length:</strong> {summary_words} words ({summary_sentences} sentences)</p>
                    <p><strong>Compression:</strong> {compression_ratio:.1f}% reduction</p>
                    <p><strong>Processing Time:</strong> {processing_time:.1f} seconds</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download button
                    summary_filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    st.download_button(
                        label="💾 Download Summary",
                        data=final_summary,
                        file_name=summary_filename,
                        mime="text/plain",
                        help="Download the summary as a text file"
                    )
                    
                    st.success("✅ Summary generated successfully!")
    
    with col2:
        if not uploaded_files:
            st.markdown("""
            <div class="summary-box">
            <h3>🎯 How It Works</h3>
            <ol>
            <li><strong>Upload</strong> your PDF files</li>
            <li><strong>Choose</strong> summary length</li>
            <li><strong>Click</strong> Generate Summary</li>
            <li><strong>Download</strong> your summary</li>
            </ol>
            
            <h4>🌟 Perfect For:</h4>
            <ul>
            <li>📊 Business reports</li>
            <li>📚 Academic papers</li>
            <li>📋 Legal documents</li>
            <li>📖 Research articles</li>
            <li>📄 Technical manuals</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
    🔒 <strong>AI PDF Summarizer</strong> - Secure, Local, Private<br>
    No data leaves your device • No API keys required • Open source
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()