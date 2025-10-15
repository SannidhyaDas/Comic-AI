import streamlit as st
from main import ComicGenerator, validate_inputs
from io import BytesIO
import time

# Page configuration
st.set_page_config(
    page_title="Video to Comic Generator",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'enhanced_prompt' not in st.session_state:
    st.session_state.enhanced_prompt = None
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False

# Header
st.markdown('<p class="main-header">🎨 Video to Comic Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform your videos into comic strips using AI</p>', unsafe_allow_html=True)

# Main content
with st.container():
    # Video URL input
    st.markdown("### 📹 Video Input")
    video_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=... or https://youtube.com/shorts/...",
        help="Paste a YouTube video URL or YouTube Shorts URL"
    )
    
    # Example URLs
    with st.expander("📖 See example URLs"):
        st.code("https://www.youtube.com/watch?v=dQw4w9WgXcQ", language=None)
        st.code("https://www.youtube.com/watch?v=_AYnFtU56hE", language=None)
        st.code("https://www.youtube.com/shorts/Q42OFDakgXc", language=None)
    
    st.markdown("---")
    
    # Comic description input
    st.markdown("### ✍️ Comic Description")
    user_input = st.text_area(
        "Describe your comic",
        placeholder="Example: Make the girl a princess and the boy a knight. Add medieval castle backgrounds and fantasy elements.",
        height=120,
        help="Describe the characters, setting, or theme you want in your comic"
    )
    
    # Character count
    if user_input:
        st.caption(f"Character count: {len(user_input)}")
    
    st.markdown("---")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 Generate Comic", type="primary")

# Generation process
if generate_button:
    # Validate inputs
    is_valid, error_message = validate_inputs(video_url, user_input)
    
    if not is_valid:
        st.error(f"❌ {error_message}")
    else:
        # Reset previous results
        st.session_state.generated_image = None
        st.session_state.enhanced_prompt = None
        st.session_state.generation_complete = False
        
        try:
            # Initialize generator
            generator = ComicGenerator()
            
            # Step 1: Video Analysis
            with st.spinner("🔍 Analyzing video content..."):
                time.sleep(0.5)  # Brief pause for UX
                enhanced_prompt = generator.extract_comic_prompt_and_enhance(video_url, user_input)
            
            st.success("✅ Video analysis complete!")
            
            # Show enhanced prompt in expandable section
            with st.expander("📝 View Enhanced Prompt"):
                st.write(enhanced_prompt)
            
            # Step 2: Comic Generation
            with st.spinner("🎨 Generating your comic strip..."):
                image_bytes = generator.generate_comic_image(enhanced_prompt)
                image = generator.bytes_to_pil_image(image_bytes)
            
            st.success("✅ Comic generated successfully!")
            
            # Save to session state
            st.session_state.generated_image = image
            st.session_state.enhanced_prompt = enhanced_prompt
            st.session_state.generation_complete = True
            
        except ValueError as e:
            st.error(f"❌ Configuration Error: {str(e)}")
            st.info("💡 Please check that your GEMINI_API_KEY is set in the .env file")
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ {error_msg}")
            
            # Additional helpful tips based on error
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                st.info("💡 Tip: The Gemini API has daily usage limits. Try again after the quota resets.")
            elif "billing" in error_msg.lower():
                st.info("💡 Tip: Enable billing in your Google Cloud account to use this model.")
            elif "permission" in error_msg.lower():
                st.info("💡 Tip: Verify your API key has the correct permissions in Google AI Studio.")
            elif "url" in error_msg.lower():
                st.info("💡 Tip: Make sure the YouTube video is public and the URL is correct.")

# Display results
if st.session_state.generation_complete and st.session_state.generated_image:
    st.markdown("---")
    st.markdown("### 🎉 Your Comic Strip")
    
    # Display image
    st.image(
        st.session_state.generated_image,
        use_container_width=True,
        caption="Generated Comic Strip"
    )
    
    # Download button
    buf = BytesIO()
    st.session_state.generated_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="⬇️ Download Comic",
            data=byte_im,
            file_name="comic_strip.png",
            mime="image/png"
        )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>Powered by Google Gemini AI | Built with Streamlit</p>
        <p>🎨 Transform your videos into engaging comic strips</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar with instructions
with st.sidebar:
    st.markdown("## 📖 How to Use")
    st.markdown("""
    1. **Paste YouTube URL**
       - Copy any YouTube video or Shorts URL
       - Make sure the video is public
    
    2. **Describe Your Comic**
       - Add character descriptions
       - Specify themes or styles
       - Be creative!
    
    3. **Generate**
       - Click the generate button
       - Wait for AI processing
       - Download your comic!
    """)
    
    st.markdown("---")
    st.markdown("## ⚙️ Settings")
    
    # API Key status
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            st.success("✅ API Key loaded")
        else:
            st.error("❌ API Key missing")
            st.info("Add GEMINI_API_KEY to your .env file")
    except:
        st.warning("⚠️ Could not check API key")
    
    st.markdown("---")
    st.markdown("## 💡 Tips")
    st.markdown("""
    - Use detailed descriptions for better results
    - Specify character emotions and actions
    - Mention desired comic style (manga, superhero, etc.)
    - Keep videos under 2 minutes for faster processing
    """)
