#!/usr/bin/env python
#-*- coding: utf-8 -*-

from sys import argv, exit, stderr, stdout
from os import mkdir
import cv2, json

def print_s(msg, std='out'):
    place = stdout if std == 'out' else stderr
    place.write('{}\n'.format(msg))
    place.flush()


def open_image(img_name):
    try:
        img = cv2.imread(img_name)
        print_s('File: {}'.format(img_name), 'err')
        return img
    except:
        print_s('Cannot open "{}"'.format(img_name), 'err')
        return None
    

def crop_images(img_name, objects, trg_dir, data_dir, train_fn, test_fn):
    if objects == []: return None

    trg_name = img_name.replace('/','_')
    trg_name = '.'.join(trg_name.split('.')[:-1])
    trg_ext  = img_name.split('.')[-1]
    
    img = open_image('{}/{}'.format(data_dir, img_name))
    if img is None:
        return False
    else:
        print_s('File: {}'.format(img_name), 'err')
    out = test_fn if img_name.find('test/') != -1 else train_fn

    count = 0
    for i in objects:
        xmin = xmax = ymin = ymax = 0
        try:
            catg = i['category']
            xmin = int(i['bbox']['xmin']-0.5)
            xmax = int(i['bbox']['xmax']+0.5)
            ymin = int(i['bbox']['ymin']-0.5)
            ymax = int(i['bbox']['ymax']+0.5)
            cropImg = img[ymin:ymax, xmin:xmax]
            target_name = '{}/{}-{}-{}.{}'.format(
                           trg_dir, catg, trg_name, count, trg_ext)
            cv2.imwrite(target_name, cropImg)
            print_s('{} {} ({}:{}, {}:{})'.format(
                     target_name, catg, xmin, xmax, ymin, ymax))
            out.write('{} {}\n'.format(target_name, catg))
            count += 1
        except:
            continue
    
    return True


def check_args():
    if len(argv) != 3:
        print_s("Use: {} filename.json target_path".format(argv[0]), 'err')
        exit(1)
    
    return argv[1], argv[2]


def check_trg_path(p):
    try:
        mkdir(trg_dir, 0770)
    except:
        print_s('Remove "{}" to continue.'.format(trg_dir), 'err')
        exit(2)

if __name__ == '__main__':
    json_fn, trg_dir = check_args()
    train_fn = open('images_train.txt', 'w')
    test_fn  = open('images_test.txt' , 'w')

    data     = json.loads(open(json_fn).read())['imgs']
    data_dir = '/'.join(json_fn.split('/')[:-1])
    
    check_trg_path(trg_dir)

    for i in data:
        img = data[i]['path']
        crop_images(img, data[i]['objects'], trg_dir, data_dir, train_fn, test_fn)
    train_fn.close()
    test_fn.close()
