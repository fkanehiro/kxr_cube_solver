
2024年3月20日に行われた東京大学稲葉雅幸教授の最終講義第1部としておこなわれたJSK OB・OG会用に作成した、KXRでルービックキューブを解くプログラムです。

# KXRの改造
## グリッパ取付角度の変更
## グリッパ先端形状の変更
# ルービックキューブ
# インストール
JSK環境がインストールされたubuntu20.04LTSが前提です。
```
$ pip3 install kociemba
$ cd <catkin workspace>/src
$ git clone git@github.com:fkanehiro/kxr_cube_solver
$ cd ..
$ catkin build
```
# 初期設定
# 実行方法
```
terminal1$ roslaunch
terminal2$ roslaunch
```
画像処理結果を表示するウィンドウが開き、KXRのサーボがONになり、初期姿勢に移行しながら、「ルービックキューブを手の上においてください」としゃべります。
ルービックキューブを手の上に置きaキーを押すとルービックキューブを見回した後解き始めます。解き終わると最初の状態に戻るので、ルービックキューブを取って状態を変えて置き、aキーを押す、という流れを繰り返すことができます。

## キー操作
画像処理結果を表示しているウィンドウの上でキーを押すことで以下の操作ができます。
- a 状態遷移の自動・手動をトグルで切り替えます。
# 参考
- https://github.com/muodov/kociemba
- https://github.com/kkoomen/qbr
- https://www.thingiverse.com/thing:3826740
   
