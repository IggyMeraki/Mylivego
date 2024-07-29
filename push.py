import cv2 as cv
import time
import subprocess as sp
import multiprocessing
import platform
import psutil

class stream_pusher(object):
    def __init__(self, rtmp_url=None, raw_frame_q=None): #类实例化的时候传入rtmp地址和帧传入队列
        self.rtmp_url = rtmp_url
        self.raw_frame_q = raw_frame_q
       

        fps = 30  # 设置帧速率
        # 设置分辨率
        width = 640  # 宽
        height = 480  # 高
        
        # 设置FFmpeg命令文本
        self.command = ['ffmpeg',
               '-y',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',
               '-s', "{}x{}".format(width, height),
               '-r', str(fps),
               '-i', '-',
               '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p',
               '-preset', 'ultrafast',
               '-f', 'flv',
               self.rtmp_url]

    # 对获取的帧做一些画面处理的方法，返回完成处理的帧。
    def __frame_handle__(self, raw_frame, text, shape1, shape2):
        #帧用cv2进行一些处理，比如写上文本，画矩形等
        return(raw_frame)

    # 向服务器推送
    def push_frame(self):
        # 指定在哪些cpu核上运行。我的ARM有6核，前4核较慢做辅助处理。后2核较快，做核心程序的处理。这里指定推流动作在慢的4个核中运行
        p = psutil.Process()
        p.cpu_affinity([0,1,2,3])
        # 配置向os传递命令的管道
        p = sp.Popen(self.command, stdin=sp.PIPE)

        while True:
            if not self.raw_frame_q.empty(): # 如果输入管道不为空
                # 把帧和相关信息从输入队列中取出
                raw_frame, text, shape1, shape2 = self.raw_frame_q.get() 
                # 对获取的帧进行画面处理
                frame = self.__frame_handle__(raw_frame, text, shape1, shape2)

                # 把内容放入管道，放入后有os自己去执行
                p.stdin.write(frame.tostring())            
            else:
                time.sleep(0.01)


    # 启动运行
    def run(self):
        # 定义一个子进程
        push_frame_p = multiprocessing.Process(target=self.push_frame, args=())
        push_frame_p.daemon = True # 把子进程设置为daemon方式
        push_frame_p.start() # 运行子进程


if __name__ == '__main__':
    # 根据不同的操作系统，设定读取哪个摄像头
    if platform.system() == 'Linux': # 如果是Linux系统
        cap = cv.VideoCapture(0) # 绑定编号为0的摄像头
        cap.set(3, 640) # 设置摄像头画面的宽
        cap.set(4, 480) # 设置摄像头画面的高
    elif platform.system() == 'Darwin': # 如果是苹果的OS X系统
        cap = cv.VideoCapture(0) #绑定编号为0的摄像头
        cap.set(3, 640)
        cap.set(4, 480)
    else: # 没有windows系统，所以就不判断了
        exit(0)

    rtmpUrl = "rtmp://localhost:1935/live/rfBd56ti2SMtYvSgD5xAV0YU99zampta7Z7S575KLkIZ9PYk"  # 用vcl等直播软件播放时，也用这个地址
    raw_q = multiprocessing.Queue() # 定义一个向推流对象传入帧及其他信息的队列

    my_pusher = stream_pusher(rtmp_url=rtmpUrl, raw_frame_q=raw_q) # 实例化一个对象
    my_pusher.run() # 让这个对象在后台推送视频流
    while 1:
        _, raw_frame = cap.read()
        info = (raw_frame,'2','3','4') # 把需要送入队列的内容进行封装
        if not raw_q.full(): # 如果队列没满
            raw_q.put(info) # 送入队列
        cv.waitKey(1)
    cap.release()
    print('finish')