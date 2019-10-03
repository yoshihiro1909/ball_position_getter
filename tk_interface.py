# -*- coding: utf-8-*-

import os
import threading
import time
import Tkinter as tk

import serial
from PIL import Image, ImageTk

import get_ball_coordinate


DEFAULT_IMG_PATH = '/home/pi/ball_position_estimation/picture/seim_start.png'
IMG_PATH = '/home/pi/ball_position_estimation/picture/photo.jpg'


class GetBallInterface():
    def __init__(self):
        self.img = None  # グローバル変数
        self.constantly_updated_image = None
        self.root = tk.Tk()
        self.root.title(u"ボール認識システム")
        self.root_height = 445
        self.root_width = 800
        self.root.geometry("{}x{}".format(self.root_width, self.root_height))

        self.connect_serial_port()

        self.connect_camera()

        self.event = threading.Event()

    def connect_camera(self):
        self.get_ball_coordinate = get_ball_coordinate.GetBallCoordinate(0, 0)
        self.get_ball_coordinate.start_camera(0, 100)

    def connect_serial_port(self):
        path = '/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0'
        self.port = serial.Serial(path, 9600)
        time.sleep(2)

    def resize_img(self, img):
        img_width, img_height = img.size

        if img_height > img_width:
            magnification = float(img_height) / float(self.root_height)
            resize_height = int(img_height/magnification)
            resize_width = int(img_width/magnification)
            img = img.resize((resize_width, resize_height))
        else:
            magnification = float(img_height) * 2 / float(self.root_height)
            resize_height = int(img_height/magnification)
            resize_width = int(img_width/magnification)
            img = img.resize((resize_width, resize_height))

        return img, resize_width, resize_height

    def read_serial(self):
        while True:
            read_data = self.port.readline()
            if read_data == b"shutter\r\n":
                print("シリアルポートからシャッターボタンが押された")
                self.shutter_btn()

            elif read_data == b"reset\r\n":
                print("シリアルポートからリセットボタンが押された")
                self.reset_btn()

            elif read_data == b"shutdown\r\n":
                print("シリアルポートからシャットダウンボタンが押された")
                self.shutdown_btn()

            if self.event.wait(timeout=0.01):
                break

    def serial_write(self, text):
        text = str(text)+"\r\n"
        text.encode()
        write_data = text
        self.port.write(write_data)

    def read_img(self):
        while True:
            self.constantly_updated_image = self.get_ball_coordinate.get_img()

            if self.event.wait(timeout=0.01):
                break

    def shutter_btn(self):
        print("シャッターボタンが押された")

        img = self.constantly_updated_image
        img = self.get_ball_coordinate.rotate_img(1, img)
        img = self.get_ball_coordinate.make_grayscal_img(img)
        img = self.get_ball_coordinate.make_smooth_img(img)
        img = self.get_ball_coordinate.draw_grit(img)
        norm_and_degree_list = self.get_ball_coordinate.get_circle_central_coordinate(
            img)
        img = self.get_ball_coordinate.draw_circle(img)
        img = self.get_ball_coordinate.draw_circle_central_coordinate(img)

        self.serial_write(norm_and_degree_list)
        print(norm_and_degree_list)

        path = IMG_PATH
        self.get_ball_coordinate.save_img(path, img)
        self.diplay_img(path)

    def reset_btn(self):
        print("リセットボタンが押された")
        path = DEFAULT_IMG_PATH
        self.diplay_img(path)

    def shutdown_btn(self):
        print("シャットダウンボタンが押された")
        path = DEFAULT_IMG_PATH
        self.diplay_img(path)
        self.event.set()
        self.port.close()
        self.get_ball_coordinate.release_camera()
        self.root.quit()

        #os.system("sudo shutdown -h now")

    def make_canvas(self):
        # self.canvas_width = resize_width
        # self.canvas_height = resize_height
        self.canvas_width = 333
        self.canvas_height = 445
        self.canvas = tk.Canvas(bg="black",
                                width=self.canvas_width,
                                height=self.canvas_height)
        self.canvas.place(x=0, y=0)  # 左上の座標を指定

    def diplay_img(self, path):
        # 画像を準備
        self.img = Image.open(path)
        self.img, resize_width, resize_height = self.resize_img(self.img)
        self.img = ImageTk.PhotoImage(self.img)

        # キャンバスに画像を表示する
        img_x = (self.canvas_width-resize_width)/2
        img_y = (self.canvas_height-resize_height)/2
        self.canvas.create_image(img_x,
                                 img_y,
                                 image=self.img,
                                 anchor=tk.NW)
        print("画像を表示した")

    def make_thread(self):
        thread1 = threading.Thread(target=self.read_serial)
        thread1.start()
        thread2 = threading.Thread(target=self.read_img)
        thread2.start()

    def set_tk(self):
        # キャンバスを作成する
        self.make_canvas()

        # キャンバスに画像を表示する
        path = DEFAULT_IMG_PATH
        self.diplay_img(path)

        # ボタンの位置調整
        btn_width = 50
        btn_height = 3
        btn_place_x = self.canvas_width + 20
        btn_place_y = 80
        btn_place_b = 30

        btn1 = tk.Button(self.root,
                         text='シャッター',
                         width=btn_width,
                         height=btn_height,
                         command=self.shutter_btn)
        btn1.place(x=btn_place_x, y=1*btn_place_y+btn_place_b)

        btn2 = tk.Button(self.root,
                         text='リセット',
                         width=btn_width,
                         height=btn_height,
                         command=self.reset_btn)
        btn2.place(x=btn_place_x, y=2*btn_place_y+btn_place_b)

        btn3 = tk.Button(self.root,
                         text='シャットダウン',
                         width=btn_width,
                         height=btn_height,
                         command=self.shutdown_btn)
        btn3.place(x=btn_place_x, y=3*btn_place_y+btn_place_b)

    def run_tk(self):
        self.make_thread()
        tk.mainloop()


def main():
    get_ball_interface = GetBallInterface()
    get_ball_interface.set_tk()
    get_ball_interface.run_tk()


if __name__ == "__main__":
    main()
