#!/bin/bash

echo "清理旧文件..."
rm -rf build dist __pycache__ .pyarmor_output

echo "用 PyArmor 加密源代码..."
pyarmor gen -r \
  client.py \
  game_login.py \
  game_logic.py \
  snake.py \
  player1.py player2.py player3.py \
  player4.py player5.py player6.py \
  player7.py player8.py player9.py \
  server.py

echo "用 PyInstaller 打包（加入资源文件）..."

SEP=":"  # Mac 使用冒号分隔 add-data

pyinstaller --noconfirm --clean --windowed \
  --name SnakeGame \
  --add-data "assets${SEP}assets" \
  --add-data "fontEND.ttf${SEP}." \
  --add-data "eat.mp3${SEP}." \
  dist/client.py

echo "打包完成！可执行文件已生成于 dist/SnakeGame"
