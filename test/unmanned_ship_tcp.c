#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <pthread.h>

// 配置参数
#define SERVER_IP "127.0.0.1"  // 服务器IP（根据实际修改） 8.130.132.91
#define SERVER_PORT 9001      // 服务器端口（根据实际修改）
#define BUF_SIZE 1024              // 数据缓冲区大小
#define RECONNECT_INTERVAL 5       // 断线重连间隔（秒）
#define HEARTBEAT_INTERVAL 10      // 心跳包发送间隔（秒）

// 无人船数据结构体（示例）
typedef struct {
    unsigned int head;          // 包头标识 0xAA55
    float longitude;            // 经度
    float latitude;             // 纬度
    float speed;                // 速度 (m/s)
    float direction;            // 航向 (度)
    unsigned short crc16;       // CRC校验
    unsigned int tail;          // 包尾标识 0x55AA
} UnmannedShipData;

// 全局变量
int sock_fd = -1;               // TCP套接字
pthread_mutex_t sock_mutex;     // 套接字互斥锁

// CRC16校验（简化版）
unsigned short crc16_calc(unsigned char *data, int len) {
    unsigned short crc = 0xFFFF;
    for (int i = 0; i < len; i++) {
        crc ^= (unsigned short)data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return crc;
}

// 设置非阻塞套接字
int set_nonblock(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

// 建立TCP连接
int tcp_connect() {
    pthread_mutex_lock(&sock_mutex);
    
    // 关闭旧连接
    if (sock_fd >= 0) {
        close(sock_fd);
        sock_fd = -1;
    }

    // 创建套接字
    sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (sock_fd < 0) {
        perror("socket create failed");
        pthread_mutex_unlock(&sock_mutex);
        return -1;
    }

    // 设置非阻塞
    set_nonblock(sock_fd);

    // 服务器地址配置
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        perror("invalid server IP");
        close(sock_fd);
        sock_fd = -1;
        pthread_mutex_unlock(&sock_mutex);
        return -1;
    }

    // 连接服务器（非阻塞）
    int ret = connect(sock_fd, (struct sockaddr*)&server_addr, sizeof(server_addr));
    if (ret == 0) {
        printf("TCP connected to %s:%d\n", SERVER_IP, SERVER_PORT);
        pthread_mutex_unlock(&sock_mutex);
        return 0;
    } else if (errno == EINPROGRESS) {
        // 连接中，等待完成
        fd_set write_fds;
        FD_ZERO(&write_fds);
        FD_SET(sock_fd, &write_fds);
        struct timeval timeout = {3, 0};  // 3秒超时
        ret = select(sock_fd + 1, NULL, &write_fds, NULL, &timeout);
        if (ret > 0 && FD_ISSET(sock_fd, &write_fds)) {
            int err = 0;
            socklen_t err_len = sizeof(err);
            getsockopt(sock_fd, SOL_SOCKET, SO_ERROR, &err, &err_len);
            if (err == 0) {
                printf("TCP connected to %s:%d\n", SERVER_IP, SERVER_PORT);
                pthread_mutex_unlock(&sock_mutex);
                return 0;
            }
        }
    }

    // 连接失败
    perror("TCP connect failed");
    close(sock_fd);
    sock_fd = -1;
    pthread_mutex_unlock(&sock_mutex);
    return -1;
}

// 发送无人船数据
int send_ship_data(UnmannedShipData *data) {
    if (data == NULL) return -1;

    pthread_mutex_lock(&sock_mutex);
    if (sock_fd < 0) {
        pthread_mutex_unlock(&sock_mutex);
        return -1;
    }

    // 填充校验值
    data->crc16 = crc16_calc((unsigned char*)data, sizeof(UnmannedShipData) - sizeof(unsigned short) - sizeof(unsigned int));
    
    // 发送数据
    int ret = send(sock_fd, data, sizeof(UnmannedShipData), 0);
    if (ret <= 0) {
        perror("send data failed");
        close(sock_fd);
        sock_fd = -1;
        pthread_mutex_unlock(&sock_mutex);
        return -1;
    }

    printf("Send data success: lon=%.6f, lat=%.6f, speed=%.2f, dir=%.1f\n",
           data->longitude, data->latitude, data->speed, data->direction);
    pthread_mutex_unlock(&sock_mutex);
    return 0;
}

// 心跳包线程
void *heartbeat_thread(void *arg) {
    UnmannedShipData heartbeat = {0};
    heartbeat.head = 0xAA55;
    heartbeat.tail = 0x55AA;
    heartbeat.longitude = 0.0;
    heartbeat.latitude = 0.0;
    heartbeat.speed = 0.0;
    heartbeat.direction = 0.0;

    while (1) {
        sleep(HEARTBEAT_INTERVAL);
        // 如果连接断开，先重连
        if (sock_fd < 0) {
            tcp_connect();
        }
        // 发送心跳包
        send_ship_data(&heartbeat);
    }
    return NULL;
}

int main() {
    // 初始化互斥锁
    pthread_mutex_init(&sock_mutex, NULL);

    // 启动心跳线程
    pthread_t hb_tid;
    pthread_create(&hb_tid, NULL, heartbeat_thread, NULL);
    pthread_detach(hb_tid);

    // 初始化连接
    tcp_connect();

    // 模拟无人船数据发送
    UnmannedShipData ship_data = {0};
    ship_data.head = 0xAA55;
    ship_data.tail = 0x55AA;
    ship_data.longitude = 120.123456;  // 示例经度
    ship_data.latitude = 30.654321;   // 示例纬度

    // 主循环：模拟数据更新并发送
    for (int i = 0; i < 100; i++) {
        // 模拟数据变化
        ship_data.speed = 1.2 + i * 0.1;
        ship_data.direction = 90.0 + i * 1.5;

        // 如果连接断开，尝试重连
        if (sock_fd < 0) {
            if (tcp_connect() != 0) {
                printf("Reconnect failed, wait %d seconds...\n", RECONNECT_INTERVAL);
                sleep(RECONNECT_INTERVAL);
                continue;
            }
        }

        // 发送数据
        send_ship_data(&ship_data);
        sleep(1);  // 1秒发送一次
    }

    // 清理资源
    pthread_mutex_lock(&sock_mutex);
    if (sock_fd >= 0) close(sock_fd);
    pthread_mutex_unlock(&sock_mutex);
    pthread_mutex_destroy(&sock_mutex);

    return 0;
}