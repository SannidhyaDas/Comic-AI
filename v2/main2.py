import os
from google import genai
from google.genai import types
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image as PILImage
from dotenv import load_dotenv

load_dotenv()

class ComicGenerator:
    """Video-to-comic generator with OpenAI and Imagen support."""
    
    def __init__(self, primary_service="openai", fallback_service="imagen"):
        """
        Initialize the comic generator.
        
        Args:
            primary_service: "openai" or "imagen"
            fallback_service: "openai" or "imagen"
        """
        # Load API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Export to environment
        os.environ["GEMINI_API_KEY"] = self.gemini_api_key
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
        
        # Initialize clients
        self.gemini_client = genai.Client(api_key=self.gemini_api_key)
        
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
        
        # Configuration
        self.primary_service = primary_service
        self.fallback_service = fallback_service
        self.openai_model = "gpt-image-1"
        self.imagen_model = "imagen-4.0-generate-001"
        self.gemini_model = "gemini-2.0-flash"
        
        # Available services
        self.services = {
            "openai": self._generate_with_openai,
            "imagen": self._generate_with_imagen
        }
    
    def extract_comic_prompt_and_enhance(self, video_url, user_input):
        """
        Analyze video and enhance comic prompt using Gemini.
        
        Args:
            video_url: YouTube URL or video file URI
            user_input: User's comic description
            
        Returns:
            Enhanced prompt string
            
        Raises:
            Exception: If video analysis fails
        """
        prompt = f"""
        You are an expert comic strip prompt creator. Your task is to generate a single, detailed ready-to-use prompt for an image generation AI. 
        You will use the user-provided panel descriptions and a video to create a complete prompt.

        ### User Inputs:
        {user_input}
        
        ### Your Task & Instructions:

        1. **Analyze and Enhance:** Watch the video at the provided URL: {video_url}. Based on the video's context, add relevant details to each of the four panel descriptions. Enhance the descriptions to make them more vivid and engaging.

        2. **Generate a Single Prompt:** Your entire output must be one single, cohesive prompt for the image generator.

        3. **Specify Format, Style, and Composition in the Final Prompt:** The final prompt you generate must explicitly instruct the image AI to create a comic strip with the following specifications:
           - **Layout:** A **4-panel** layout, arranged in a **2x2 grid**. Each panel must be **clearly framed and equally spaced**.
           - **Art Style:** A distinct **comic book art style only**. Strictly instruct for **no photorealism**.
           - **Text Elements:** Appropriate **dialogue in speech bubbles** and descriptive **caption text** for each panel.
           - **Compositional Integrity:** Ensure that **no part of the characters, speech bubbles, or dialogue is cropped or cut off** by the panel borders. All text inside speech bubbles must be **fully visible and legible**.

        4. **Set the Tone:** The comic must be **humorous**. Instruct the image AI to capture **exaggerated timing and over-the-top reactions**, in the style of classic internet memes.  

        5. **Content Moderation:**
           * You must strictly filter the final prompt to **remove any harmful or inappropriate content**.
           * **Handle Copyright-adjacent Material:**
                * If the user's input mentions a movie title, you **must remove the movie title** from your generated prompt. 
                * However, if a character name is mentioned, **keep the character name**. Your prompt should instruct the image AI to create a character that *resembles* the mentioned character, but is not an exact replica.
                * Replace any specific brands or logos with generic equivalents (e.g., "a soda can" instead of "Coca-Cola can").
                
        6. **Final Output:** Return only the final, complete prompt for the image AI without any of your own commentary, introductions, or extra text.
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model,
                contents=types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            file_data=types.FileData(file_uri=video_url)
                        )
                    ]
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Video analysis failed: {str(e)}")
    
    def _generate_with_openai(self, prompt):
        """Generate image using OpenAI's gpt-image-1 model."""
        if not self.openai_client:
            raise Exception("OpenAI API key not configured")
        
        result = self.openai_client.images.generate(
            model=self.openai_model,
            prompt=prompt,
            size="1024x1024"
        )
        
        # gpt-image-1 always returns b64_json by default
        image_data = result.data[0].b64_json
        image_bytes = base64.b64decode(image_data)
        return image_bytes
    
    def _generate_with_imagen(self, prompt):
        """Generate image using Google Imagen."""
        response = self.gemini_client.models.generate_images(
            model=self.imagen_model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )
        return response.generated_images[0].image
    
    def generate_image_with_fallback(self, prompt):
        """
        Generate image using primary service, fallback to secondary if needed.
        
        Args:
            prompt: Enhanced comic prompt
            
        Returns:
            tuple: (image_data, service_used, error_message)
        """
        # Try primary service
        try:
            if self.primary_service in self.services:
                image_data = self.services[self.primary_service](prompt)
                return image_data, self.primary_service, None
        except Exception as e:
            primary_error = self._parse_error(e, self.primary_service)
            
            # Try fallback service
            if self.fallback_service != self.primary_service:
                try:
                    if self.fallback_service in self.services:
                        image_data = self.services[self.fallback_service](prompt)
                        return image_data, self.fallback_service, f"Primary service failed: {primary_error}"
                except Exception as fallback_e:
                    fallback_error = self._parse_error(fallback_e, self.fallback_service)
                    return None, None, f"Primary: {primary_error}\nFallback: {fallback_error}"
            
            return None, None, primary_error
        
        return None, None, "No services configured"
    
    def _parse_error(self, error, service_name):
        """Parse error into user-friendly message."""
        error_msg = str(error)
        
        if "429" in error_msg or "quota" in error_msg.lower():
            return f"{service_name.upper()}: Daily limit reached. Please try again later."
        elif "400" in error_msg and "billed" in error_msg.lower():
            return f"{service_name.upper()}: Billing required. Please enable billing in your account."
        elif "401" in error_msg or "api key" in error_msg.lower():
            return f"{service_name.upper()}: Invalid API key. Please check your credentials."
        elif "403" in error_msg or "permission" in error_msg.lower():
            return f"{service_name.upper()}: Permission denied. Check API key permissions."
        elif "invalid" in error_msg.lower() and "url" in error_msg.lower():
            return "Invalid video URL. Ensure the YouTube video is publicly accessible."
        else:
            return f"{service_name.upper()}: {error_msg}"
    
    def bytes_to_pil_image(self, image_data):
        """Convert bytes to PIL Image."""
        if isinstance(image_data, bytes):
            return PILImage.open(BytesIO(image_data))
        return image_data
    
    def generate_comic(self, video_url, user_input):
        """
        Complete comic generation pipeline.
        
        Args:
            video_url: YouTube URL or video file URI
            user_input: User's comic description
            
        Returns:
            tuple: (PIL Image, enhanced_prompt, service_used, warning_message) or (None, error_message, None, None)
        """
        try:
            # Step 1: Analyze video and enhance prompt
            enhanced_prompt = self.extract_comic_prompt_and_enhance(video_url, user_input)
            
            # Step 2: Generate image with fallback
            image_data, service_used, warning = self.generate_image_with_fallback(enhanced_prompt)
            
            if image_data is None:
                return None, warning or "Image generation failed", None, None
            
            # Step 3: Convert to PIL Image
            image = self.bytes_to_pil_image(image_data)
            
            return image, enhanced_prompt, service_used, warning
            
        except Exception as e:
            return None, str(e), None, None


def validate_youtube_url(url):
    """Validate if the URL is a valid YouTube URL."""
    youtube_patterns = [
        'youtube.com/watch',
        'youtube.com/shorts',
        'youtu.be/',
        'm.youtube.com'
    ]
    return any(pattern in url for pattern in youtube_patterns)


def validate_inputs(video_url, user_input):
    """
    Validate user inputs.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not video_url or not video_url.strip():
        return False, "Please provide a video URL"
    
    if not user_input or not user_input.strip():
        return False, "Please provide a comic description"
    
    if not validate_youtube_url(video_url):
        return False, "Please provide a valid YouTube URL (youtube.com or youtu.be)"
    
    if len(user_input.strip()) < 10:
        return False, "Comic description is too short. Please provide more details (at least 10 characters)"
    
    return True, None


def check_api_keys():
    """
    Check which API keys are configured.
    
    Returns:
        dict: Status of each API key
    """
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY"))
    }
