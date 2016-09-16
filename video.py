# coding:utf-8
"""
date: 2016/3/01
desc:  每次能在前进的方向上移动20个像素的都是同一辆车
"""
import cv2
from copy import copy
from math import pow, sqrt
from datetime import datetime as dt
import numpy as np
from settings import *

video_fpath = f

MIN_AREA = 200       # 最小面积
MAX_AREA = 10000    # 最大面积
MIN_W = 18          # 最小宽度
MAX_W = 45         # 最大宽度肯定不能超过马路的宽
MIN_H = 20          # 最大长度
MAX_H = 250         # 最大的长度不能超过桥长的多少
LEFT_X = 240
RIGHT_X = 415

# 这是缩放后的大小
SMALL_W = 600
SMALL_H = 400
ignore_len = 20   # 上下20个像素时表示已经要退出视野了，应该remove相应的车辆

# 车道，小于下面这个值是为左，，大于为右
LEFT_VAL = 340
FONT_SIZE = 0.4
word_font = cv2.FONT_HERSHEY_SIMPLEX


class V(object):
    """
    表示一辆车的各种参数
    """
    def __init__(self):
        self.name = ''          # 车的编号，左边的用L-12, 右边的用R-30
        self.start_dt = None    # 出现的时间
        self.cen_point = ()     # 中心点 --- 变
        self.length = 0.0       # 车长
        self.lane = ''          # 左还是右车道, 默认是左车道向下，右车道向上
        self.speed = 0.0        # 车速  ---可能变
        self.w, self.h = 0.0, 0.0  # 车的尺寸



def is_exists_v(l, b):
    for a in l:
        # 必须是同车道
        if a.lane != b.lane:
            print u'不是同车道..'
            continue
        # 距离必须小于某一个阀值
        c = sqrt(pow(float(a.cen_point[0]-b.cen_point[0]), 2) + pow(float(a.cen_point[1]-b.cen_point[1]), 2))
        if c <= 4:
            # 直接返回相应的之前的车
            return a

def judge_same_v(v1, v2):
    """判断是不是同一辆车，因为当前是上下四车道，所有车都几乎延同一直接运行，所以只需要判断x坐标的差距就行了"""
    if v1.lane != v2.lane:
        return False
    # 两帧frame的相同车辆的 x坐标的距离应该很小
    if abs(v1.cen_point[0] - v2.cen_point[0]) > 5:
        return False

    return True

def judge_new_v(v):
    """判断一个车是不是新出现的车"""
    pass


