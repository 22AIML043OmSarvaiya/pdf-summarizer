#!/usr/bin/env python3
"""
Test script to verify the improved summarization logic
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from pdf_summarizer import extract_key_sentences, create_intelligent_summary, get_text_stats

def test_summarization():
    """Test the summarization functions"""
    
    # Sample long text
    sample_text = """
    Artificial Intelligence (AI) has become one of the most transformative technologies of the 21st century. 
    It encompasses a wide range of techniques and applications that enable machines to perform tasks that 
    typically require human intelligence. Machine learning, a subset of AI, allows systems to automatically 
    learn and improve from experience without being explicitly programmed. Deep learning, which uses neural 
    networks with multiple layers, has revolutionized fields such as computer vision, natural language 
    processing, and speech recognition. The applications of AI are vast and growing rapidly. In healthcare, 
    AI systems can analyze medical images, assist in diagnosis, and help discover new drugs. In transportation, 
    autonomous vehicles use AI to navigate roads safely. In finance, AI algorithms detect fraud and make 
    trading decisions. In entertainment, AI powers recommendation systems and creates personalized content. 
    However, the rapid advancement of AI also raises important ethical and societal questions. Issues such as 
    job displacement, privacy concerns, algorithmic bias, and the need for transparency in AI decision-making 
    are actively being debated. As AI continues to evolve, it is crucial to develop frameworks for responsible 
    AI development and deployment. The future of AI holds immense promise, but it requires careful consideration 
    of its impact on society, economy, and human values. Collaboration between technologists, policymakers, 
    and society at large will be essential to harness the benefits of AI while mitigating its risks.
    """
    
    print("🧪 Testing AI PDF Summarizer - Improved Logic")
    print("=" * 60)
    
    # Test original text stats
    words, chars, sentences = get_text_stats(sample_text)
    print(f"📊 Original Text Stats:")
    print(f"   Words: {words:,}")
    print(f"   Characters: {chars:,}")
    print(f"   Sentences: {sentences}")
    print()
    
    # Test key sentence extraction
    print("🔍 Testing Key Sentence Extraction:")
    key_sentences = extract_key_sentences(sample_text, 3)
    key_summary = " ".join(key_sentences)
    key_words, _, _ = get_text_stats(key_summary)
    key_compression = (key_words / words) * 100
    
    print(f"   Extracted {len(key_sentences)} key sentences")
    print(f"   Summary words: {key_words}")
    print(f"   Compression ratio: {key_compression:.1f}%")
    print(f"   Size reduction: {100-key_compression:.1f}%")
    print()
    print("📝 Key Sentences Summary:")
    print(f"   {key_summary}")
    print()
    
    # Test intelligent summary for different lengths
    for length in ["short", "medium", "long"]:
        print(f"🎯 Testing Intelligent Summary ({length.upper()}):")
        intelligent_summary = create_intelligent_summary(sample_text, length)
        
        if intelligent_summary:
            intel_words, _, _ = get_text_stats(intelligent_summary)
            intel_compression = (intel_words / words) * 100
            print(f"   Summary words: {intel_words}")
            print(f"   Compression ratio: {intel_compression:.1f}%")
            print(f"   Size reduction: {100-intel_compression:.1f}%")
            print(f"   Summary: {intelligent_summary[:100]}...")
        else:
            print("   Would use AI summarization (text too long)")
        print()
    
    # Test with shorter text
    short_text = "AI is transforming healthcare. Machine learning helps doctors diagnose diseases faster."
    short_words, _, _ = get_text_stats(short_text)
    print(f"🔬 Testing with Short Text ({short_words} words):")
    short_summary = create_intelligent_summary(short_text, "short")
    if short_summary:
        short_sum_words, _, _ = get_text_stats(short_summary)
        print(f"   Original: {short_words} words")
        print(f"   Summary: {short_sum_words} words")
        print(f"   Summary: {short_summary}")
    print()
    
    print("✅ Summarization tests completed!")
    print("\n🎯 Expected Results:")
    print("   - Short summaries: 50-100 words (85-95% reduction)")
    print("   - Medium summaries: 100-200 words (80-90% reduction)")
    print("   - Long summaries: 200-300 words (70-85% reduction)")

if __name__ == "__main__":
    test_summarization()