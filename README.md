# 🎭 Kid Good Story Teller

Transform pictures into magical stories! An AI-powered storytelling application for children aged 10+.

## 🌟 Features

- **📸 Image Recognition**: Upload any image and let AI analyze it
- **📚 Story Generation**: Automatically creates engaging stories based on images
- **🎵 Voice Narration**: Text-to-speech conversion for immersive experience
- **✨ Interactive UI**: Beautiful, child-friendly Streamlit interface
- **📊 Progress Tracking**: Visual progress indicator for each step

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. Clone the repository:
```bash
git clone https://github.com/CaseyXu2021/KidGoodStoryTeller.git
cd KidGoodStoryTeller
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

Then open your browser and navigate to `http://localhost:8501`

## 🎨 How It Works

1. **Upload Image**: Select an image from your device
2. **Image Analysis**: AI creates a detailed caption of the image
3. **Story Generation**: Based on the caption, AI generates a unique 80-120 word story
4. **Voice Narration**: Story is converted to natural-sounding audio

## 🏗️ Project Structure

```
KidGoodStoryTeller/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore patterns
└── story-vocab-extension/   # VS Code extension (optional)
    ├── extension.ts
    ├── vocabularyHighlighter.ts
    ├── dictionaryLookup.ts
    └── package.json
```

## 🧠 AI Models Used

- **Salesforce/BLIP**: Image captioning - converts images to text descriptions
- **pranavpsv/genre-story-generator**: Story generation - creates engaging narratives
- **Matthijs/mms-tts-eng**: Text-to-speech - provides audio narration
- **PyTorch**: Deep learning inference engine

## 📋 Requirements

All requirements are specified in `requirements.txt`:
- streamlit 1.28.0
- torch 2.0.0
- transformers 4.32.0
- Pillow 10.0.0
- numpy 1.24.3

## 🎯 Target Audience

- Children aged 10+
- Teachers and educators
- Parents looking for creative storytelling tools

## 💡 Future Enhancements

- [ ] Story customization (length, theme, genre)
- [ ] Multi-language support
- [ ] Story export to PDF/ePUB
- [ ] User feedback system
- [ ] Story history/library

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

Created by Casey Xu

## 🙏 Acknowledgments

- Hugging Face community for excellent pre-trained models
- Streamlit for the amazing web framework
- All contributors and testers

---

**Transform imagination into stories! 🚀✨**
