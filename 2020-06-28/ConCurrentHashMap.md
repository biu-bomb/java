# 扰动函数

```java
    static final int spread(int h) {
        return (h ^ (h >>> 16)) & HASH_BITS; // 有位数限制
    }
```

# 初始化

```java
 private final Node<K,V>[] initTable() {
        Node<K,V>[] tab; int sc;
     	// 自旋
        while ((tab = table) == null || tab.length == 0) {
            // sizeCtl < 0，礼让CPU
            if ((sc = sizeCtl) < 0)
                Thread.yield(); 
            // 比较设置SIZECTL，失败继续自旋
            else if (U.compareAndSwapInt(this, SIZECTL, sc, -1)) {
                try {
                    if ((tab = table) == null || tab.length == 0) {
                        int n = (sc > 0) ? sc : DEFAULT_CAPACITY;
                        @SuppressWarnings("unchecked")
                        Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n];
                        table = tab = nt;
                        // 0.75
                        sc = n - (n >>> 2);
                    }
                } finally {
                    sizeCtl = sc;
                }
                break;
            }
        }
        return tab;
    }
```

``sizeCtl``有两重含义

- 控制
  - ``-1``：正在进行初始化
  - ``-N``：``N-1``个线程正在扩容
- 容量
  - 未初始化：初始容量
  - 已初始化：扩容阈值

# ``putVal``

```java
    final V putVal(K key, V value, boolean onlyIfAbsent) {
        if (key == null || value == null) throw new NullPointerException();
        int hash = spread(key.hashCode());
        int binCount = 0;
        for (Node<K,V>[] tab = table;;) {
            Node<K,V> f; int n, i, fh;
            // 1. 初始化
            if (tab == null || (n = tab.length) == 0)
                tab = initTable();
            // 2. null，直接无锁设置
            else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
                // cas设置，避免冲突
                if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                    break;                   
            }
            // 3. 正在扩容，协助扩容
            else if ((fh = f.hash) == MOVED)
                tab = helpTransfer(tab, f);
            // 4. 加锁put
            else {
                V oldVal = null;
                synchronized (f) {
                    // 4.1 链表
                    if (tabAt(tab, i) == f) {
                        if (fh >= 0) {
                            binCount = 1;
                            for (Node<K,V> e = f;; ++binCount) {
                                K ek;
                                // 4.1.1 找到，替换
                                if (e.hash == hash &&
                                    ((ek = e.key) == key ||
                                     (ek != null && key.equals(ek)))) {
                                    oldVal = e.val;
                                    if (!onlyIfAbsent)
                                        e.val = value;
                                    break;
                                }
                                // 4.1.2 末尾，添加
                                Node<K,V> pred = e;
                                if ((e = e.next) == null) {
                                    pred.next = new Node<K,V>(hash, key,value, null);
                                    break;
                                }
                            }
                        }
                        // 4.2 红黑树
                        // TreeBin extends Node，但是hash < 0
                        else if (f instanceof TreeBin) {
                            Node<K,V> p;
                            binCount = 2;
                            if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key, value)) != null) {
                                oldVal = p.val;
                                if (!onlyIfAbsent)
                                    p.val = value;
                            }
                        }
                    }
                }
                // 5. 判断是否链转树
                if (binCount != 0) {
                    if (binCount >= TREEIFY_THRESHOLD)
                        treeifyBin(tab, i);
                    if (oldVal != null)
                        return oldVal;
                    break;
                }
            }
        }
        addCount(1L, binCount);
        return null;
    }
```

# ``get``

```java
 	public V get(Object key) {
        Node<K,V>[] tab; Node<K,V> e, p; int n, eh; K ek;
        // hash
        int h = spread(key.hashCode());
        // 1. 存在
        if ((tab = table) != null && (n = tab.length) > 0 &&
            (e = tabAt(tab, (n - 1) & h)) != null) {
            // 1.1 链表头即结果
            if ((eh = e.hash) == h) {
                if ((ek = e.key) == key || (ek != null && key.equals(ek)))
                    return e.val;
            }
            // 1.2 红黑树或者正在扩容，find查找
            else if (eh < 0)
                return (p = e.find(h, key)) != null ? p.val : null;
            // 1.3 链表查找
            while ((e = e.next) != null) {
                if (e.hash == h &&
                    ((ek = e.key) == key || (ek != null && key.equals(ek))))
                    return e.val;
            }
        }
        return null;
    }
```

# 扩容

## ``sizeCtl``

- 扩容

**扩容前**

