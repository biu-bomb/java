# OSI

![img](../.imgs/OSI)

| 顺序 | 层级       | 功能                                                         |
| ---- | ---------- | ------------------------------------------------------------ |
| 1    | 物理层     | 基础硬件设施以及规范                                         |
| 2    | 数据链路层 | 帧数据格式协议规定                                           |
| 3    | 网络层     | 建立``IP``节点关系，维护传输通道                             |
| 4    | 传输层     | 提供端到端(``port``)的可靠、透明数据传输服务。(``TCP``、``UDP``) |
| 5    | 会话层     | 维护表示层实体之间的有状态请求和响应会话。                   |
| 6    | 表示层     | 完成传输数据和业务数据的编解码转换功能。                     |
| 7    | 应用层     | 基于业务数据，直接提供网络服务。                             |

# TCP

| 顺序 | 层级   | OSI                            | 功能             |
| ---- | ------ | ------------------------------ | ---------------- |
| 1    | 链路层 | 物理层<br />数据链路层         | 物理传输基础     |
| 2    | 网络层 | 网络层                         | 机器节点网络     |
| 3    | 传输层 | 传输层                         | 端点稳定数据传输 |
| 4    | 应用层 | 会话层<br />表示层<br />应用层 | 应用             |

