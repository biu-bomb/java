# select

```c
int select (int n, fd_set *readfds, fd_set *writefds, fd_set *exceptfds, struct timeval *timeout);
```

1. 监控IO队列
   - ``readfds``
   - ``writefds``
   - ``exceptfds``
2. 阻塞等待：调用``select``会阻塞，直到有结果返回
3. 结果返回
   - 超时：``timeout``
   - 队列响应
     - ``readfds``
     - ``writefds``
     - ``exceptfds``
4. 就绪描述符
   - 遍历``fd_set``，找到就绪的文件描述符``O(n)``

| 优点                           | 缺点                                                         |
| ------------------------------ | ------------------------------------------------------------ |
| 1. 简单易维护<br />2. 平台兼容 | 1. 阻塞等待<br />2. 文件描述符1024，修改需要重编译内核<br />3. 遍历查找就绪文件描述符 |

# poll

```c
int poll (struct pollfd *fds, unsigned int nfds, int timeout);

struct pollfd {
    int fd; 
    short events; 
    short revents; 
};
```

|            | poll                     | select             |
| ---------- | ------------------------ | ------------------ |
| 文件描述符 | 新结构，通过事件区分     | 通过入参队列区分   |
| 描述符数量 | 无限制，数量过大性能下降 | 1024，修改重编内核 |
| 描述符筛选 | 遍历描述符集合           | 遍历描述符集合     |

# epoll

- ``epoll_create``

```c
int epoll_create(int size);
```

创建``epoll``句柄，并设置初始化监听最大的``fd+1``的值。

> <font color='red'>``size``作为初始化大小，而非最大限制，``epoll``无监听句柄数量限制。</font>

- ``epoll_ctl``

```c
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
```

| param     | description                                                  |
| --------- | ------------------------------------------------------------ |
| ``epfd``  | 监听的``epfd``句柄<br />也就是``epoll_create``的返回值       |
| ``op``    | 操作<br />``EPOLL_CTL_ADD``：添加<br />``EPOLL_CTL_DEL``：删除<br />``EPOLL_CTL_MOD``：修改 |
| ``fd``    | 需要监听的文件描述符                                         |
| ``event`` | 监听的事件，结构如下                                         |

```c
struct epoll_event {
  __uint32_t events; 
  epoll_data_t data; 
};
```

| events           | description                                                  |
| ---------------- | ------------------------------------------------------------ |
| ``EPOLLIN``      | 可读                                                         |
| ``EPOLLOUT``     | 可写                                                         |
| ``EPOLLPRI``     | 紧急数据可读                                                 |
| ``EPOLLERR``     | 错误                                                         |
| ``EPOLLHUP``     | 挂断                                                         |
| ``EPOLLET``      | 设置为``Edge Triggered``边缘触发，相对``Level Triggered``水平触发 |
| ``EPOLLONESHOT`` | 仅监听一次，触发完毕移除队列                                 |

- `` int epoll_wait``

```c
int epoll_wait(int epfd, struct epoll_event * events, int maxevents, int timeout);
```

监听，等待``IO``就绪。

## 工作模式

|      | ET                                                   | LT                                                       |
| ---- | ---------------------------------------------------- | -------------------------------------------------------- |
| 名称 | ``Edge Triggered``<br />边缘触发                     | ``Level Triggered``<br />水平触发                        |
| 动作 | 描述符就绪，必须处理<br />下次``epoll_wait``不再通知 | 描述符就绪，可以延迟处理<br />下次``epoll_wait``继续通知 |
| 默认 | ``false``                                            | ``true``                                                 |
| 支持 | ``non-block socket``                                 | ``block socket``<br />``non-block socket``               |
| 优点 | 降低``epoll_wait``被触发次数效率更高                 | 延迟处理，多次通知<br />方便调度，防止遗漏               |
| 缺点 | 必须``non-block``，阻塞会导致任务饿死                | 频繁触发``epoll_wait``                                   |

