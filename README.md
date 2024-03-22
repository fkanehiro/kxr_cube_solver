
2024年3月20日に行われた東京大学稲葉雅幸教授の最終講義第1部としておこなわれたJSK OB・OG会用に作成した、KXRでルービックキューブを解くプログラムです。
[!['altテキスト'](https://github.com/fkanehiro/kxr_cube_solver/assets/845257/afad05b2-a767-409a-a879-5e31ad2c2718)](https://youtu.be/CVYYmKJGDNQ)

# KXRの改造
## グリッパ取付角度の変更
グリッパの取付を90度変更します。
## グリッパ先端形状の変更
[ダイソーのすべり止めシート](https://jp.daisonet.com/collections/living0223/products/4940921833423)を指先のサイズに合わせてカットし、両面テープで貼り付けます。
# ルービックキューブ
一辺が56mmの3x3ルービックキューブを用います。軽い力で回転させることが可能な[MonsterGo社のMG3x3](https://www.amazon.co.jp/gp/product/B0B67PYMHB/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&th=1)を使用しました。色認識もこのルービックキューブに合わせて調整しています。
# インストール
JSK環境がインストールされたDebian10が前提です。
```
$ pip3 install kociemba
$ cd <catkin workspace>/src
$ git clone git@github.com:fkanehiro/kxr_cube_solver
$ cd ..
$ catkin build
```
# 初期設定
euslisp/cubeSolver.lのinit-pose関数でしている関節の角度を調整します。
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
- n 状態遷移が手動になっている際に次の状態に遷移させます。
- e ルービックキューブを見る動作または解く動作を中断し、init-pose姿勢に戻ります。ルービックキューブの把持状態がずれてしまった場合などに用います。
- x neutral姿勢に移行し、サーボをOFFにします。
# 参考
- https://github.com/muodov/kociemba
- https://github.com/kkoomen/qbr
- https://www.thingiverse.com/thing:3826740
   
