| 垃圾收集器       | 年龄分代 | 回收算法                                        |
| ---------------- | -------- | ----------------------------------------------- |
| ``Serial``       | 年轻代   | 标记-复制                                       |
| ``Serial``       | 年老代   | 标记-压缩                                       |
| ``ParNew``       | 年轻代   | 标记-复制<br />并行回收<br />多线程版``Serial`` |
| ``Parallel``     | 年轻代   | 标记-复制<br />并行回收<br />吞吐量优先         |
| ``Parallel Old`` | 年老代   | 标记-压缩<br />并行回收                         |
|                  |          |                                                 |
|                  |          |                                                 |

