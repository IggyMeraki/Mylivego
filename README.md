## 使用Livego作为推拉流服务器（Linux）

1. ### 安装Livego

   ​	[gwuhaolin/livego: live video streaming server in golang (github.com)](https://github.com/gwuhaolin/livego)

   #### 运行Livego

   ​	终端打开Livego可执行二进制文件所在目录，执行

   ​		`./livego`

   1. 访问 `http://localhost:8090/control/get?room=movie` 获取一个房间的 **channelkey**(channelkey用于推流，movie用于播放).
   2. 推流: 通过`RTMP`协议推送视频流到地址 `rtmp://localhost:1935/{appname}/{channelkey}` (appname默认是`live`), 例如： 使用 `ffmpeg -re -i demo.flv -c copy -f flv rtmp://localhost:1935/{appname}/{channelkey}` 推流([下载demo flv](https://s3plus.meituan.net/v1/mss_7e425c4d9dcb4bb4918bbfa2779e6de1/mpack/default/demo.flv));

2. ### 部署index.html

   1. 安装node.js

      `apt install nodejs -y`

   2. 安装http-server

      `npm intall http-server`

   3. 在index.html中编辑url为你需要拉流的地址，在这里为

      ​	http://你的IP地址:7001/live/movie.flv

   4. 在index.html所在目录执行：

      `npx http-server -p 4000`(你要部署在的端口)

3. #### RTMP推流摄像头和麦克风

   ​	**第一次推流前务必访问**http://localhost:8090/control/get?room=movie

   在终端中输入以下命令行：

   ```bash
   ffmpeg -y \
   -thread_queue_size 1024 -f v4l2 -framerate 30 -video_size 640x480 -i /dev/video0 \
   -thread_queue_size 1024 -f alsa -i hw:2,0 \
   -c:v libx264 -preset ultrafast -tune zerolatency -maxrate 3000k -bufsize 3000k -pix_fmt yuv420p -g 30 \
   -c:a aac -b:a 128k -ar 44100 -ac 1 -af aresample=async=1:min_hard_comp=0.100000:first_pts=0 \
   -f flv rtmp://localhost:1935/live/rfBd56ti2SMtYvSgD5xAV0YU99zampta7Z7S575KLkIZ9PYk
   ```

   

   **命令行具体解析：**
   
   


​		**输入源**:

- ```
  -f v4l2 -framerate 30 -video_size 640x480 -i /dev/video0
  ```

  - 从 `/dev/video0` 设备（V4L2 设备）**默认摄像头**，捕获视频，设置帧率为 30 帧每秒，分辨率为 640x480。

- ```
  -f alsa -i hw:1,0
  ```

  - 从 ALSA 设备 `hw:1,0` 捕获音频。
  - Linux可以使用`arecord -l `命令查询音频设备，选择你需要的设备

**视频编码**:

- ```
  -c:v libx264 -preset ultrafast -tune zerolatency -maxrate 3000k -bufsize 3000k -pix_fmt yuv420p -g 30
  ```

  - 使用 `libx264` 编码器，设置编码预设为 `ultrafast`（极快模式），优化延迟。最大比特率和缓冲区大小为 3000 kbps，使用 `yuv420p` 像素格式。`-g 30` 设置关键帧间隔为每 30 帧（适合 30 FPS）。

**音频编码**:

- ```
  -c:a aac -b:a 128k -ar 44100 -ac 2 -af aresample=async=1:min_hard_comp=0.100000:first_pts=0
  ```

  - 使用 `aac` 编码器，音频比特率为 128 kbps，采样率为 44.1 kHz，立体声。`aresample` 滤镜用于音频重采样，并设置了特定的同步参数。

**输出**:

- ```
  -f flv rtmp://localhost:1935/live/rfBd56ti2SMtYvSgD5xAV0YU99zampta7Z7S575KLkIZ9PYk
  ```

  - 将编码后的流推送到本地的 RTMP 服务器，URL 为 `rtmp://localhost:1935/live/`，流密钥为 `rfBd56ti2SMtYvSgD5xAV0YU99zampta7Z7S575KLkIZ9PYk`。即为第一步中Livego的**channelkey**