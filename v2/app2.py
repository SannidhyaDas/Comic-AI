import streamlit as st
from main2 import ComicGenerator, validate_inputs, check_api_keys
from io import BytesIO
import time

# Page configuration
st.set_page_config(
    page_title="Video to Comic Generator Pro",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
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
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #4ECDC4 0%, #FF6B6B 100%);
    }
    .service-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    .service-openai {
        background-color: #10a37f;
        color: white;
    }
    .service-imagen {
        background-color: #4285f4;
        color: white;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d1e7dd;
        border: 1px solid #a3cfbb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'enhanced_prompt' not in st.session_state:
    st.session_state.enhanced_prompt = None
if 'service_used' not in st.session_state:
    st.session_state.service_used = None
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False
if 'warning_message' not in st.session_state:
    st.session_state.warning_message = None

# Header
st.markdown('<p class="main-header">🎬 Video to Comic Generator</p>', unsafe_allow_html=True)
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
    
    # Service selection
    st.markdown("---")
    st.markdown("### ⚙️ Service Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        primary_service = st.selectbox(
            "Primary Service",
            ["openai", "imagen"],
            help="Service to try first"
        )
    with col2:
        fallback_service = st.selectbox(
            "Fallback Service",
            ["openai", "imagen"],
            help="Service to use if primary fails",
            index=1 if primary_service == "openai" else 0
        )
    
    # Validate API keys
    api_keys = check_api_keys()
    if not api_keys["gemini"]:
        st.error("❌ GEMINI_API_KEY is not configured in .env file")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 Generate Comic", type="primary", use_container_width=True)

# Generation process
if generate_button:
    # Validate inputs
    is_valid, error_message = validate_inputs(video_url, user_input)
    
    if not is_valid:
        st.error(f"❌ {error_message}")
    elif not api_keys["gemini"]:
        st.error("❌ Cannot generate comic without GEMINI_API_KEY")
    else:
        # Reset previous results
        st.session_state.generated_image = None
        st.session_state.enhanced_prompt = None
        st.session_state.service_used = None
        st.session_state.generation_complete = False
        st.session_state.warning_message = None
        
        try:
            # Initialize generator
            generator = ComicGenerator(primary_service=primary_service, fallback_service=fallback_service)
            
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
                result = generator.generate_comic(video_url, user_input)
                image, enhanced_prompt, service_used, warning = result
                
            if image is not None:
                st.success("✅ Comic generated successfully!")
                
                # Show service used
                if service_used:
                    class_name = "service-openai" if service_used == "openai" else "service-imagen"
                    st.markdown(f'<span class="service-badge {class_name}">Generated with {service_used.upper()}</span>', unsafe_allow_html=True)
                
                # Show warning if any
                if warning:
                    st.markdown(f'<div class="warning-box">⚠️ {warning}</div>', unsafe_allow_html=True)
                
                # Save to session state
                st.session_state.generated_image = image
                st.session_state.enhanced_prompt = enhanced_prompt
                st.session_state.service_used = service_used
                st.session_state.generation_complete = True
                st.session_state.warning_message = warning
            else:
                st.error(f"❌ Comic generation failed: {enhanced_prompt}")
                if not api_keys["openai"] and primary_service == "openai":
                    st.info("💡 Tip: OpenAI API key not configured. Try setting primary service to 'imagen'.")
                    
        except ValueError as e:
            st.error(f"❌ Configuration Error: {str(e)}")
            st.info("💡 Please check that your GEMINI_API_KEY is set in the .env file")
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ {error_msg}")
            
            # Additional helpful tips based on error
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                st.info("💡 Tip: The API has daily usage limits. Try again after the quota resets.")
            elif "billing" in error_msg.lower():
                st.info("💡 Tip: Enable billing in your Google Cloud account to use this model.")
            elif "permission" in error_msg.lower():
                st.info("💡 Tip: Verify your API key has the correct permissions in Google AI Studio.")
            elif "invalid" in error_msg.lower() and "url" in error_msg.lower():
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
    
    # Service information
    if st.session_state.service_used:
        class_name = "service-openai" if st.session_state.service_used == "openai" else "service-imagen"
        st.markdown(f'<span class="service-badge {class_name}">Generated with {st.session_state.service_used.upper()}</span>', unsafe_allow_html=True)
    
    # Warning message
    if st.session_state.warning_message:
        st.markdown(f'<div class="warning-box">⚠️ {st.session_state.warning_message}</div>', unsafe_allow_html=True)
    
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
            mime="image/png",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>Powered by Google Gemini AI | Built with Streamlit</p>
        <p>🎬 Transform your videos into engaging comic strips</p>
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
    
    3. **Configure Services**
       - Choose primary and fallback services
       - OpenAI: Best text rendering
       - Imagen: High quality images
    
    4. **Generate**
       - Click the generate button
       - Wait for AI processing
       - Download your comic!
    """)
    
    st.markdown("---")
    st.markdown("## 🔑 API Key Status")
    
    # API Key status
    keys_status = check_api_keys()
    if keys_status["openai"]:
        st.success("✅ OPENAI_API_KEY: Configured")
    else:
        st.error("❌ OPENAI_API_KEY: Not configured")
    
    if keys_status["gemini"]:
        st.success("✅ GEMINI_API_KEY: Configured")
    else:
        st.error("❌ GEMINI_API_KEY: Not configured")
    
    # Services available
    st.markdown("---")
    st.markdown("## 💡 Available Services")
    
    if keys_status["openai"]:
        st.markdown("""
        <div class="success-box">
            <strong>🟢 OpenAI (gpt-image-1)</strong><br>
            - Excellent text rendering<br>
            - Fast generation<br>
            - Requires API key with credits
        </div>
        """, unsafe_allow_html=True)
    
    if keys_status["gemini"]:
        st.markdown("""
        <div class="success-box">
            <strong>🟢 Google Imagen</strong><br>
            - High quality images<br>
            - Requires billing enabled<br>
            - Fallback option if OpenAI fails
        </div>
        """, unsafe_allow_html=True)
    
    if not keys_status["openai"] and not keys_status["gemini"]:
        st.warning("Configure API keys in your .env file to use services")
    
    st.markdown("---")
    st.markdown("## 💡 Tips")
    st.markdown("""
    - Use detailed descriptions for better results
    - Specify character emotions and actions
    - Mention desired comic style (manga, superhero, etc.)
    - Keep videos under 2 minutes for faster processing
    """)
