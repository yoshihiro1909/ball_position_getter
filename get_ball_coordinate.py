# -*- coding: utf-8 -*-

# Python 2.7.13
# OpenCV 2.4.9.1

import time

import cv2
import numpy as np
from numpy import linalg


def split_norm_and_degree(norm_list, degree_list):
    norm_and_degree_list = []
    try:
        for norm, degree in zip(norm_list, degree_list):
            norm_and_degree = []
            norm_and_degree.append(norm)
            norm_and_degree.append(degree)
            norm_and_degree_list.append(norm_and_degree)
    except:
        pass

    return norm_and_degree_list


def calculate_coordinate(img, camera_distance_x, camera_distance_y):
    height, width = img.shape[:2]
    width = int(width)
    height = int(height)
    width_half = int(width/2)+camera_distance_y
    height_half = int(height / 2) + camera_distance_x

    return height, width, width_half, height_half


def vector_to_norm_and_degree(u, v):
    i = np.inner(u, v)
    n = linalg.norm(u) * linalg.norm(v)
    c = i / n
    degree = np.rad2deg(np.arccos(np.clip(c, -1.0, 1.0)))
    if v[1] < 0:
        degree = 360 - degree

    return int(linalg.norm(v)), int(degree)


class GetBallCoordinate():
    def __init__(self, camera_distance_x, camera_distance_y):
        self.cap = None
        self.circles = None
        # 原点をどの程度ずらすか
        self.camera_distance_x = camera_distance_x
        self.camera_distance_y = camera_distance_y

    def start_camera(self, camera_number, wait):
        wait_count = 0
        while True:
            self.cap = cv2.VideoCapture(camera_number)
            wait_count += 1
            if wait_count >= wait:
                print("カメラを開くのに失敗した")
                break
            time.sleep(0.1)
            flag = self.cap.isOpened()
            if flag == True:
                print("カメラを開くのに成功した")
                break
            else:
                pass

    def open_img(self, path):
        img = cv2.imread(path)

        return img

    def get_img(self):
        _, img = self.cap.read()

        return img

    # カラー画像用
    # 画像を右回りに90度回転するとともに座標を再計算する
    def rotate_img(self, rotation_count, img):

        for _ in range(rotation_count):
            img = img.transpose(1, 0, 2)[:, ::-1]

        self.height, self.width, self.width_half, self.height_half = calculate_coordinate(img,
                                                                                          self.camera_distance_x,
                                                                                          self.camera_distance_y)

        return img

    def make_smooth_img(self, img):
        img = cv2.medianBlur(img, 5)

        return img

    def make_grayscal_img(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return img

    def draw_grit(self, img):
        # 1pxで白の線を描写
        cv2.line(img,
                 (self.width_half, 0),
                 (self.width_half, self.height),
                 255,
                 1)
        cv2.line(img,
                 (self.width_half+1, 0),
                 (self.width_half + 1, self.height),
                 255,
                 1)
        # 1pxで白の線を描写
        cv2.line(img,
                 (0, self.height_half),
                 (self.width, self.height_half),
                 255,
                 1)
        cv2.line(img,
                 (0, self.height_half + 1),
                 (self.width, self.height_half + 1),
                 255,
                 1)

        return img

    def get_circle_central_coordinate(self, img):
        x_list = []
        y_list = []
        norm_list = []
        degree_list = []

        # minRadius(最小半径) maxRadius(最大半径)
        self.circles = cv2.HoughCircles(img,
                                        cv2.cv.CV_HOUGH_GRADIENT,
                                        1,
                                        85,
                                        param1=50,
                                        param2=30,
                                        minRadius=50,
                                        maxRadius=70)

        try:
            # 各ボール中心座標を取得
            for i in self.circles[0, :]:
                # ボール中心座標を変換
                x = i[0]-self.width_half
                y = i[1] * (-1) + self.height_half

                # ベクトルの定義
                u = np.array([1, 0])
                v = np.array([x, y])
                norm, degree = vector_to_norm_and_degree(u, v)

                x_list.append(x)
                y_list.append(y)

                norm_list.append(norm)
                degree_list.append(degree)

                norm_and_degree_list = split_norm_and_degree(norm_list,
                                                             degree_list)

        except:
            norm_and_degree_list = []

        return norm_and_degree_list

    def draw_circle(self, img):
        try:
            self.circles = np.uint16(np.around(self.circles))

            # 円の描写
            for i in self.circles[0, :]:
                # draw the outer circle
                cv2.circle(img, (i[0], i[1]), i[2], 0, 2)

                # draw the center of the circle
                cv2.circle(img, (i[0], i[1]), 2, 0, 2)

                # 中心から各ボールへの矢印を描写
                for i in self.circles[0, :]:
                        # draw the outer circle
                    cv2.line(img,
                             (self.width_half, self.height_half),
                             (i[0], i[1]),
                             255,
                             2)
        except:
            cv2.putText(img,
                        'NOT FOUND',
                        (self.width_half - 80, self.height_half),
                        cv2.cv.CV_FONT_HERSHEY_SIMPLEX,
                        1.0,
                        255,
                        thickness=2)

        return img

    def draw_circle_central_coordinate(self, img):
        try:
            # 各ボール中心座標を取得
            for i in self.circles[0, :]:

                # ボール中心座標を変換
                x = i[0]-self.width_half
                y = i[1] * (-1) + self.height_half

                # ベクトルの定義
                u = np.array([1, 0])
                v = np.array([x, y])
                norm, degree = vector_to_norm_and_degree(u, v)

                # 直行座標表示
                # cv2.putText(img,
                #             '({},{},{})'.format(x, y, i[2]),
                #             (i[0], i[1]),
                #             cv2.cv.CV_FONT_HERSHEY_SIMPLEX,
                #             1.0,
                #             255,
                #             thickness=2)

                # 極座標表示
                cv2.putText(img,
                            '({},{},{})'.format(norm, degree, i[2]),
                            (i[0], i[1]),
                            cv2.cv.CV_FONT_HERSHEY_SIMPLEX,
                            1.0,
                            255,
                            thickness=2)

                # 原点表示
                cv2.putText(img,
                            '({},{})'.format(0, 0),
                            (self.width_half, self.height_half),
                            cv2.cv.CV_FONT_HERSHEY_SIMPLEX,
                            1.0,
                            255,
                            thickness=2)
        except:
            pass

        return img

    def release_camera(self):
        self.cap.release()

    def save_img(self, path, img):
        cv2.imwrite(path, img)


def main():
    get_ball_coordinate = GetBallCoordinate(0, 0)

    use_camera = True
    if use_camera == True:
        get_ball_coordinate.start_camera(0, 100)
        img = get_ball_coordinate.get_img()
        img = get_ball_coordinate.rotate_img(1, img)
        img = get_ball_coordinate.make_grayscal_img(img)
        img = get_ball_coordinate.make_smooth_img(img)
        img = get_ball_coordinate.draw_grit(img)
        norm_and_degree_list = get_ball_coordinate.get_circle_central_coordinate(
            img)
        img = get_ball_coordinate.draw_circle(img)
        img = get_ball_coordinate.draw_circle_central_coordinate(img)
        get_ball_coordinate.release_camera()

    else:
        IMG_PATH = "/home/pi/ball_position_estimation/picture/WIN_20190909_13_48_07_Pro.jpg"
        img = get_ball_coordinate.open_img(IMG_PATH)
        img = get_ball_coordinate.rotate_img(1, img)
        img = get_ball_coordinate.make_grayscal_img(img)
        img = get_ball_coordinate.make_smooth_img(img)
        img = get_ball_coordinate.draw_grit(img)
        norm_and_degree_list = get_ball_coordinate.get_circle_central_coordinate(
            img)
        img = get_ball_coordinate.draw_circle(img)
        img = get_ball_coordinate.draw_circle_central_coordinate(img)

    IMG_PATH = "/home/pi/ball_position_estimation/picture/photo.jpg"
    get_ball_coordinate.save_img(IMG_PATH, img)


if __name__ == "__main__":
    main()
