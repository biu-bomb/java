# 内存模型

![这里写图片描述](../.imgs/8cedf683cdfacb3cfcd970cd739d5b9d.png)

详情参考[volatile](volatile.md)

# 重排序

| 重排序     | 原因                    | 负面影响                   |
| ---------- | ----------------------- | -------------------------- |
| 编译重排序 | 压缩操作 ，替身代码性能 | 破坏数据依赖、破坏控制依赖 |
| 指令重排序 | 无关操作，多CPU分散运行 | 破坏数据依赖、破坏控制依赖 |
| 内存重排序 | 就近缓存，提升数据操作  | 线程间数据不一致           |

# 防护手段

| 规则               | 功能                               |
| ------------------ | ---------------------------------- |
| ``happens-before`` | 强制指定操作间顺序                 |
| ``as-if-serial``   | 单线程运行必定正常                 |
| 内存屏障           | 内存屏障间动作原子                 |
| ``synchronized``   | 释放锁同步主存<br />获取锁失效缓存 |

==happens-before==

- 对于任意一个操作，它应该``happens-before``之后的任意操作
- 解锁应该``happens-before``于下一个加锁操作
- ``volatile``的写，应该``happens-before``下一次的``volatile``的读
- 传递性：``A happens-before B``, 且``B happens-before C``，则``A happens-before C``
- ``start``：如果``A``线程进行``B.start()``，``B.start()``应该``happens-before``于``B``线程中的任意操作
- ``join``：如果``A``进行``B.join()``并成功，``B``线程中的任意操作应该``happens-before``返回成功后的``A``的任意操作
- ``interrupt``：``interrupt``方法应当``happens-before``于中断线程中的中断逻辑。