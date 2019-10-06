ball_position_getter
====

## Description
This is a program for using the Raspberry Pi as a ball detection sensor. The position information of the ball detected by shooting from directly above is output in distance and angle. Because it is under development, it is a beta version.

このプログラムはラズベリーパイをボール検出用のセンサーとして使うためのプログラムです．ボールまでの距離と角度をシリアル通信で返します．このプログラムは開発中でベータ版です．

## Requirement
- Python 2.7.13
- OpenCV 2.4.9.1
- Pillow 5.1.0
- Numpy
- Tkinter

Just installing Pillow is not enough. Add the module by executing the following command. 

Pillowをインストールしただけでは描写系のライブラリに不足があるため追加で以下のパッケージをインストールして下さい．
  
```sudo apt-get install python-imaging-tk```

## Usage
The ball position information is returned by sending a command via serial communication.

シリアル通信でコマンドを送ることにより，ボールの位置情報を返します．
