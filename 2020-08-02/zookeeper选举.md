# zookeeper选举

## 状态描述

| 状态          | 描述                              |
| ------------- | --------------------------------- |
| ``LEADING``   | ``leader``节点                    |
| ``LOOKING``   | 选举中                            |
| ``FOLLOWING`` | 从节点，发送给``leader``投票      |
| ``OBSERBING`` | 同``following``，但是不具备投票权 |

## 启动选举

> - 过半原则
> - max(myid)

假设存在五台机器，分别启动，选举状态如下

- 启动1：当前只有一台机器，投票给自己，票数不过半，选举未完成
- 启动2: 
  - 1(looking)节点投票给myid更大的2节点
  - 2(looking)投票给自身
  - 票数未过半，选举未完成
- 启动3
  - 1(following) -> 3（leading）
  - 2(following) -> 3 (leading)
  - 3 -> 3
  - 票数过半，选举完成，3为主节点
- 启动4
  - 主节点选举完成，4(following)->3(leading)
- 启动5
  - 主节点选举完成，5(following)->3(leading)

## 宕机选举

> - 过半原则
> - max(zxid)
> - max(myid)

具体步骤同启动选举，但是对比方案前置$\max(\text{zxid})$作为选举条件。

