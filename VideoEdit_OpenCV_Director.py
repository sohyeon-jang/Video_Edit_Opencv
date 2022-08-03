import os 
from pathlib import Path
import glob
import cv2
import xml.etree.ElementTree as ET



def time2sec(timeStr):
    
    time_HMS = timeStr.split(":")
    hour = int(time_HMS[0])
    min = int(time_HMS[1])
    sec = int(time_HMS[2])
    
    return hour*3600+min*60+sec



# xml, mp4파일이 있는 data_sample 주소
path = './data_sample'
result_folder = f'{path}/result'



file_list = os.listdir(path)

xml_path = glob.glob(f"{path}/*.xml", recursive=True)
mp4_path = glob.glob(f"{path}/*.mp4", recursive=True)



# result 폴더 만들기
if not os.path.isdir(result_folder):
    os.mkdir(result_folder)




for xml_file in xml_path :
    

    mp4_file = xml_file[:-4]+".mp4"

    mp4_file_name = Path(mp4_file).stem
    
    cap = cv2.VideoCapture(mp4_file)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    

    # 동영상 FPS값
    fps = float(cap.get(cv2.CAP_PROP_FPS))

    print(f'{mp4_file_name}의 ', 'Frame width:', width)
    print(f'{mp4_file_name}의 ', 'Frame height:', height)
    print(f'{mp4_file_name}의 ', 'Frame count:', count)

    print(f'{mp4_file_name}의 ', 'FPS:', fps)
    print(f'{mp4_file_name}의 ', 'codec:', fourcc)

    

    # XML 파일 시간 가져오기
    doc = ET.parse(xml_file)

    root = doc.getroot()

    # xml 파일 알람 이벤트 시작 진행 시간 가져오기
    for Alarm in root.findall("./Library/Clip/Alarms/Alarm"):
        start = Alarm.find('StartTime').text
        AlarmDuration = Alarm.find('AlarmDuration').text
        AlarmDescription = Alarm.find('AlarmDescription').text

    
    StartTime_sec = time2sec(start)
    AlarmDuration_sec = time2sec(AlarmDuration)
    
    Start_frame = StartTime_sec * fps
    End_frame = (StartTime_sec + AlarmDuration_sec) * fps

    # print("영상 시작 프레임 : ", Start_fps) -> 영상 시작 프레임 :  6150...
    # print("영상 끝나는 프레임 : ", End_fps) -> 영상 끝나는 프레임 :  6450...

    
    output_path = f"{result_folder}/{mp4_file_name}_edit.mp4"
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    

    
    frame_num = 0
    while(cap.isOpened()):
        ret, frame = cap.read()

        if (not ret) or (frame_num >= End_frame):
            break
        if frame_num >= Start_frame :
            out.write(frame)
        frame_num+=1
        

    out.release()
    cap.release()