```java
int rs = resizeStamp(n)
U.compareAndSwapInt(this, SIZECTL, sc,(rs << RESIZE_STAMP_SHIFT) + 2);
// sizeCtl = resizeStamp(n) << RESIZE_STAMP_SHIFT + 2
```

**辅助扩容**

```java
U.compareAndSwapInt(this, SIZECTL, sc, sc + 1)
// sizeCtl = sizeCtl + 1
```

- 线程扩容

**辅助扩容**

```java
U.compareAndSwapInt(this, SIZECTL, sc = sizeCtl, sc - 1);
// sizeCtl = sizeCtl - 1
```

**最后扩容**

```java
(sc - 2) == resizeStamp(n) << RESIZE_STAMP_SHIFT;
// 恢复 sizeCtl = resizeStamp(n) << RESIZE_STAMP_SHIFT + 2
```

## 标记

- 类型标记

| hash    | 类型                         |
| ------- | ---------------------------- |
| ``>=0`` | 链表                         |
| ``-1``  | ``MOVED``,``ForwardingNode`` |
| 其他    | 红黑树                       |

- 迁移标记
  1. 节点实现``find``方法
     1. 链表直接查询
     2. 红黑树使用``find``
  2. ``ForwardingNode``包装``nextTable``，同时实现``find``方法
     1. 未迁移前，``table``不包含``fwd``
     2. 单桶迁移完成，替换为``fwd``，查询``nextTable``
     3. ``table``全部都是``fwd``，表示迁移完成

## 下标

前面说通过高位即可判断，现在书面梳理一下：原始长度``n``，扩容长度为``m``，下标为``i``，``h``表示哈希

扩容前下标：``i_n = h & (n - 1)``

扩容后下标：``i_m = h & (m - 1)``

关系式：``i_m = i_n + (h & n)``

> 经常说高位判断有些抽象，但是举个例子就能体会了
>
> ```text
> 3 % 2 = 1
> 3 % 4 = 3
> 
> 5 % 2 = 1
> 5 % 4 = 1
> ```
>
> 对于小的模长，有些数字被再次折半了，当模长翻倍，这部分数据应该恢复，长度刚好为小模长。
>
> 而对于另一部分数据，直接投射到小模长范围，无需操作。

## 源码阅读

