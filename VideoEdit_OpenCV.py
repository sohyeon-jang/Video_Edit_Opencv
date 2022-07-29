import os 
import os.path
from pathlib import Path
import glob
import cv2
import ffmpeg
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, dump, ElementTree



# data_sample 주소 입력
path = 'C:/Users/DIP아카데미센터-KDigital02/Desktop/OpenCV/data_sample'



file_list = os.listdir(path)
# file_list -> ['C045100_001.mp4', 'C045100_001.xml', 'C045300_010.mp4', 'C045300_010.xml', 'C055200_006.mp4', 'C055200_006.xml']

xml_path = glob.glob(f"{path}/*.xml", recursive=True)
mp4_path = glob.glob(f"{path}/*.mp4", recursive=True)



# result 폴더 만들기
result_folder = f'{path}/result'

if not os.path.isdir(result_folder):
    os.mkdir(result_folder)


i = 0

while i < (len(xml_path)):
    
    # xml_path[0] -> C:/Users/~~/data_sample\C045100_001.xml
    # mp4_path[0] -> C:/Users/~~/data_sample\C045100_001.mp4

    xml_file = xml_path[i]
    mp4_file = mp4_path[i]

    mp4_file_name = Path(mp4_path[i]).stem
    
    cap = cv2.VideoCapture(mp4_file)

    width = float(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = float(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    count = float(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 동영상 FPS값
    fps = float(cap.get(cv2.CAP_PROP_FPS))

    print(f'{mp4_file_name}의 ', 'Frame width:', width)
    print(f'{mp4_file_name}의 ','Frame height:', height)
    print(f'{mp4_file_name}의 ','Frame count:', count)

    print(f'{mp4_file_name}의 ','FPS:', fps)



    # XML 파일 시간 가져오기
    doc = ET.parse(xml_file)

    root = doc.getroot()

    # xml 파일 알람 이벤트 시작 진행 시간 가져오기
    for Alarm in root.findall("./Library/Clip/Alarms/Alarm"):
        start = Alarm.find('StartTime').text
        AlarmDuration = Alarm.find('AlarmDuration').text
        AlarmDescription = Alarm.find('AlarmDescription').text

    StartHour = int(start[3:5])
    StartMin = int(start[6:8])
    AlarmDuration_int = int(AlarmDuration[4:6])
    StartTime_time = (StartHour * 60) + StartMin

    Start_fps = StartTime_time * fps
    End_fps = (StartTime_time + AlarmDuration_int) * fps

    # print("영상 시작 프레임 : ", Start_fps) -> 영상 시작 프레임 :  6150...
    # print("영상 끝나는 프레임 : ", End_fps) -> 영상 끝나는 프레임 :  6450...


    # FFMPEG 설치할 것

    # sys.path.append(r'C:\Program Files\ffmpeg-4.3\bin')h

    stream = ffmpeg.input(mp4_file) # Video location

    # 영상 자르기
    stream = stream.trim(start_frame = Start_fps, end_frame = End_fps).filter('setpts', 'PTS-STARTPTS')
    stream = stream.filter('fps', fps, round='up').filter('scale', width, height)

    stream = ffmpeg.output(stream, f"{result_folder}/{mp4_file_name}_edit.mp4")

    ffmpeg.run(stream)


    i += 1