# GC分代假说

- 弱分代假说（Weak Generational Hypothesis）：绝大多数对象都是朝生夕灭的。
- 强分代假说（Strong Generational Hypothesis）：熬过越多次垃圾收集过程的对象就越难以消亡。
- 跨代引用假说（Intergenerational Reference Hypothesis）：跨代引用相对于同代引用来说仅占极少数。

# 新生代

新创建对象都在这，整体区域分为三部分

| generation     | description                                                  |
| -------------- | ------------------------------------------------------------ |
| ``eden``       | 新创建的对象基本都在这                                       |
| ``survivor-1`` | ``mirror-GC``时候存活对象复制到此<br />元素来自``eden``或者``survivor-2`` |
| ``survivor-2`` | 同``survivor-1``                                             |

- 默认比例：``eden:survivor-1:survivor-2 = 8:1:1``
- ``GC``年龄：``survivor``来回复制，复制一次年龄``+1``，超出限度移到老年代，默认``16``
- ``GC``算法：复制算法

# 老年代

- 对象来源
  - ``GC``年龄超过阈值，移动到老年代
  - 新建对象大小超过阈值，移动到老年代
- ``GC``算法：标记清除

# 参数说明

| property                       | description           |
| ------------------------------ | --------------------- |
| ``-Xms``                       | 最小堆空间            |
| ``-Xmx``                       | 最大堆空间            |
| ``-XX:NewSize``                | 新生代最小值          |
| ``-XX:MaxNewSize``             | 新生代最大值          |
| ``-XX:NewRatio``               | 新生代：老年代        |
| ``-XX:SurvivorRatio``          | ``eden``:``survivor`` |
| ``-XX:MaxTenuringThreshold``   | ``GC``年龄阈值        |
| ``-XX:PretenureSizeThreshold`` | 大对象阈值            |

