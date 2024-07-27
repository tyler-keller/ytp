import subprocess
import tempfile
import sys
import os

def find_silences(filename, dB = -35):
  """
    returns a list:
      even elements (0,2,4, ...) denote silence start time
      uneven elements (1,3,5, ...) denote silence end time
  """
  command = ["ffmpeg", "-i", filename, "-af", "silencedetect=n=" + str (dB) + "dB:d=1", "-f", "null", "-"]
  output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  s = str(output)
  lines = s.split("\\n")
  time_list = []

  for line in lines:
    if ("silencedetect" in line):
        words = line.split(" ")
        for i in range (len(words)):
            if ("silence_start" in words[i]):
              time_list.append (float(words[i+1]))
            if "silence_end" in words[i]:
              time_list.append (float (words[i+1]))
  silence_section_list = list (zip(*[iter(time_list)]*2))

  #return silence_section_list
  return time_list

def get_video_duration(filename:str) -> float:
  command = ["ffprobe","-i",filename,"-v","quiet","-show_entries","format=duration","-hide_banner","-of","default=noprint_wrappers=1:nokey=1"]
  output = subprocess.run (command, stdout=subprocess.PIPE)
  s = str(output.stdout, "UTF-8")
  return float (s)

def get_sections_of_new_video (silences, duration):
  """Returns timings for parts, where the video should be kept"""
  return [0.0] + silences + [duration]

def ffmpeg_filter_getSegmentFilter(videoSectionTimings):
  ret = ""
  for i in range (int (len(videoSectionTimings)/2)):
    start = videoSectionTimings[2*i]
    end   = videoSectionTimings[2*i+1]
    ret += "between(t," + str(start) + "," + str(end) + ")+"
  # cut away last "+"
  ret = ret[:-1]
  return ret

def get_file_content_video_filter(videoSectionTimings):
  ret = "select='"
  ret += ffmpeg_filter_getSegmentFilter (videoSectionTimings)
  ret += "', setpts=N/FRAME_RATE/TB"
  return ret

def get_file_content_audio_filter(videoSectionTimings):
  ret = "aselect='"
  ret += ffmpeg_filter_getSegmentFilter (videoSectionTimings)
  ret += "', asetpts=N/SR/TB"
  return ret

def write_file (filename, content):
  with open (filename, "w") as file:
    file.write (str(content))

def ffmpeg_run(file, videoFilter, audioFilter, outfile):
  # prepare filter files
  vFile = tempfile.NamedTemporaryFile (mode="w", encoding="UTF-8", prefix="silence_video")
  aFile = tempfile.NamedTemporaryFile (mode="w", encoding="UTF-8", prefix="silence_audio")
  videoFilter_file = vFile.name #"/tmp/videoFilter" # TODO: replace with tempfile
  audioFilter_file = aFile.name #"/tmp/audioFilter" # TODO: replace with tempfile
  write_file(videoFilter_file, videoFilter)
  write_file(audioFilter_file, audioFilter)
  command = ["ffmpeg","-i",file,
              "-filter_script:v",videoFilter_file,
              "-filter_script:a",audioFilter_file,
              outfile]
  subprocess.run (command)
  vFile.close()
  aFile.close()


def cut_silences(infile, outfile, dB = -35):
  silences = find_silences(infile,dB)
  duration = get_video_duration(infile)
  videoSegments = get_sections_of_new_video(silences, duration)
  videoFilter = get_file_content_video_filter(videoSegments)
  audioFilter = get_file_content_audio_filter(videoSegments)
  ffmpeg_run(infile, videoFilter, audioFilter, outfile)