class VideoCamera(object):

    def __init__(self):
        self.maxThresholdValue = 200
        self.cap = cv2.VideoCapture(video_fpath)
        # fgbg = cv2.createBackgroundSubtractorMOG()
        self.fgbg = cv2.BackgroundSubtractorMOG2()
        self.frame = None       # 保存每次取到的视频帧图像
        self.debug = True
        # self.v_list = []        # 用于保存所有在视野中的车的中同点的坐标
        # self.is_first = True    # 表示第一次
        self.v_left_list = []   # 左边车辆的列表
        self.v_right_list = []  # 右边的列表

        self.v_index = 0        # 表示当前左右车道出现的所有车的编号，依次往上增加

    def is_valid_size(self, x, y, w, h):
        """
        检查是不是合格的车辆位置
        """
        return MIN_W <= w <= MAX_W and MIN_H <= h <= MAX_H and LEFT_X <= x <= RIGHT_X


    def get_maybe_valid_plate_roi_by_contours(self, contours):
        """
        初步获取可能是车辆外形的roi，依据是找到的轮廓的尺寸大小
        """
        valid_list = []
        for i, cnt in enumerate(contours):
            # 面积必须在一个定义好的区间中
            area = cv2.contourArea(cnt)
            if MIN_AREA < area < MAX_AREA:
                # 画出最小的矩形++++
                # rect = cv2.minAreaRect(cnt)
                x, y, w, h = cv2.boundingRect(cnt)
                if self.is_valid_size(x, y, w, h):
                    # 保存起来并返回
                    valid_list.append([x, y, w, h, cnt])
        return valid_list


    def remove_v_timeout(self):
        for v in self.v_left_list:
            if (dt.now() - v.start_dt).total_seconds() > 6:
                self.v_left_list.remove(v)

        for v in self.v_right_list:
            if (dt.now() - v.start_dt).total_seconds() > 6:
                self.v_right_list.remove(v)


    def process_frame(self, fgmask):
        """

        """
        print u'当前桥上的总车辆:', len(self.v_left_list) + len(self.v_right_list)
        # 1.先将灰边去掉
        ret, thresh1 = cv2.threshold(fgmask, self.maxThresholdValue, 255, cv2.THRESH_BINARY)

        # 2.再将一些多余的小白点去掉
        # 闭操作 先膨胀后腐蚀的
        kernel = np.ones((3, 3), np.uint8)
        closing = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)

        # 3.找出一些轮廓
        contours, hierarchy = cv2.findContours(closing, cv2.cv.CV_RETR_EXTERNAL, cv2.cv.CV_CHAIN_APPROX_NONE)
        valid_list = self.get_maybe_valid_plate_roi_by_contours(contours)

        # 先将超时的车去掉，根据时间， 这种方式不准确
        # self.remove_v_timeout()

        img = copy(self.frame)
        v_tmp_list = []  # 存放本次临时的正确的车的位置点

        for x, y, w, h, cnt in valid_list:
            # 在当前的帧上面画上相应的框子
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 1)

            # 计算出中心点
            M = cv2.moments(cnt)
            centroid_x = int(M['m10']/M['m00'])
            centroid_y = int(M['m01']/M['m00'])

            v = V()
            v.w, v.h = w, h
            v.cen_point = (centroid_x, centroid_y)
            v.lane = 'L' if centroid_x <= LEFT_VAL else 'R'
            v_list = self.v_left_list if v.lane == 'L' else self.v_right_list

            # 第一次的话，直接加入列表
            if self.v_index == 0:
                v.start_dt = dt.now()
                self.v_index += 1
                v.name = v.lane + ':' + str(self.v_index)
                v_list.append(v)
            else:
                # 不是空的情况，需要在之前的列表中找出是不是已经存在本车
                res = is_exists_v(v_list, v)
                if res and isinstance(res, V):
                    # 表示已经存在，那就先更新它的位置
                    res.cen_point = (centroid_x, centroid_y)
                    v_tmp_list.append(copy(res))
                    # 左车道是往下开
                    if v.lane == 'L':
                        if y + v.h >= SMALL_H - 5:
                            v_list.remove(res)
                            pass
                    else:
                        if y <= 5:
                            v_list.remove(res)
                else:
                    # 不存在，那有可能是新车，需要加到相应车道的列表中
                    # 新车在左右两边的入口位置是不同的
                    if v.lane == 'L' and y <= 5:
                        self.v_index += 1
                        v.start_dt = dt.now()
                        v.name = v.lane + ':' + str(self.v_index)
                        v_list.append(v)
                    elif v.lane == 'R' and v.h + y >= SMALL_H - 5:
                        self.v_index += 1
                        v.start_dt = dt.now()
                        v.name = v.lane + ':' + str(self.v_index)
                        v_list.append(v)

        # 过滤出本次要画的所有车后
        # 这里用粉色画出物体的中心
        for v in v_tmp_list:
            cv2.circle(img, (v.cen_point[0], v.cen_point[1]), 4, (255,0,255), -1)
            cv2.putText(img, u'%s (%d, %d)' % (v.name, v.cen_point[0], v.cen_point[1]), (v.cen_point[0], v.cen_point[1]), word_font, FONT_SIZE, (0,0,255), 1, cv2.CV_AA)

        # self.v_list = v_tmp_list
        # self.is_first = False

        # cv2.imshow('imggg', img)
        return closing, img

    def __del__(self):
        try:
            self.cap.release()
            cv2.destroyAllWindows()
        except:
            pass

    def start(self):
        while True:
            ret, frame = self.cap.read()
            self.frame = cv2.resize(frame, (SMALL_W, SMALL_H))  # frame.array

            # 这是个黑白的图片
            fgmask = self.fgbg.apply(self.frame)

            cv2.imshow('fgmask', fgmask)

            res, drawed_img = self.process_frame(fgmask)

            cv2.imshow('drawed_img', drawed_img)
            # cv2.imshow('res', res)

            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        """
        这里输出视频到网页中
        """
        '''
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
        '''
        ret, frame = self.cap.read()
        self.frame = cv2.resize(frame, (SMALL_W, SMALL_H))  # frame.array

        # 这是个黑白的图片
        fgmask = self.fgbg.apply(self.frame)
        res, drawed_img = self.process_frame(fgmask)
        # cv2.imshow('src', drawed_img)
        ret, jpeg = cv2.imencode('.jpg', drawed_img)
        # windows
        # return jpeg.tobytes()
        # ubuntu
        return jpeg.tostring()


if __name__ == '__main__':
    watch = VideoCamera()
    watch.start()


