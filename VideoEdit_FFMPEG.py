from email.mime import image
from unittest import result
import ffmpeg
# import sys
import glob
import os 
import xml.etree.ElementTree as ET
import subprocess
import shlex
import datetime

file_path = 'data/'
result_folder = 'result'


if not os.path.isdir(result_folder):
        os.mkdir(result_folder)


#디렉토리 내에 mp4파일과 xml 파일만 찾음
xmlname = glob.glob(f'{file_path}*xml')


# sys.path.append(r'C:\Users\DIP아카데미센터-KDigital06\Desktop\wkit\ffmpeg-5.1-full_build\bin') 
for xml_file in xmlname :
    #root노드 가져오기
    doc = ET.parse(xml_file)
    root = doc.getroot()
    #xml 파일안에 Alarm 태그만 검색
    for Alarm in root.findall("./Library/Clip/Alarms/Alarm"):
        start = Alarm.find('StartTime').text
        AlarmDuration = Alarm.find('AlarmDuration').text
        AlarmDescription = Alarm.find('AlarmDescription').text
        Start_Frame = 0
        End_Frame = 0
        print(start,"에서부터 ",AlarmDuration,"동안", AlarmDescription)
    #input 파일 이름 검색  
    s = os.path.join(file_path,root.find("./Library/Clip/Header/Filename").text)
    s = xml_file[:-4]+'.mp4'
    #파일이 없는경우 에러 메시지 출력
    if not os.path.isfile(s):
        print('not_found_file : %s'%(s))
        continue
    
    #output 파일 설정
    #./data/result output + basename(s)
    d = os.path.join(result_folder,"output"+os.path.basename(s))
    test_d = result_folder + "/output" + os.path.basename(s)



    #s == input location
    stream = ffmpeg.input(s) # video location
    stream = stream.trim(start = start, duration=AlarmDuration).filter('setpts', 'PTS-STARTPTS')
    stream = ffmpeg.output(stream, d)
    #d == ./data/result/output/xmlfile.mp4
    #result_folder = f'{file_path}result'
    #ffmpeg 실행
    ffmpeg.run(stream)

    #초당 프레임으로 자른 이미지를 저장할 폴더생성
    imagefolder = f"{d[:-4]}"
    if not os.path.isdir(imagefolder):
        os.mkdir(imagefolder)
    
    #초당프레임 구하는 코드 
    #잘라낸 영상의 총프레임을 영상 길이로 나눔
    #영상길이 = length_v = Total_time초
    length_v = subprocess.check_output(f"ffmpeg -i {d} 2>&1 | grep Duration | cut -d ' ' -f 4 | sed s/,//"
    , shell=True, text=True)
    time_video = length_v.split(':')
    Hour_Alarm = int(time_video[0])
    Min_Alarm = int(time_video[1])
    Second_Alarm = float(time_video[2])
    Total_time = Hour_Alarm*60*60 + Min_Alarm*60 + Second_Alarm

    #총 프레임 구하는 코드 
    Frame_v = subprocess.check_output(f"ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {d}", shell=True, text=True)
    #초당 프레임 Fps
    Fps = float(Frame_v)/Total_time



    # 추출된 영상에서 1프레임당 한장씩 자르도록
    command = f"ffmpeg -ss 00:00:0 -i {test_d} -r {Fps} -f image2 {imagefolder}/-%d.jpg"
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    for line in process.stdout:
        now = datetime.datetime.now()
        print(now, line)    