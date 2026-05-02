# ============================================
# Kids Story Creator - AI Picture to Story App
# Designed for Children aged 10+
# ============================================

import streamlit as st
from transformers import pipeline
import os
import time

# ============================================
# Page Configuration
# ============================================
st.set_page_config(
    page_title="Kids Story Creator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# Custom Styling and Theme
# ============================================
st.markdown("""
    <style>
        .main {
            background-color: #f0f8ff;
        }
        .stButton>button {
            background-color: #FF6B6B;
            color: white;
            font-size: 18px;
            padding: 15px 30px;
            border-radius: 10px;
        }
        .stButton>button:hover {
            background-color: #FF5252;
        }
        .stSubheader {
            color: #FF6B6B;
        }
        .success-box {
            background-color: #D4F1D4;
            padding: 10px;
            border-radius: 5px;
        }
        .story-box {
            background-color: #FFF9E6;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #FFD700;
            font-size: 18px;
            line-height: 1.8;
        }
        .progress-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 24px;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================
# Session State for Progress Tracking
# ============================================
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0  # 0: idle, 1: image analysis, 2: story creation, 3: audio generation

# ============================================
# Function Definitions
# ============================================

def img2text(image_path: str) -> str:
    """
    Convert image to text description using AI vision model
    """
    try:
        image_to_text_model = pipeline(
            "image-to-text",
            model="Salesforce/blip-image-captioning-base"
        )
        text = image_to_text_model(image_path)[0]["generated_text"]
        return text
    except Exception as e:
        st.error(f"❌ Image recognition error: {str(e)}")
        return None

def text2story(caption: str) -> str:
    """
    Expand image description into a full, vivid story
    Fine-tuned parameters to keep story closer to original picture context
    """
    try:
        story_generator = pipeline(
            "text-generation",
            model="pranavpsv/genre-story-generator-v2"
        )
        results = story_generator(
            caption,
            max_length=120,  # Control story length
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,  # Lower temp for more focused, coherent stories
            top_p=0.9,  # Add top_p for better nucleus sampling
            repetition_penalty=1.2,  # Avoid repetitive text
            truncation=True
        )
        story = results[0]['generated_text']
        
        # Word count control (80-120 words) - keep story focused on the image
        words = story.split()
        if len(words) > 120:
            story = ' '.join(words[:120])
        elif len(words) < 50:
            # If story is too short, add more context related to caption
            story = story + " " + caption + " " + story
        
        return story
    except Exception as e:
        st.error(f"❌ Story generation error: {str(e)}")
        return None

def story2audio(story_text: str):
    """
    Convert story text to speech audio using AI voice model
    """
    try:
        audio_pipe = pipeline(
            "text-to-audio",
            model="Matthijs/mms-tts-eng"
        )
        audio_data = audio_pipe(story_text)
        return audio_data
    except Exception as e:
        st.error(f"❌ Audio generation error: {str(e)}")
        return None

def save_uploaded_file(uploaded_file) -> str:
    """
    Save uploaded image file to temporary directory
    """
    try:
        if not os.path.exists("temp_images"):
            os.makedirs("temp_images")
        
        file_path = os.path.join("temp_images", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return file_path
    except Exception as e:
        st.error(f"❌ File save error: {str(e)}")
        return None

def show_progress_bar(step: int):
    """
    Display animated progress bar with moving star emoji
    step: 0=idle, 1=analyzing image, 2=creating story, 3=generating audio, 4=complete
    """
    steps = ["📌 Start", "📸 Image", "📖 Story", "🎵 Audio", "✅ Done"]
    
    # Create progress bar with moving star
    progress_html = '<div class="progress-bar">'
    for i, step_name in enumerate(steps):
        if i < step:
            # Completed steps
            progress_html += f'<div style="color: #4CAF50; font-weight: bold;">⭐{step_name}</div>'
        elif i == step:
            # Current step - animated star
            progress_html += f'<div style="color: #FF6B6B; font-weight: bold; font-size: 28px;">⭐{step_name}</div>'
        else:
            # Future steps
            progress_html += f'<div style="color: #999;">☆{step_name}</div>'
    
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

def process_image_to_story(image_path: str):
    """
    Complete 3-stage pipeline: Image → Text → Story → Audio
    With animated progress indicator
    """
    # Stage 1: Image to Text
    st.session_state.current_step = 1
    show_progress_bar(1)
    
    st.subheader("📸 Step 1: Understanding Your Picture")
    st.text("AI robot is analyzing your image...")
    
    with st.spinner("🤔 Analyzing..."):
        caption = img2text(image_path)
    
    if caption:
        st.success(f"✅ Image Description: **{caption}**")
    else:
        return
    
    time.sleep(0.5)  # Brief pause for visual feedback
    
    # Stage 2: Text to Story
    st.session_state.current_step = 2
    show_progress_bar(2)
    
    st.subheader("📖 Step 2: Writing Your Story")
    st.text("AI author is creating an exciting story inspired by your image...")
    
    with st.spinner("✍️ Creating story..."):
        story = text2story(caption)
    
    if story:
        # Display story in larger font
        st.markdown(
            f'<div class="story-box"><b>🎉 Your Amazing Story:</b><br><br>{story}</div>',
            unsafe_allow_html=True
        )
    else:
        return
    
    time.sleep(0.5)
    
    # Stage 3: Story to Audio
    st.session_state.current_step = 3
    show_progress_bar(3)
    
    st.subheader("🎵 Step 3: Creating Voice Narration")
    st.text("AI voice actor is recording your story...")
    
    with st.spinner("🎤 Generating audio..."):
        audio_output = story2audio(story)
    
    if audio_output:
        audio_array = audio_output["audio"]
        sample_rate = audio_output["sampling_rate"]
        
        st.session_state.current_step = 4
        show_progress_bar(4)
        
        st.success("✅ Story narration complete!")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎧 Listen to Your Story")
            st.audio(audio_array, sample_rate=sample_rate)
        
        with col2:
            st.subheader("📢 How to Enjoy")
            st.info("Click the play button above to hear your story narrated by AI!")
            st.markdown("**Enjoy your magical story! 🎭✨**")

# ============================================
# Main Application UI
# ============================================

# Title and Welcome Section
st.header("🎨 Kids Story Creator - Turn Pictures into Stories")
st.markdown("""
---
### 👋 Welcome to the Magic Story Factory!
**Upload a picture and let AI create an exciting story for you!** 🎭

**This app has 3 amazing steps:**
1. 📸 **Image Recognition** - AI looks at your picture and describes what it sees
2. 📖 **Story Creation** - AI author transforms the description into a full story
3. 🎵 **Voice Narration** - AI voice actor reads your story out loud

---
""")

# Sidebar with Tips
with st.sidebar:
    st.subheader("💡 Helpful Tips")
    st.info("""
    🖼️ **Best pictures for this app:**
    - Clear, well-lit photos
    - Pictures with interesting people or animals
    - Not too complex or busy
    
    ⚠️ **Important Notes:**
    - First run downloads AI models (5-15 minutes)
    - Please be patient! ⏳
    - Works best with English descriptions
    """)
    
    st.markdown("---")
    st.subheader("ℹ️ About This Project")
    st.success("""
    **Learn AI Technology!**
    
    This app uses:
    - **BLIP AI** - Sees pictures
    - **GPT-2** - Writes stories  
    - **MMS-TTS** - Creates voices
    
    These are top-level AI technologies! 🚀
    """)

# Main Functionality Area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload Your Picture")
    uploaded_file = st.file_uploader(
        "Choose a JPG or PNG image",
        type=["jpg", "jpeg", "png"],
        help="Click to select or drag and drop your image here"
    )
    
    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="📸 Your Uploaded Picture",
            use_column_width=True
        )
        
        # Save file
        image_path = save_uploaded_file(uploaded_file)
        
        if image_path:
            st.markdown("---")
            st.session_state.current_step = 0
            
            # Create story generation button
            if st.button("🚀 Create My Story!", use_container_width=True):
                st.markdown("---")
                process_image_to_story(image_path)

with col2:
    st.subheader("🎨 How It Works")
    st.markdown("""
    **Step 1️⃣**
    Upload a picture
    
    **Step 2️⃣**
    Click the button
    
    **Step 3️⃣**
    Enjoy your story! 
    
    It's that easy! 😊
    """)

# Footer
st.markdown("""
---
### 🎓 Course Project
- **Course:** ISOM5240 - Python Programming
- **Project:** AI Story Creator
- **Technology:** Streamlit + Transformers + PyTorch

**Have fun creating stories! 🎉✨**
""")
