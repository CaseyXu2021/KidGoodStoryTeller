import streamlit as st
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, GPT2Tokenizer, GPT2LMHeadModel, pipeline
import numpy as np
import os
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="🎭 Kid Good Story Teller",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stButton>button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    .story-box {
        background: rgba(255,255,255,0.1);
        border-left: 5px solid #f093fb;
        padding: 20px;
        border-radius: 10px;
        font-size: 16px;
        line-height: 1.8;
    }
    .progress-item {
        display: flex;
        align-items: center;
        margin: 10px 0;
        font-weight: bold;
    }
    .sidebar-title {
        color: #f5576c;
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Model loading function
@st.cache_resource
def load_models():
    """Load all necessary models"""
    # Image to Text model
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model_img2text = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        torch_dtype=torch.float16
    ).to("cpu")
    
    # Story generation model
    story_tokenizer = GPT2Tokenizer.from_pretrained("pranavpsv/gpt2-genre-story-generator")
    story_model = GPT2LMHeadModel.from_pretrained(
        "pranavpsv/gpt2-genre-story-generator"
    ).to("cpu")
    
    # Text to Speech model
    tts_pipeline = pipeline(
        "text-to-speech",
        model="Matthijs/mms-tts-eng",
        device=-1
    )
    
    return processor, model_img2text, story_tokenizer, story_model, tts_pipeline

def img2text(image_path):
    """Convert image to text description using BLIP model"""
    processor, model_img2text, _, _, _ = load_models()
    
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt").to("cpu")
    
    out = model_img2text.generate(**inputs, max_length=77)
    caption = processor.decode(out[0], skip_special_tokens=True)
    
    return caption, image

def text2story(caption):
    """Generate a story from image caption"""
    _, _, story_tokenizer, story_model, _ = load_models()
    
    prompt = f"In a land far away, {caption}. "
    
    input_ids = story_tokenizer.encode(prompt, return_tensors="pt")
    
    story_output = story_model.generate(
        input_ids,
        max_length=120,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.2,
        pad_token_id=story_tokenizer.eos_token_id,
        num_return_sequences=1
    )
    
    story = story_tokenizer.decode(story_output[0], skip_special_tokens=True)
    return story

def story2audio(story_text):
    """Convert story text to audio"""
    _, _, _, _, tts_pipeline = load_models()
    
    # Generate audio
    audio = tts_pipeline(story_text[:500], forward_params={"speaker_embeddings": None})
    
    return audio

def save_uploaded_file(uploaded_file, folder="uploads"):
    """Save uploaded file to local directory"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def process_image_to_story(image_path):
    """Main processing pipeline: Image -> Caption -> Story -> Audio"""
    caption, image = img2text(image_path)
    story = text2story(caption)
    audio = story2audio(story)
    
    return caption, story, audio, image

def show_sidebar_progress():
    """Display progress in sidebar"""
    st.sidebar.markdown("### ⭐ Progress Tracker")
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    steps = [
        "📸 Upload Image",
        "🎨 Generate Caption",
        "📚 Create Story",
        "🔊 Generate Audio"
    ]
    
    for i, step in enumerate(steps):
        if i < st.session_state.current_step:
            st.sidebar.markdown(f"⭐ {step}")
        elif i == st.session_state.current_step:
            st.sidebar.markdown(f"🌟 {step}")
        else:
            st.sidebar.markdown(f"☆ {step}")

# Main app
def main():
    st.title("🎭 Kid Good Story Teller")
    st.markdown("### Transform Your Pictures into Amazing Stories! 📖✨")
    st.markdown("Upload an image and let AI create a magical story for you!")
    
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    # Sidebar progress tracker
    show_sidebar_progress()
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📷 Step 1: Upload Your Image")
        uploaded_file = st.file_uploader(
            "Choose an image (JPG, PNG, or GIF)",
            type=["jpg", "png", "gif", "jpeg"]
        )
        
        if uploaded_file is not None:
            st.session_state.current_step = 1
            st.image(uploaded_file, caption="Your uploaded image", use_column_width=True)
    
    if uploaded_file is not None:
        with col2:
            st.markdown("### 🎬 Processing Steps")
            
            if st.button("🚀 Create Story!", key="process_btn"):
                st.session_state.current_step = 2
                
                # Save uploaded file
                file_path = save_uploaded_file(uploaded_file)
                
                # Step 1: Generate Caption
                with st.spinner("🎨 Analyzing your image..."):
                    caption, image = img2text(file_path)
                    st.session_state.current_step = 2
                    st.success(f"✨ Caption: {caption}")
                
                # Step 2: Generate Story
                with st.spinner("📚 Writing your story..."):
                    story = text2story(caption)
                    st.session_state.current_step = 3
                    st.success("📖 Story created!")
                
                # Step 3: Generate Audio
                with st.spinner("🔊 Creating audio narration..."):
                    try:
                        audio = story2audio(story)
                        st.session_state.current_step = 4
                        st.success("🎵 Audio ready!")
                    except Exception as e:
                        st.warning(f"Audio generation note: {str(e)}")
                
                # Display results
                st.markdown("---")
                st.markdown("### 📖 Your Story")
                st.markdown(f'<div class="story-box">{story}</div>', unsafe_allow_html=True)
                
                # Display caption
                with st.expander("📝 Image Caption"):
                    st.write(caption)
                
                # Try to display audio if available
                if 'audio' in locals():
                    st.markdown("### 🎵 Story Narration")
                    try:
                        st.audio(audio.get("audio", ""), format="audio/wav")
                    except:
                        st.info("Audio narration is ready but cannot be displayed here.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888; margin-top: 30px;'>
            <p>🎓 Created for children aged 10+ | Powered by AI</p>
            <p>Transform imagination into stories! 🚀</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
