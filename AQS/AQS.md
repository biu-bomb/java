# AQS

| field     | type     | description |
| --------- | -------- | ----------- |
| ``state`` | ``int``  | 锁状态      |
| ``head``  | ``Node`` | 队头        |
| ``tail``  | ``Node`` | 队尾        |

# 入队

## 直接入队

```java
    private Node addWaiter(Node mode) {
        Node node = new Node(Thread.currentThread(), mode);
        // 直接入队，成功返回
        Node pred = tail;
        if (pred != null) {
            node.prev = pred;
            if (compareAndSetTail(pred, node)) {
                pred.next = node;
                return node;
            }
        }
        // 直接入队失败，自旋入队
        enq(node);
        return node;
    }
```

## 自旋入队

```java
    private Node enq(final Node node) {
        // 自旋
        for (;;) {
            Node t = tail;
            if (t == null) { // 懒加载
                if (compareAndSetHead(new Node()))
                    tail = head;
            } else {
                // 直接设置
                node.prev = t;
                // 并发情况下自旋，防止中途有插入
                if (compareAndSetTail(t, node)) {
                    t.next = node;
                    return t;
                }
            }
        }
    }
```

# 锁定

## 核心逻辑

```java
    final boolean acquireQueued(final Node node, int arg) {
        boolean failed = true;
        try {
            boolean interrupted = false;
            for (;;) {
                final Node p = node.predecessor();
                // 如果获取锁成功
                if (p == head && tryAcquire(arg)) {
                    // 设置为头结点
                    setHead(node);
                    p.next = null; // help GC
                    failed = false;
                    return interrupted;
                }
                // 如果是中断唤醒的，活跃之后补充中断
                if (shouldParkAfterFailedAcquire(p, node) &&
                    parkAndCheckInterrupt())
                    interrupted = true;
            }
        } finally {
            if (failed)
                cancelAcquire(node);
        }
    }
```

| 唤醒条件      | 操作逻辑                                              |
| ------------- | ----------------------------------------------------- |
| ``unpark``    | 执行逻辑                                              |
| ``interrupt`` | 重新休眠，<font color='red'>如有必要，补充中断</font> |

