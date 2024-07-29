const WebSocket = require('ws');
const { spawn } = require('child_process');

// 创建 WebSocket 服务器
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', ws => {
    console.log('客户端已连接');

    // 使用 ffmpeg 播放音频流
    const ffmpeg = spawn('ffmpeg', [
        '-f', 'webm',
        '-i', 'pipe:0',
        '-f', 'alsa',
        'default'
    ]);

    ws.on('message', message => {
        // 将接收到的数据传递给 ffmpeg
        ffmpeg.stdin.write(message);
    });

    ws.on('close', () => {
        ffmpeg.stdin.end();
        ffmpeg.kill('SIGINT');
        console.log('连接已关闭');
    });

    // 处理错误
    ffmpeg.on('error', err => {
        console.error('ffmpeg 错误:', err);
    });
});

console.log('WebSocket 服务器已启动，监听端口 8080');