```java
	private final void transfer(Node<K,V>[] tab, Node<K,V>[] nextTab) {
        int n = tab.length, stride;
        // 1. 单线程扩容数据量，多线程下，保证每个CPU最小任务量为16
        if ((stride = (NCPU > 1) ? (n >>> 3) / NCPU : n) < MIN_TRANSFER_STRIDE)
            stride = MIN_TRANSFER_STRIDE; 
    	// 2. 扩容数组初始化
        if (nextTab == null) {            // initiating
            try {
                @SuppressWarnings("unchecked")
                Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n << 1];
                nextTab = nt;
            } catch (Throwable ex) {      // try to cope with OOME
                sizeCtl = Integer.MAX_VALUE;
                return;
            }
            nextTable = nextTab;
            // 倒计
            transferIndex = n;
        }
        int nextn = nextTab.length;
        /**
        	ForwardingNode(Node<K,V>[] tab) {
            	super(MOVED, null, null, null);
            	this.nextTable = tab;
        	}
        */
        // 3. 数据标识
        // 		3.1 扩容表节点
        ForwardingNode<K,V> fwd = new ForwardingNode<K,V>(nextTab);
        // 		3.2 是否进行继续扩容
        boolean advance = true;
        // 		3.3 扩容操作是否完成
        boolean finishing = false; 
		// 4. 自旋扩容(槽) [nextIndex - stride, nextIndex - 1] = [bound, i]
        for (int i = 0, bound = 0;;) {
            Node<K,V> f; int fh;
            // 4.1. 任务分配
            while (advance) {
                int nextIndex, nextBound;
                // 4.1.1 当前分配的槽已经迁移完毕，或者整体扩容已经迁移完毕
                if (--i >= bound || finishing)
                    advance = false;
                // 4.1.2 全部的槽已经迁移完毕，表明该线程helptransfer但实际上已经迁移完毕
                else if ((nextIndex = transferIndex) <= 0) {
                    i = -1;
                    advance = false;
                }
                // 4.1.3 cas分配槽任务 [nextIndex - stride, nextIndex - 1] = [bound, i]
                else if (U.compareAndSwapInt
                         (this, TRANSFERINDEX, nextIndex,
                          nextBound = (nextIndex > stride ?
                                       nextIndex - stride : 0))) {
                    // nextIndex - stride
                    bound = nextBound;
                    // nextIndex - 1
                    i = nextIndex - 1;
                    advance = false;
                }
            }
            // 5. 多场景扩容
            // 	5.1 扩容完毕
            if (i < 0 || i >= n || i + n >= nextn) {
                int sc;
                // 5.1.1 全体扩容完毕
                if (finishing) {
                    nextTable = null;
                    table = nextTab;
                    // 0.75
                    sizeCtl = (n << 1) - (n >>> 1);
                    return;
                }
                // 5.1.2 当前扩容完毕
                if (U.compareAndSwapInt(this, SIZECTL, sc = sizeCtl, sc - 1)) {
                    // 5.1.2.1 辅助扩容完毕，退出
                    if ((sc - 2) != resizeStamp(n) << RESIZE_STAMP_SHIFT)
                        return;
                    // 5.1.2.2 最后扩容，更新变量，下次循环检查退出
                    finishing = advance = true;
                    i = n; 
                }
            }
            // 5.2 空节点，直接替换fwd
            else if ((f = tabAt(tab, i)) == null)
                advance = casTabAt(tab, i, null, fwd);
            // 5.3 已经是fwd，当前bin扩容完毕，被其他线程扩容
            else if ((fh = f.hash) == MOVED)
                advance = true; 
            // 5.4 具体扩容操作
            else {
                synchronized (f) {
                    if (tabAt(tab, i) == f) {
                        Node<K,V> ln, hn;
                        // 链表
                        if (fh >= 0) {
                            int runBit = fh & n;
                            Node<K,V> lastRun = f;
                            for (Node<K,V> p = f.next; p != null; p = p.next) {
                                int b = p.hash & n;
                                if (b != runBit) {
                                    runBit = b;
                                    lastRun = p;
                                }
                            }
                            if (runBit == 0) {
                                ln = lastRun;
                                hn = null;
                            }
                            else {
                                hn = lastRun;
                                ln = null;
                            }
                            for (Node<K,V> p = f; p != lastRun; p = p.next) {
                                int ph = p.hash; K pk = p.key; V pv = p.val;
                                // 头插法，会倒序
                                if ((ph & n) == 0)
                                    ln = new Node<K,V>(ph, pk, pv, ln);
                                else
                                    hn = new Node<K,V>(ph, pk, pv, hn);
                            }
                            // nextTable数据迁移
                            setTabAt(nextTab, i, ln);
                            setTabAt(nextTab, i + n, hn);
                            // table(i) 设置fwd
                            setTabAt(tab, i, fwd);
                            advance = true;
                        }
                        // 红黑树
                        else if (f instanceof TreeBin) {
                            TreeBin<K,V> t = (TreeBin<K,V>)f;
                            TreeNode<K,V> lo = null, loTail = null;
                            TreeNode<K,V> hi = null, hiTail = null;
                            int lc = 0, hc = 0;
                            for (Node<K,V> e = t.first; e != null; e = e.next) {
                                int h = e.hash;
                                TreeNode<K,V> p = new TreeNode<K,V>
                                    (h, e.key, e.val, null, null);
                                if ((h & n) == 0) {
                                    if ((p.prev = loTail) == null)
                                        lo = p;
                                    else
                                        loTail.next = p;
                                    loTail = p;
                                    ++lc;
                                }
                                else {
                                    if ((p.prev = hiTail) == null)
                                        hi = p;
                                    else
                                        hiTail.next = p;
                                    hiTail = p;
                                    ++hc;
                                }
                            }
                            ln = (lc <= UNTREEIFY_THRESHOLD) ? untreeify(lo) :
                                (hc != 0) ? new TreeBin<K,V>(lo) : t;
                            hn = (hc <= UNTREEIFY_THRESHOLD) ? untreeify(hi) :
                                (lc != 0) ? new TreeBin<K,V>(hi) : t;
                            // nextTable数据迁移
                            setTabAt(nextTab, i, ln);
                            setTabAt(nextTab, i + n, hn);
                            // table(i) 设置fwd
                            setTabAt(tab, i, fwd);
                            advance = true;
                        }
                    }
                }
            }
        }
    }

```

## 辅助扩容

