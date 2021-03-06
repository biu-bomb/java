# 并发冲突

| 冲突场景 | 引发问题                                               |
| -------- | ------------------------------------------------------ |
| 读-读    | 不存在问题，无需并发控制                               |
| 读-写    | 有线程安全问题，可能导致脏读、幻读、不可重复度         |
| 写-写    | 有线程安全问题，可能造成第一类更新丢失、第二类更新丢失 |

- 更新丢失

| 类别           | 说明     | 例子                                                         |
| -------------- | -------- | ------------------------------------------------------------ |
| 第一类更新丢失 | 回滚覆盖 | ``1000``取``100``，数据库修改为``900``<br />转入``100``，金额为``1000``<br />取钱失败，回滚为``1000``，覆盖转账记录 |
| 第二类更新丢失 | 修改覆盖 | 金额``1000``，两个事务并发转入``100``<br />理论应该为``1200``，由于独立写入，结果为``1100``<br />两个事务之间修改覆盖 |

# MVCC

``Multi-Version Concurrency Control``，多版本并发控制；针对解决``读-写``下的并发冲突问题。

## 读取方式

| 读取方式 | 说明                 | 例子                                               |
| -------- | -------------------- | -------------------------------------------------- |
| 当前读   | 直接读取当前最新数据 | ``select lock in share mode``                      |
| 快照读   | 读取历史快照数据     | ``select``，如果事务隔离级别为串行，退化为当前读。 |

## 行记录结构

![img](../.imgs/column)

| column          | byte | description                                                  |
| --------------- | ---- | ------------------------------------------------------------ |
| ``DB_ROW_ID``   | 6    | 未声明主键时候的默认主键                                     |
| ``DB_TRX_ID``   | 6    | 事务``ID``，顺序递增                                         |
| ``DB_ROLL_PTR`` | 7    | 回滚指针，指向当前记录``ROLLBACK SEGMENT``的``undo log``记录 |

最后形成一个事务版本链

![img](../.imgs/tx_link)

## ``Read View``

![img](../.imgs/readView)

快照读的时候就会生成``Read View``，根据事务活跃度分为三个部分

| 活跃阶段   | 数据特点             |
| ---------- | -------------------- |
| 已提交事务 | 数据已提交，不会变更 |
| 进行中事务 | 数据操作中，可能变更 |
| 未开始事务 | 事务申请中，还没开始 |

对于行记录的``DB_TRX_ID``，它能读取到的数据分为三种

| 数据类型     | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 已提交数据   | 已经提交的数据，不会再变更，可读                             |
| 当前事务数据 | 不能读取其他事务数据，造成脏读<br />活跃数据只能读取自身事务 |
| 未删除数据   | 历史数据如果标记``delete_flag=true``，删除数据不读取         |

# RR

- 提交前快照读

| 事务A                | 事务B                                      |
| -------------------- | ------------------------------------------ |
| 开启事务             | 开启事务                                   |
| ``query: money=500`` | ``query: money=500``                       |
| ``set: money = 400`` |                                            |
| ``commit``           |                                            |
|                      | ``select: money = 500``                    |
|                      | ``select lock in share mode: money = 400`` |

- 提交后快照

| 事务A                | 事务B                                       |
| -------------------- | ------------------------------------------- |
| 开启事务             | 开启事务                                    |
| ``query: money=500`` |                                             |
| ``set: money=400``   |                                             |
| ``commit``           |                                             |
|                      | ``select: monty=400``                       |
|                      | ``select lock in share monde: money = 400`` |

在``RR``级别应该可以得出结论

- **快照只在第一次快照读时候建立Read View**
- **RR级别下，同一事务内的快照读都是共用一份Read View，解决不可重复读问题**
  - ``RC``级别下，每次快照读都是重新建立``Read View``