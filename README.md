# Comic-AI ([🌐Live Demo](https://sannidhya-das-comic-ai.streamlit.app))

![app_img_1](https://github.com/SannidhyaDas/Comic-AI/blob/main/assets/app_interface1.png)
![app_img_1](https://github.com/SannidhyaDas/Comic-AI/blob/main/assets/app_interface2.png)

Turn any YouTube video or uploaded video into a comic strip using AI! 🎨 Transform your favorite moments into shareable comic art with just a few clicks.
---
## 🌟 Features

- **Convert Videos to Comics**: Turn YouTube videos or uploaded videos into 4-panel comic strips
- **AI-Powered**: Uses advanced AI models (OpenAI + Google Imagen) to generate high-quality comics
- **Natural Language Prompts**: Describe your comic in plain English
- **Dual AI Engine**: Primary and fallback AI models for maximum reliability
- **Professional Quality**: High-resolution 1024×1024 comic strips
- **Easy to Use**: Simple web interface with Streamlit
- **Free & Open Source**: No cost for setup and deployment

## 🎥 Demo

### Input Video
[![Sample Video](https://img.youtube.com/vi/_AYnFtU56hE/maxresdefault.jpg)](https://www.youtube.com/watch?v=_AYnFtU56hE)

### Generated Comic
![Sample Comic](https://github.com/SannidhyaDas/Comic-AI/blob/main/assets/generated_img1.png)

## 🔧 How It Works

1. **Video Analysis**: Uses Gemini AI to analyze video content and context
2. **Prompt Enhancement**: Transforms user descriptions into detailed AI prompts
3. **Comic Generation**: Generates comics using OpenAI's gpt-image-1 or Google's Imagen
4. **Fallback System**: Automatic fallback to secondary AI if primary fails
5. **Web Interface**: Streamlit-based UI for easy interaction
---
## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- YouTube video URL or video file
- API keys (see below)

### Installation
Clone the repository
```bash
git clone https://github.com/SannidhyaDas/Comic-AI.git
cd Comic-AI
```
Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```
Install dependencies
```bash
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file in the project root:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

2. Get your API keys:
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com)
- **OpenAI API Key**: [OpenAI Platform](https://platform.openai.com)

### Running the App

Run the Streamlit app
```bash
streamlit run app2.py
```
Open your browser to [http://localhost:8501]
---

## 🛠️ Technical Architecture

```mermaid
graph TD
A[User Input] --> B(YouTube Video URL + Comic Description)
B --> C{Video Analysis}
C -->|Gemini API| D(Prompt Enhancement)
D --> E{Comic Generation}
E -->|Primary: OpenAI gpt-image-1| F[Comic Strip]
E -->|Fallback: Google Imagen| F
F --> G[Streamlit Web Interface]
G --> H[User Output]
```
---

## 📦 Project Structure


