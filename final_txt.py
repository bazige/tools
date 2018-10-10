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

cls = {'0': 0,
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
    
    if w <= 0 or h <= 0:
        return 0
    sa = (int(b1[2]) - int(b1[0])) * (int(b1[3]) - int(b1[1]))
    sb = (int(b2[2]) - int(b2[0])) * (int(b2[3]) - int(b2[1]))
    
    cross = w * h
    return cross * 1.0/(sa + sb - cross)
    
ratio = [0.6, 0.8, 1]
net_w = 256
net_h = 256
for root, subdir, files in os.walk(new_path):
    if files != []:
        count = 0
        for doc in files:
            if doc.endswith('.txt'):
                print root
                print doc
                #------------------------------------------------------------------------------#
                # 1. find picture according to matched txt, and make a folder
                #------------------------------------------------------------------------------#
                #pdb.set_trace()
                file_path = os.path.join(root, doc)
                f = open(file_path, 'r')
                img = cv2.imread(file_path[:-4] + '.jpg')
                if img is None:
                    continue
                re_width = img.shape[1]
                re_height = img.shape[0]
                img_resize = cv2.resize(img, (re_width, re_height))
                new_dir = '/home/public/133public/face_person/RegionData/struct_data_roi/pad_256' + root[24:]
                if not os.path.isdir(new_dir):
                    os.makedirs(new_dir)
                    
                #-------------------------------------------------------------------------------#
                # 2. read typeId and label of txt, and reshape the format to up-left and right
                #    -down point and then shuff them
                #-------------------------------------------------------------------------------#
                obj_list = []
                for line in f:
                    content = line.strip('\n').split(' ')
                    cls_name = cls[content[0]]
                    x_1 = int((float(content[1]) - float(content[3]) / 2) * re_width)
                    y_1 = int((float(content[2]) - float(content[4]) / 2) * re_height)
                    x_2 = x_1 + int(float(content[3]) * re_width))
                    y_2 = y_1 + int(float(content[4]) * re_height))
                    if x_1 < 0:
                        x_1 = 0
                    if y_1 < 0:
                        y_1 = 0
                    if x_2 >= re_width:
                        x_2 = re_width - 1
                    if y_2 >= re_height:
                        y_2 = re_height - 1
                    obj_list.append([cls_name, x_1, y_1, x_2, y_2])
                    
                obj_count = len(obj_list)
                random.shuffle(obj_list)
                
                #---------------------------------------------------------------------------------#
                # 3. The center offset of x,y is about 5~20%, and padding value refer to w and h 
                #    is about 80%~160%
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
                    # ignoring the object that typeID is 5
                    if class_name >= 5:
                        continue 
                    if w < 10 or h < 10:
                        continue
                        
                    center_x = (x_1 + x_2)/2
                    center_y = (y_1 + y_2)/2
                    
                    roffx = int((float(random.randint(5, 20)) / 100) * w)
                    roffy = int((float(random.randint(5, 20)) / 100) * h)
                    
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
                    # boundary protection 
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
                        
                    # caculating label's up-left and right-down point after shift
                    # and get padding image
                    new_x_1 = center_x - pad/2
                    new_y_1 = center_y - pad/2
                    
                    new_x_2 = new_x_1 + pad
                    new_y_2 = new_y_1 + pad
                    if pad < 64:
                        continue
                    if new_x_1 < 0:# moving left if beyond right boundary
                        new_x_2 = new_x_2 - new_x_1
                        new_x_1 = 0
                    if new_y_1 < 0:# moving down if beyond top
                        new_y_2 = new_y_2 - new_y_1
                        new_y_1 = 0
                    if new_x_2 >= re_width:# moving right if beyond left boundary
                        new_x_1 = new_x_1 - (new_x_2 - re_width + 1)
                        new_x_2 = re_width - 1
                    if new_y_2 >= re_height:# moving up if beyond bottom
                        new_y_1 = new_y_1 - (new_y_2 - re_height + 1)
                        new_y_2 = re_height - 1
                    if new_x_1 < 0:
                        new_x_2 = new_x_2 - new_x_1
                        new_x_1 = 0
                    if new_y_1 < 0:
                        new_y_2 = new_y_2 - new_y_1
                        new_y_1 = 0
                    print new_x_1, new_x_2, new_y_1, new_y_2
                    # crop ROI zone
                    sub_img = img[new_y_1:new_y_2, new_x_1:new_x_2]
                    sub_img = cv2.resize(sub_img, (net_w, net_h))
                    
                    #cv2.imshow("a", sub_img)
                    #cv2.waitKey()
                    #cv2.rectangle(img_resize, (new_x_1, new_y_1), (new_x_2, new_y_2), (255, 0, 0), 1)
                    new_jpg_name = subdir + '/' + str(count) + '.jpg'
                    cv2.imwrite(new_jpg_name, sub_img)
                    new_txt_name = subdir + '/' + str(count) + '.txt'
                                
                    #---------------------------------------------------------------------------------#
                    # 4. reconvert label information to new position that refer to new image
                    #---------------------------------------------------------------------------------#
                    with open(new_txt_name, 'w') as f:
                        o_x_1_1 = x_1
                        o_y_1_1 = y_1
                        o_x_2_1 = x_2        
                        o_y_2_1 = y_2 
                        if x_1 < new_x_1:
                            o_x_1_1 = new_x_1
                        if y_1 < new_y_1:
                            o_y_1_1 = new_y_1
                        if x_2 > new_x_2:
                            o_x_2_1 = new_x_2
                        if y_2 > new_y_2:
                            o_y_2_1 = new_y_2
                        o_w = o_x_2_1 - o_x_1_1
                        o_h = o_y_2_1 - o_y_1_1   
                                
                        # get padding label position that refer to new ROI
                        obj_x = (o_x_1_1 + o_w/2 - new_x_1) * 1.0 / (new_x_2 - new_x_1)
                        obj_y = (o_y_1_1 + o_h/2 - new_y_1) * 1.0 / (new_y_2 - new_y_1)       
                        obj_w = o_w * 1.0 / (new_x_2 - new_x_1)
                        obj_h = o_h * 1.0 / (new_y_2 - new_y_1)
                        obj_cls = class_name 
                        f.write(str(obj_cls) + ' ' + str(obj_x) + ' ' + str(obj_y) + ' ' + str(obj_w) + ' ' + str(obj_h) + '\n')
                                
                        #---------------------------------------------------------------------------------#
                        # 5. if this box overlaps with other boxes, caculating IOU, and then throw away the box with low
                        #    value of IOU       
                        #---------------------------------------------------------------------------------#
                        # pdb.set_trace()
                        for other_obj in obj_list:
                            o_c = other_obj[0]
                            o_x_1 = other_obj[1]
                            o_y_1 = other_obj[2]
                            o_x_2 = other_obj[3]
                            o_y_2 = other_obj[4]
                                
                            if o_x_1 == x_1 and o_y_1 == y_1 and o_x_2 == x_2 and o_y_2 == y_2:
                                continue
                            cx = (o_x_1 + o_x_2) / 2
                            cy = (o_y_1 + o_y_2) / 2
                            # print o_x_1, o_y_1, o_x_2, o_y_2
                            t_iou = iou([new_x_1, new_y_1, new_x_2, new_y_2], [o_x_1, o_y_1, o_x_2, o_y_2])
                            if t_iou > 0:
                                o_x_1_1 = o_x_1
                                o_y_1_1 = o_y_1
                                o_x_2_1 = o_x_2
                                o_y_2_1 = o_y_2
                                if o_x_1 < new_x_1:
                                    o_x_1_1 = new_x_1
                                if o_y_1 < new_y_1:
                                    o_y_1_1 = new_y_1
                                if o_x_2 > new_x_2:
                                    o_x_2_1 = new_x_2
                                if o_y_2 > new_y_2:
                                    o_y_2_1 = new_y_2
                                o_w = o_x_2_1 - o_x_1_1
                                o_h = o_y_2_1 - o_y_1_1
                                # if one box overlaps with another or the box is cropped, the recaculating box
                                obj_x = (o_x_1_1 + o_w/2 - new_x_1) * 1.0 / (new_x_2 - new_x_1)
                                obj_y = (o_y_1_1 + o_h/2 - new_y_1) * 1.0 / (new_y_2 - new_y_1)
                                obj_w = o_w * 1.0 /(new_x_2 - new_x_1)
                                obj_h = o_h * 1.0 /(new_y_2 - new_y_1)
                                obj_cls = o_c
                                scale_w = o_w * 1.0 /(new_x_2 - new_x_1)
                                scale_h = o_h * 1.0 /(new_y_2 - new_y_1)
                                if scale_h*scale_w < 0.0025 or scale_w < 0.05 or scale_h < 0.05:
                                    continue
                                if t_iou > 0.003 and cx >= new_x_1 and cx <= new_x_2 and cy >= new_y_1 and cy <= new_y_2:
                                    f.write(str(obj_cls) + ' ' + str(obj_x) + ' ' + str(obj_y) + ' ' + str(obj_w) + ' ' + str(obj_h) + '\n')
                                # if the object's is cropped, its type will be set 4
                                else: 
                                    f.write('4' + ' ' + str(obj_x) + ' ' + str(obj_y) + ' ' + str(obj_w) + ' ' + str(obj_h) + '\n')
                    count += 1
        #break                        
                                                     
                                
                                
                                
                                
                                
