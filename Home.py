import streamlit as st
import subprocess
from pytube import YouTube
from urllib.parse import urlparse
from urllib.parse import parse_qs
from slience_cutter import * 

def download_video(url):
    # 'https://www.youtube.com/watch?v=EJ6qapvqqpI'
    parsed_url = urlparse(url)
    vid_id = parse_qs(parsed_url.query)['v'][0]
    command = ['yt-dlp', url, '-o', f'./videos/%(id)s', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best']
    # st.write_stream(subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    st.write(process.stdout.read())
    return vid_id

form = st.form(key='youtube-url')

with form:
    url = st.text_input(label='ENTER YOUTUBE URL:')
    st.form_submit_button('SUBMIT')

vid_id = download_video(url)

st.video(f'./videos/{vid_id}.mp4')