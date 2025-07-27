# 🔒 AI PDF Summarizer

A secure, local PDF summarization tool that processes your confidential documents without sending data to external APIs.

## ✨ Features

- **🔒 Complete Privacy**: All processing happens locally - your documents never leave your browser
- **📄 Multi-PDF Support**: Upload and summarize multiple PDF files at once
- **🤖 AI-Powered**: Uses DistilBART model for high-quality summaries
- **🎨 Perfect Theming**: Adaptive light/dark theme support
- **📊 Smart Analytics**: Processing stats and compression ratios
- **💾 Easy Export**: Download summaries as text files
- **⚡ Fast Processing**: Optimized for cloud deployment

## 🚀 Live Demo

**[Try it now on Streamlit Cloud!](https://your-app-url.streamlit.app)**

## 🛠️ Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-summarizer.git
cd pdf-summarizer

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 📋 Requirements

- Python 3.8+
- Streamlit
- PyPDF2
- Transformers
- PyTorch
- Requests

## 🎯 How to Use

1. **Upload PDFs**: Drag and drop or select your PDF files
2. **Choose Length**: Select summary detail level (Short/Medium/Long)
3. **Generate**: Click "Summarize PDFs" to process
4. **Download**: Save your summary as a text file

## 🔧 Configuration

The app includes several customizable features:

- **Summary Lengths**: 3-5, 5-8, or 8-12 sentences
- **Theme Support**: Automatic light/dark theme adaptation
- **File Limits**: Supports multiple PDFs up to 200MB total
- **Processing**: Intelligent chunking for large documents

## 🌟 Perfect For

- **Business Documents**: Reports, proposals, contracts
- **Academic Papers**: Research papers, theses, articles
- **Legal Documents**: Contracts, agreements, policies
- **Technical Manuals**: User guides, documentation
- **Financial Reports**: Quarterly reports, analyses

## 🔒 Privacy & Security

- ✅ **No External APIs**: Everything runs locally
- ✅ **No Data Storage**: Files are processed in memory only
- ✅ **No Tracking**: No usage analytics or data collection
- ✅ **Open Source**: Full transparency in processing
- ✅ **Secure**: No data leaves your browser session

## 🎨 Screenshots

### Light Theme
![Light Theme](screenshots/light-theme.png)

### Dark Theme
![Dark Theme](screenshots/dark-theme.png)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- AI model: [DistilBART](https://huggingface.co/sshleifer/distilbart-cnn-12-6)
- PDF processing: [PyPDF2](https://pypdf2.readthedocs.io/)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/pdf-summarizer/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

---

**Made with ❤️ for secure document processing**