```java
    // 辅助扩容
	final Node<K,V>[] helpTransfer(Node<K,V>[] tab, Node<K,V> f) {
        Node<K,V>[] nextTab; int sc;
        // 1. 扩容状态判断
        if (tab != null && (f instanceof ForwardingNode) &&
            (nextTab = ((ForwardingNode<K,V>)f).nextTable) != null) {
            int rs = resizeStamp(tab.length);
            // 2 自旋扩容检测
            while (nextTab == nextTable && table == tab &&
                   (sc = sizeCtl) < 0) {
                // 3.1 扩容完毕，退出
                if ((sc >>> RESIZE_STAMP_SHIFT) != rs || sc == rs + 1 ||
                    sc == rs + MAX_RESIZERS || transferIndex <= 0)
                    break;
                // 3.2 扩容中，辅助扩容
                if (U.compareAndSwapInt(this, SIZECTL, sc, sc + 1)) {
                    transfer(tab, nextTab);
                    break;
                }
            }
            return nextTab;
        }
        return table;
    }
```

# 容量计算

- ``size``

```java
    public int size() {
        long n = sumCount();
        return ((n < 0L) ? 0 :
                (n > (long)Integer.MAX_VALUE) ? Integer.MAX_VALUE :
                (int)n);
    }
```

- ``sumCount``

```java
    // baseCount + sum(counterCell)
	final long sumCount() {
        CounterCell[] as = counterCells; CounterCell a;
        long sum = baseCount;
        if (as != null) {
            for (int i = 0; i < as.length; ++i) {
                if ((a = as[i]) != null)
                    sum += a.value;
            }
        }
        return sum;
    }
```

- ``addCount``

```java
    // putVal最后调用
	private final void addCount(long x, int check) {
        CounterCell[] as; long b, s;
        // 1. 元素统计
        if ((as = counterCells) != null ||
            // 1.1 尝试 baseCount += 1
            !U.compareAndSwapLong(this, BASECOUNT, b = baseCount, s = b + x)) {
            CounterCell a; long v; int m;
            boolean uncontended = true;
            if (as == null || (m = as.length - 1) < 0 ||
                (a = as[ThreadLocalRandom.getProbe() & m]) == null ||
                // 1.2 baseCount更新失败，尝试更新到counterCells
                !(uncontended =U.compareAndSwapLong(a, CELLVALUE, v = a.value, v + x))) {
                // 1.3 以上两者更新失败，陷入自旋更新
                fullAddCount(x, uncontended);
                return;
            }
            if (check <= 1)
                return;
            s = sumCount();
        }
        // 2. 结果校验
        if (check >= 0) {
            Node<K,V>[] tab, nt; int n, sc;
            // 结果不对，说明有扩容操作，先扩容
            while (s >= (long)(sc = sizeCtl) && (tab = table) != null &&
                   (n = tab.length) < MAXIMUM_CAPACITY) {
                int rs = resizeStamp(n);
                // 2.1 正在扩容
                if (sc < 0) {
                    // 2.1.1 扩容完毕
                    if ((sc >>> RESIZE_STAMP_SHIFT) != rs || sc == rs + 1 ||
                        sc == rs + MAX_RESIZERS || (nt = nextTable) == null ||
                        transferIndex <= 0)
                        break;
                    // 2.1.2 协助扩容 sizeCtl += 1
                    if (U.compareAndSwapInt(this, SIZECTL, sc, sc + 1))
                        transfer(tab, nt);
                }
                // 2.2 自身发起的扩容， sizeCtl = resizeStamp(n) << RESIZE_STAMP_SHIFT + 2
                else if (U.compareAndSwapInt(this, SIZECTL, sc,
                                             (rs << RESIZE_STAMP_SHIFT) + 2))
                    transfer(tab, null);
                s = sumCount();
            }
        }
    }
```

# 版本对比

|          | 1.7                                                          | 1.8                                                          |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 组件     | ``Segment + HashEntry + Unsafe``                             | ``Synchronized + CAS + Node + Unsafe``                       |
| 初始化   | 加锁                                                         | ``sizeCtl = -1``                                             |
| ``put``  | 1. 位置锁定``segment + table``<br />2. 自旋取锁<br />3. 超过``64``次自旋挂起等锁 | 1. 锁定位置``table[i]``<br />2. ``f == null``，直接设置<br />3. ``f.hash == -1``，协助扩容<br />4. ``hash != -1`` ，锁住，判断链表或红黑树，设置 |
| ``get``  | ``volatile``保证写优先读                                     | ``volatile``保证写优先读                                     |
| 扩容     | 1. 单线程扩容<br />2. 步骤同``hashMap``                      | 1. 多线程辅助扩容<br />2. ``ForwardingNode ``标识<br />3. ``sizeCtl``标识 |
| ``size`` | 1. 不加锁，计算两次，相同则返回，否则冲突<br />2. 冲突情况，全锁``segment``再统计 | 1. 基础计数``baseCount``，冲突计数``counterCells``<br />2. 设置失败自旋等待设置<br />3. 校验数据、辅助扩容 |

