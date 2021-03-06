# ACID

| ACID               | 性质   | 说明                                                         |
| ------------------ | ------ | ------------------------------------------------------------ |
| ``A(Atomicity)``   | 原子性 | 事务中的操作集合，要么全部成功，要么全部失败                 |
| ``C(Consistency)`` | 一致性 | 事务状态变化的一致性，数据准确性                             |
| ``I(Isolation)``   | 隔离性 | 事务之间的相互感知屏蔽<br />即使是同一时间，同一数据两者操作应该互不影响，互不干扰 |
| ``D(Durability)``  | 持久性 | 事务提交状态的延续性<br />提交过的事务无论如何不会变更和丢失 |

# 事务问题

| 问题       | 描述                                                     |
| ---------- | -------------------------------------------------------- |
| 脏读       | 两个事务进行未提交，一个事务读取到另一个事务中的数据变更 |
| 不可重复读 | 事务进行中，重复查询情况下，某条数据两次查询呈现不同状态 |
| 幻读       | 事务进行中，对整体数据集的操作没有全部覆盖               |

# 隔离级别

| 隔离级别            | 杜绝问题               | 效果描述                                                   |
| ------------------- | ---------------------- | ---------------------------------------------------------- |
| ``Read UnCommited`` | 无                     | 读取不加锁，还是能够读到未提交数据                         |
| ``Read Commited``   | 脏读                   | 读取加锁，不会读取到未提交数据，但是对于已提交数据能够读取 |
| ``Repeatable read`` | 脏读、不可重复度       | 锁定数据集，新提交数据不会读取                             |
| ``Serializable``    | 脏读、不可重复度、幻读 | 确定时刻，仅存在唯一事务，不可能事务冲突                   |

