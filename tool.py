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
    parser_create_list.add_argument('img_path', help='训练图片存放路径（标签与图片同文件夹）', type=str)
    parser_create_list.add_argument('dest_path',help='list生成路径（包括文件名）', type=str)
    parser_create_list.set_defaults(func=create_list)
    
    parser_show = sub_parser.add_parser('show')
    parser_show.add_argument('img_path', help='显示图片存放路径（标签与图片同文件夹）', type=str)
    parser_show.set_defaults(func=show_image_label)
  
    parser_json = sub_parser.add_parser('json')
    parser_json.add_argument('img_path', help='显示json存放路径', type=str)
    parser_json.set_defaults(func=parse_json)
                                            
    args = parent_parser.parse_args()
    if args.func.__name__ == 'create_list':
       args.func(args.img_path, args.dest_path)
    elif args.func.__name__ == 'show_image_label':
       args.func(args.img_path)
    elif args.func.__name__ == 'parse_json':
       args.func(args.img_path)  
                                            
#生成测试txt
if 0:
   data_path = '/home/public/test_2/'
   with open('test_aa.txt', 'w') as f:
       for i in os.listdir(data_path):
           f.write(data_path + i + '\n')
                                            
#删除样本中目标数过多的样本及对应label
if 1:
    data_path = '/home/public/face_person/region_data'
    for root, subdir, files in os.walk(data_path):
       if file != []:
           for doc in files:
               if doc[-3:] == 'txt':
                   count = 0
                   ff = open(root, + '/' + doc, 'r')
                   for line in ff:
                       content = line.strip('\n').split(' ')
                       if content[0] int ['0', '1', '2']:
                            count += 1
                       if count > 5:
                           print doc
                           os.remove(root + '/' + doc)
                           os.remove(root + '/' + doc[:-3] + 'jpg')
                                            
#删除生成样本中目标过小的情况
if 0:
    data_path = '/home/public/new_re/obj/'
    count = 0
    for root, subdir, files in os.walk(data_path):
       if file != []:
           for doc in files:
               if doc[-3:] == 'jpg':
                   img_path = os.path.join(root, doc)
                   img = cv2.imread(img_path)
                   width = img.shape[1]
                   height = img.shape[0]
                   if height * width < 30*30:
                       count += 1
                       print img_path
                       os.remove(root + '/' + doc)
                       os.remove(root + '/' + doc[:-3] + 'txt')
    print count
