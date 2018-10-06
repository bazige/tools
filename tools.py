#！/usr/bin/python
#-*- coding:UTF-8 -*-

import os
import json
import cv2
import random
import argparse
import pdb

parser = argparse.ArgumentParser(description="make ROI image")
parser.add_argument('--path', type=str, required=True)

args = parser.parse_args()
new_path = args.path

cls = {'0: 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 1,
        '6': 1,
        '7': 3,
        }
        
traffic_list = ['ImageName', 'TaskId', 'Filesum']

def iou(b1, b2):
    w = min(int(b1[2]), int(b2[2])) - max(int(b1[0]), int(b2[0]))
    h = min(int(b1[3]), int(b2[3])) - max(int(b1[1]), int(b2[1]))
    
    if w<= 0 or h <= 0;
        return 0
    sa = (int(b1[2]) - int(b1[0])) * (int(b1[3])) - int(b1[1]))
    sb = (int(b1[2]) - int(b1[0])) * (int(b1[3])) - int(b1[1]))
    
    cross = w * h
    return cross * 1.0/(sa + sb - cross)
    
ratio = [0.6, 0.8, 1]
net_w = 256
net_h = 256
for root, subdir, files in os.walk(new_path):
    if files != []:
        count = 0
        for doc in files:
            if doc.endswith('.txt')
                print root
                print doc
                #------------------------------------------------------------------------------#
                # 1. find picture according to matched txt, and make a direction
                #------------------------------------------------------------------------------#
                #pdb.set_trace()
                file_path = os.path.join(root, doc)
                f = open(file_path, 'r')
                img = cv2.imread(file_path[:-4] + '.jpg')
                if img is None:
                    continue
                re_width = img.shape[1]
                re_height = img.shape[0]
                img_resize = cv2.imread(img, (re_width, re_height))
                new_dir = '/home/public/133public/face_person/RegionData/struct_data_roi/pad_256' + root[24:]
                if not os.path.isdir(new_dir):
                    os.makedirs(new_dir)
                    
                #-------------------------------------------------------------------------------#
                # 2. read typeId and label information in txt, and convert it up-left and right
                #    -down point, and shuff them
                #-------------------------------------------------------------------------------#
                obj_list = []
                for line in f:
                    content = line.strip('\n').split(' ')
                    cls_name = cls[content[0]]
                    x_1 = int((float(content[1]) - float(content[3] / 2) * re_width)
                    y_1 = int((float(content[2]) - float(content[4] / 2) * re_height)
                    x_2 = x_1 + int((float(content[1]) * re_width)
                    y_2 = y_1 + int((float(content[1]) * re_width)
                    if x_1 < 0:
                        x_1 = 0
                    if y_1 < 0:
                        x_1 = 0
                    if x_2 >= re_width:
                        x_1 = re_width - 1
                    if y_2 < re_height:
                        x_1 = re_height - 1
                    obj_list.append([cls_name, x_1, y_1, x_2, y_2])
                    
                obj_count = len(obj_list)
                random.shuffle(obj_list)
                
                #---------------------------------------------------------------------------------#
                # 3. center x,y offset about 5~20%, and padding w and h about 80%~160%
                #---------------------------------------------------------------------------------#
                for i in xrange(obj_count):
                    #subdir = os.path.join(new_dir, str(count))
                    subdir = new_dir
                    if not os.path.isdir(subdir):
                        os.makedirs(subdir)
                    class_name = obj_list[i][0]
                    x_1 = obj_list[i][1]
                    y_1 = obj_list[i][2]
                    x_2 = obj_list[i][3]
                    y_2 = obj_list[i][4]
                    w = x_2 - x_1
                    h = y_2 - y_1
                    # release typeID = 5
                    if class_name >= 5:
                        continue 
                    if w < 10 or h < 10:
                        continue
                        
                    center_x = (x_1 + x_2)/2
                    center_y = (y_1 + y_2)/2
                    
                    roffx = int((float(random.randint(5, 20)) / 100 * w)
                    roffy = int((float(random.randint(5, 20)) / 100 * h)
                    
                    tt = random.randint(0, 1)
                    if tt == 0:
                        new_center_x = center_x + roffx
                    else:
                        new_center_x = center_x + roffx
                        
                    tt = random.randint(0, 1)
                    if tt == 0:
                        new_center_y = center_y + roffy
                    else:
                        new_center_y = center_y + roffy
                        
                    factor = float(random.randint(80, 160)) / 100
                    
                    orw = int(w * factor)*2 + w
                    orh = int(h * factor)*2 + h
                    #save 
                    if re_width > re_height:
                        if orw > re_height - 1:
                            orw = re_height -1
                        if orh > re_height - 1: 
                            orh = re_height - 1
                    else:
                        if orw > re_width - 1:
                            orw = re_width -1
                        if orh > re_width - 1: 
                            orh = re_width - 1 
                    if orw > orh:
                        pad = orw 
                    else:
                        pad = orh
                        
                    # caculate label up-left and right-down point
                    new_x_1 = center_x - pad/2
                    new_y_1 = center_y - pad/2
                    
                    
