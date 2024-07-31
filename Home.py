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
    progess = st.text('Downloading...')
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    progess.text(str(process.stdout.read()))
    return vid_id

def remove_silence(vid_id):
    command = ['unsilence', f'./videos/{vid_id}.mp4', f'./videos/{vid_id}_cut_silence.mp4']
    # st.write_stream(subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    progess = st.text('Removing silence...')
    subprocess.call(command, stdout=subprocess.PIPE)
    # progess.text(str(process.stdout.read()))

form = st.form(key='youtube-url')

with form:
    url = st.text_input(label='ENTER YOUTUBE URL:')
    st.form_submit_button('SUBMIT')

vid_id = download_video(url)

st.video(f'./videos/{vid_id}.mp4')

remove_silence(vid_id)

st.video(f'./videos/{vid_id}_cut_silence.mp4')