# CAP

![img](../.imgs/bg2018071607.jpg)

- Consistency(一致性)：针对每个节点请求数据应该一致

- Availability(可用性)：对节点进行请求，应当立即响应服务

- Partition tolerance(分区容错性)：部分节点或网络分区出现故障，仍然能够对外提供服务。

## CA

分布式系统中，数据一致性的要求，必须满足读操作读到的是最新的修改值。

但是具体修改的节点无法确认，甚至不可到达。

这时候能同时满足``CA``的，就是：修改的节点就是当前查询的节点。也就成了单机。

此时必然不能够满足``P``：单点机器。

## AP

还是对于一致性的要求，节点中最新修改值的更新涉及网络传播。

此时不能够满足``C``：因为数据同步优先于业务执行，可用性不能满足。

## CP

``C``同``A``比较，很明显，两者是不相容的，``A``必然需要一定的时间进行数据同步。

因此，当选择``CP``时，数据一致性不一定能够得到满足。

---

**CAP**的两个基本矛盾点

- **C**和**A**两者不相容
- **P**是分布式系统的必须项

但是只有在极端情况下，``C``和``A``才会相互排斥，如果在两次请求之间，已经完成数据同步，那么是不存在互斥问题。

另一种办法，就是数据修正，或者补偿。``CA``的互斥在于``A``在``C``之前，如果能够``C``在``A``之前，就能够满足``CA``的需求。

基于此，需要探知不同分区的数据差异，在``C``之后进行``A``的数据修正操作。

# BASE

补偿的思想，更多的强调了最终结果的一致性，允许过程中的分区差异性。

- Basically Available(基本可用)：部分节点出现故障，不影响对外提供服务
- Soft State(软状态)：中间过程并不要求达到严格的数据一致
- Eventually Consistent(最终一致性)：在规定时间后，数据必须达到最终一致性
  - 因果一致性：A通知B，则B的数据操作一定基于A更新的值，C无限制
  - 读己之所写：节点重视能访问到自己更新的最新值，而非旧值
  - 会话一致性：同一个会话内，满足读己之所写的一致性
  - 单调读一致性：如果节点从系统读取某个值，后续的读都不应该返回更旧的值
  - 单调写一致性：同一节点的写操作必须保证顺序性

# 一致性

一致性，并非是说每个节点之间的数据保持相等。我的理解更偏向于**延续性**。

也就是说，在数据变化的轨迹中，每次变化都有明确的衡量标准。

数据的一致性正是由这种变化的延续性进行保证的。

---

基础数据库``ACID``中的``C``，本身事务也并非先来后道，看的是提交时机；但是每次事务的确是原子操作。

``BASE``中，节点直接之的数据同步不可能以原子方式进行传播；但是如果能够对缺失、延迟的操作一一补全，数据最终的确也是一致的。





