# ============================================
# 图片转故事应用 - 为10岁小孩设计
# Picture to Story App - Designed for Kids aged 10
# ============================================

import streamlit as st
from transformers import pipeline
import os

# ============================================
# 页面配置 / Page Configuration
# ============================================
st.set_page_config(
    page_title="Kids Story Creator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 自定义样式和主题 / Custom Styling
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
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #FFD700;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================
# 函数定义 / Function Definitions
# ============================================

def img2text(image_path: str) -> str:
    """
    将图片转换为文字描述
    Convert image to text description
    """
    try:
        image_to_text_model = pipeline(
            "image-to-text",
            model="Salesforce/blip-image-captioning-base"
        )
        text = image_to_text_model(image_path)[0]["generated_text"]
        return text
    except Exception as e:
        st.error(f"❌ 图片识别出错: {str(e)}")
        return None

def text2story(caption: str) -> str:
    """
    将简短描述扩展为故事
    Expand caption into a full story
    """
    try:
        story_generator = pipeline(
            "text-generation",
            model="pranavpsv/genre-story-generator-v2"
        )
        results = story_generator(
            caption,
            max_length=150,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.8,
            truncation=True
        )
        story = results[0]['generated_text']
        
        # 字数控制逻辑 (100-150 词)
        words = story.split()
        if len(words) > 150:
            story = ' '.join(words[:150])
        
        return story
    except Exception as e:
        st.error(f"❌ 故事生成出错: {str(e)}")
        return None

def story2audio(story_text: str):
    """
    将故事转换为音频
    Convert story to audio
    """
    try:
        audio_pipe = pipeline(
            "text-to-audio",
            model="Matthijs/mms-tts-eng"
        )
        audio_data = audio_pipe(story_text)
        return audio_data
    except Exception as e:
        st.error(f"❌ 音频生成出错: {str(e)}")
        return None

def save_uploaded_file(uploaded_file) -> str:
    """
    保存上传的文件到临时目录
    Save uploaded file to temporary directory
    """
    try:
        # 创建临时目录
        if not os.path.exists("temp_images"):
            os.makedirs("temp_images")
        
        file_path = os.path.join("temp_images", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return file_path
    except Exception as e:
        st.error(f"❌ 文件保存出错: {str(e)}")
        return None

def process_image_to_story(image_path: str):
    """
    完整的三阶段流程：图片 → 文本 → 故事 → 音频
    Complete 3-stage pipeline: Image → Text → Story → Audio
    """
    # 阶段 1: 图片转文本
    st.subheader("📸 第一步：理解图片")
    st.text("AI 机器人正在看你的图片...")
    
    with st.spinner("🤔 分析中..."):
        caption = img2text(image_path)
    
    if caption:
        st.success(f"✅ 图片描述：**{caption}**")
    else:
        return
    
    # 阶段 2: 文本转故事
    st.subheader("📖 第二步：编写故事")
    st.text("AI 作家正在创作一个有趣的故事...")
    
    with st.spinner("✍️ 创作中..."):
        story = text2story(caption)
    
    if story:
        st.markdown(
            f'<div class="story-box"><b>🎉 你的故事：</b><br>{story}</div>',
            unsafe_allow_html=True
        )
    else:
        return
    
    # 阶段 3: 故事转音频
    st.subheader("🎵 第三步：生成语音")
    st.text("AI 播音员正在为故事配音...")
    
    with st.spinner("🎤 配音中..."):
        audio_output = story2audio(story)
    
    if audio_output:
        audio_array = audio_output["audio"]
        sample_rate = audio_output["sampling_rate"]
        
        st.success("✅ 故事配音完成！")
        col1, col2 = st.columns(2)
        
        with col1:
            st.audio(audio_array, sample_rate=sample_rate)
        
        with col2:
            st.info("📢 点击上面的播放按钮听你的故事！")

# ============================================
# 主应用界面 / Main Application UI
# ============================================

# 标题和欢迎信息
st.title("🎨 小孩故事创作机 Kids Story Creator")
st.markdown("""
---
### 👋 欢迎来到魔法故事工厂！
**选择一张图片，让 AI 为你编造一个有趣的故事吧！** 🎭

**这个应用有 3 个神奇步骤：**
1. 📸 **图片识别** - AI 看你的图片，说出它看到了什么
2. 📖 **故事创作** - AI 作家把描述变成一个完整的故事
3. 🎵 **语音朗读** - AI 播音员为你的故事配音

---
""")

# 创建侧边栏帮助信息
with st.sidebar:
    st.subheader("💡 小提示")
    st.info("""
    🖼️ **上传图片的建议：**
    - 图片要清晰，光线要好
    - 最好包含有趣的人物或动物
    - 图片不要太复杂
    
    ⚠️ **注意：**
    - 首次运行需要下载 AI 模型 (可能需要 5-15 分钟)
    - 请耐心等待~
    """)

# 主要功能区域
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 上传你的图片")
    uploaded_file = st.file_uploader(
        "选择一张 JPG 或 PNG 的图片",
        type=["jpg", "jpeg", "png"],
        help="点击选择或直接拖拽图片到这里"
    )
    
    # 显示上传的图片
    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="📸 你上传的图片",
            use_column_width=True
        )
        
        # 保存文件
        image_path = save_uploaded_file(uploaded_file)
        
        if image_path:
            st.markdown("---")
            
            # 创建生成按钮
            if st.button("🚀 开始创作故事!", use_container_width=True):
                # 开始三阶段流程
                process_image_to_story(image_path)
            
            st.markdown("---")

with col2:
    st.subheader("📋 你知道吗？")
    st.success("""
    ✨ 这个应用使用了：
    - **BLIP 视觉 AI** - 看图片
    - **GPT-2** - 写故事  
    - **MMS-TTS** - 配音
    
    都是世界顶级的 AI 技术哦！
    """)

# 底部信息
st.markdown("""
---
**🎓 课程项目**
- 课程: ISOM5240 - Python编程
- 项目: AI 讲故事应用
- 技术: Streamlit + Transformers + PyTorch

**祝你玩得开心！🎉**
""")
