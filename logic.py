import requests
import edge_tts
import asyncio
import random
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

# --- 1. AI SCRIPT GENERATOR (No Key Needed) ---
def get_ai_script(topic):
    """
    Uses Pollinations.ai (Free, No Key) to generate a short script.
    """
    print(f"🧠 Asking AI about: {topic}...")
    
    # We ask for a short, punchy script without special characters
    prompt = f"Write a 2-sentence hook for an Instagram Reel about {topic}. Do not use emojis or hashtags. Just the text."
    
    # Pollinations text API
    url = f"https://text.pollinations.ai/{prompt}"
    
    try:
        response = requests.get(url)
        script_text = response.text.strip()
        print(f"✅ Script: {script_text}")
        return script_text
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return f"Did you know that {topic} is fascinating? It changes how we see the world."

# --- 2. VIDEO FINDER (Mixkit Scraper) ---
def get_video(topic):
    """
    Finds a video on Mixkit based on the topic.
    """
    print(f"🕵️ Looking for video: {topic}...")
    search_url = f"https://mixkit.co/free-stock-video/{topic}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        videos = soup.find_all('video')
        
        # Default backup video if search fails
        video_url = "https://assets.mixkit.co/videos/preview/mixkit-waves-coming-to-the-beach-5016-large.mp4"
        
        if videos:
            for vid in videos:
                src = vid.get('src')
                if src and ".mp4" in src:
                    video_url = src
                    break
                    
        print(f"✅ Video URL found")
        return video_url
        
    except Exception:
        return "https://assets.mixkit.co/videos/preview/mixkit-waves-coming-to-the-beach-5016-large.mp4"

def download_file(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

# --- 3. VIDEO EDITOR ---
def make_reel(topic):
    # File Paths
    video_path = "static/temp_video.mp4"
    audio_path = "static/temp_audio.mp3"
    final_path = "static/final_reel.mp4"

    # A. Get Content
    script = get_ai_script(topic)
    vid_url = get_video(topic) # Uses topic as keyword
    
    # B. Download Assets
    download_file(vid_url, video_path)
    asyncio.run(edge_tts.Communicate(script, "en-US-ChristopherNeural").save(audio_path))
    
    # C. Edit
    print("🎬 Stitching video...")
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Loop video to match audio
    video = video.loop(duration=audio.duration + 1)
    
    # Crop to Vertical (9:16)
    w, h = video.size
    target_ratio = 9/16
    if w/h > target_ratio:
        new_w = h * target_ratio
        video = video.crop(x1=w/2 - new_w/2, x2=w/2 + new_w/2, width=new_w, height=h)
        
    # Combine
    final = video.set_audio(audio)
    
    # Add Text (Wrapped in Try/Except to prevent crashes)
    try:
        txt = TextClip(script, fontsize=40, color='white', font='Arial-Bold', method='caption', size=(video.w-40, None))
        txt = txt.set_position(('center', 'bottom')).set_duration(final.duration)
        final = CompositeVideoClip([final, txt])
    except:
        print("⚠️ Skipping text overlay (ImageMagick issue)")

    final.write_videofile(final_path, codec='libx264', audio_codec='aac', fps=24)
    print("🎉 Reel Created!")
    return script