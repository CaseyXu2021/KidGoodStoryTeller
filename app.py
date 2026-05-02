import streamlit as st
from PIL import Image
from transformers import pipeline
import os
from pathlib import Path

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

# Model loading cache
@st.cache_resource
def load_image_to_text_pipeline():
    """Load image-to-text pipeline"""
    return pipeline("image-to-text", model="Salesforce/blip-base")

@st.cache_resource
def load_text_generation_pipeline():
    """Load text generation pipeline"""
    return pipeline("text-generation", model="gpt2")

@st.cache_resource
def load_tts_pipeline():
    """Load text-to-speech pipeline"""
    try:
        return pipeline("text-to-speech", model="espnet/kan-bayashi_ljspeech_fastspeech2")
    except:
        return None

def img2text(image_path):
    """Convert image to text description using image-to-text model"""
    try:
        img2txt_pipeline = load_image_to_text_pipeline()
        image = Image.open(image_path).convert("RGB")
        result = img2txt_pipeline(image)
        caption = result[0]['generated_text'] if result else "A mysterious scene unfolds"
        return caption, image
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return "A story waiting to be told", Image.open(image_path)


def text2story(caption):
    """Generate a story from image caption"""
    try:
        text_gen_pipeline = load_text_generation_pipeline()
        prompt = f"Once upon a time, {caption}. "
        
        result = text_gen_pipeline(
            prompt,
            max_length=150,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9
        )
        
        story = result[0]['generated_text'] if result else prompt
        return story[:300]  # Limit story length
    except Exception as e:
        st.error(f"Error generating story: {str(e)}")
        return f"Once upon a time, {caption}. And they lived happily ever after."

def story2audio(story_text):
    """Convert story text to audio (optional - may fail on Streamlit Cloud)"""
    try:
        tts_pipeline = load_tts_pipeline()
        if tts_pipeline:
            audio = tts_pipeline(story_text[:200])
            return audio
    except Exception as e:
        st.warning(f"Audio generation unavailable: {str(e)}")
    return None

def save_uploaded_file(uploaded_file, folder="uploads"):
    """Save uploaded file to local directory"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def process_image_to_story(image_path):
    """Main processing pipeline: Image -> Caption -> Story"""
    try:
        caption, image = img2text(image_path)
        story = text2story(caption)
        return caption, story, image
    except Exception as e:
        st.error(f"Error processing: {str(e)}")
        return "Error", "Unable to process image", None

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
            st.image(uploaded_file, caption="Your uploaded image", width=400)
    
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
                
                # Display results
                st.markdown("---")
                st.markdown("### 📖 Your Story")
                st.markdown(f'<div class="story-box">{story}</div>', unsafe_allow_html=True)
                
                # Display caption
                with st.expander("📝 Image Caption"):
                    st.write(caption)
    
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
