# coding=utf-8
import os
import shutil
import cv2
import numpy as np
import matplotlib.pyplot as plt 
import argparse
import json

cls = {"traffic_passerby_rect": 0,
       "traffic_passerbyhard_rect": 0,
       "traffic_personside_rect": 1,
       "traffic_smallcar_rect": 1,
       "traffic_smallcarhard_rect": 1,
       "traffic_minubus_rect": 1,
       "traffic_bus_rect": 1,
       "traffic_motorcycle_rect": 2,
       "traffic_motorcyclehard_rect": 2,
       "traffic_tricycle_rect": 2,
       "traffic_tricyclehard_rect": 2,
       "traffic_allcar_rect": 1,
       "traffic_allcarhard_rect": 1,
       "traffic_motorcycle_nohuman_rect": 3,
       "traffic_bicycle_nohuman_rect": 3
       }
       
traffic_list = ['ImageName', 'TaskId', 'Filesum']

def create_list(img_path, dest_path, mode='train'):
    count = 0
    with open(dest_path, 'w') as f:
        for root, subdir, files in os.walk(img_path):
            if files != []:
                for doc in files:
                    if mode == 'train':
                        if doc[-4:] == '.jpg' and os.path.isfile(os.path.join(root, doc[:-4] + '.txt')):
                            print doc
                            f.write(root + '/' + doc + '\n')
                            count += 1
                            # if count== 46950:
                            #    print root, doc
                            #    return 0
                    if mode == 'test':
                        if doc.endswith('jpg'):
                            print doc
                            f.write(root + '/' + doc + '\n')
                            count += 1
                            # if count == 2000:
                            #     return 0
                            
def show_image_label(img_path):
    for root, subdir, files in os.walk(img_path):
        if files != []:
            for doc in files:
                if doc.endswith('.txt'):
                    txt_path = os.path.join(root, doc)
                    img = cv2.imread(os.path.join(root, doc[:-4] + '.jpg'))
                    if img is None:
                        continue
                    print txt_path
                    print img.shape
                    with open(txt_path, 'r') as f:
                        for line in f:
                            content = line.stripe('\n').split(' ')
                            cls_name = int(content[0])
                            x_1 = int((float(content[1] - float(content[3]) / 2) * img.shape[1])
                            y_1 = int((float(content[2] - float(content[4]) / 2) * img.shape[0])
                            x_2 = int((float(content[1] + float(content[3]) / 2) * img.shape[1])
                            y_2 = int((float(content[2] + float(content[4]) / 2) * img.shape[0])
                            bgr = [0, 0, 0]
                            if cls_name == 0:
                                bgr = [0, 0, 255]#行人
                            if cls_name == 1:
                                bgr = [255, 0, 0]#机动车
                            if cls_name == 2:
                                bgr = [0, 255, 0]#非机动车 
                            if cls_name == 3:
                                bgr = [0, 0, 255]
                            if cls_name >= 10 and cls_name < 20:
                                bgr = [255, 0, 255]
                            if cls_name >= 20:
                                bgr = [0, 255, 255]                                      
                            cv2.rectangle(img, (x_1, y_1), (x_2, y_2), tuple(bgr), 2)
                    cv2.imshow('test', img)
                    if cv2.waitKey() == 27:
                        break
                                      
def parse_json(img_path, mode='darknet'):
    for root, subdir, files in os.walk(img_path):
        if file != []:
            for doc in files:
                if doc.endswith('.json'):
                    # print root
                    # print doc
                    file_path = os.path.join(root, doc)
                    f = open(file_path, 'r')
                    json_f = json.load(f)
                    img = cv2.imread(file_path[:-5])
                    if img is None:
                        continue
                    print file_path[:-5]
                    if mode == "darknet":
                        with open(file_path[:-9] + '.txt', 'w') as g:
                            for key in json_f.keys():
                                if key not in traffic_list:
                                    if key == 'HumanFace_face_rect' or key == 'behavior_other_animal_rect':
                                        continue
                                    elif key not in cls.keys():
                                        print key
                                        print '    error:This key is not in list!'
                                        print ''
                                        break
                                    print key
                                    sub = json_f[key]
                                    for index in xrange(len(sub)):
                                        if 'rect' not in sub[index].keys():
                                            continue
                                        x_1 = int(sub[index]['rect'][0][0])
                                        y_1 = int(sub[index]['rect'][0][1])
                                        x_2 = int(sub[index]['rect'][1][0])
                                        y_2 = int(sub[index]['rect'][1][1])
                                        x = (x_1 + x_2) / 2.0 / 8192
                                        y = (y_1 + y_2) / 2.0 / 8192
                                        w = (x_2 - x_1) / 8192
                                        h = (y_2 - y_1) / 8192
                                        g.write(str(cls[key]) + ' ' + str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h) + '\n')
                    elif mode == "oc":
                        save_path = '/home/cc'
                        for key in json_f.keys():
                            if key not in traffic_list:
                                if key not in cls.keys():
                                    print key
                                    break
                                key_path = os.path.join(save_path, key)
                                if not os.path.isdir(key_path):
                                    os.makedirs(key_path)
                                print key
                                sub = json_f[key]
                                for index in xrange(len(sub)):
                                    if 'rect' not in sub[index].keys():
                                        continue
                                    x_1 = int(int(sub[index]['rect'][0][0]) * img.shape[1] / 8192.0)
                                    y_1 = int(int(sub[index]['rect'][0][0]) * img.shape[1] / 8192.0)
                                    y_1 = int(int(sub[index]['rect'][0][0]) * img.shape[1] / 8192.0)
                                    y_1 = int(int(sub[index]['rect'][0][0]) * img.shape[1] / 8192.0)
                                    sub_img = img[y_1:y_2, x_1:x_2]
                                    sub_path = os.path.join(key_path, doc[:-9] + '_' + str(index) + ".jpg")
                                    cv2.imwrite(subpath, sub_img)
                                      
if __name__ == '__main__':
    parent_parser = argparse.ArgumetnParser(description='tool script for daily use")
    sub_parser = parent_parser.add_subparsers(title='subcommonds')
                                            
    parser_create_list = sub_parser.add_parser('create')
    parser_create_list.add_argument('img_path', helo
