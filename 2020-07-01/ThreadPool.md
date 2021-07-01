# 控制字段

```java
    // 高三位为状态控制，后续位置为线程数量控制
	private final AtomicInteger ctl = new AtomicInteger(ctlOf(RUNNING, 0));
	// 不同CPU位数不一
    private static final int COUNT_BITS = Integer.SIZE - 3;
	// 低位全满，最大线程容量
    private static final int CAPACITY   = (1 << COUNT_BITS) - 1;

	// 高三位
    private static final int RUNNING    = -1 << COUNT_BITS; // 111
    private static final int SHUTDOWN   =  0 << COUNT_BITS; // 000
    private static final int STOP       =  1 << COUNT_BITS; // 001
    private static final int TIDYING    =  2 << COUNT_BITS; // 010
    private static final int TERMINATED =  3 << COUNT_BITS; // 011
```

| STATUS         | BITS    | ACTION                                   |
| -------------- | ------- | ---------------------------------------- |
| ``RUNNING``    | ``111`` | 接收新任务， 处理队列任务                |
| ``SHUTDOWN``   | ``000`` | 拒绝新任务，处理队列任务                 |
| ``STOP``       | ``001`` | 拒绝新任务，丢弃队列任务，中断执行中任务 |
| ``TIDYING``    | ``010`` | 任务全完成，活跃线程为0                  |
| ``TERMINATED`` | ``011`` | 终止状态，``terminated``完成后状态       |

# 任务提交

```java
    public void execute(Runnable command) {
        // 1. 空任务，报错
        if (command == null)
            throw new NullPointerException();
        int c = ctl.get();
        // 2. 低于corePoolSize， 新建线程池
        if (workerCountOf(c) < corePoolSize) {
            if (addWorker(command, true))
                return;
            c = ctl.get();
        }
        // 3. 运行中，添加到任务队列
        if (isRunning(c) && workQueue.offer(command)) {
            int recheck = ctl.get();
            // 3.1 二次检查，非运行中移除任务，执行拒绝
            if (! isRunning(recheck) && remove(command))
                reject(command);
            // 3.2 如果没有线程，新建线程
            else if (workerCountOf(recheck) == 0)
                addWorker(null, false);
        }
        // 4. 队列已满，增加线程，失败则拒绝
        else if (!addWorker(command, false))
            reject(command);
    }
```

# 增加线程

```java
    
	private boolean addWorker(Runnable firstTask, boolean core) {
        retry:
        for (;;) {
            int c = ctl.get();
            int rs = runStateOf(c);
			// 1. 特殊情况队列非空校验
            if (rs >= SHUTDOWN && !(rs == SHUTDOWN && firstTask == null && ! workQueue.isEmpty()))
                return false;
			// 2. 自旋计数
            for (;;) {
                int wc = workerCountOf(c);
                // 2.1 超容量限制
                if (wc >= CAPACITY || wc >= (core ? corePoolSize : maximumPoolSize))
                    return false;
                // 2.2 CAS,成功跳出
                if (compareAndIncrementWorkerCount(c))
                    break retry;
                c = ctl.get();  
                // 2.3 不相等，走最外层逻辑自旋
                if (runStateOf(c) != rs)
                    continue retry;
            }
        }

        boolean workerStarted = false;
        boolean workerAdded = false;
        Worker w = null;
        // 3. 新建线程
        try {
            // 3.1 新建线程
            w = new Worker(firstTask);
            final Thread t = w.thread;
            if (t != null) {
                final ReentrantLock mainLock = this.mainLock;
                mainLock.lock();
                try {
                    int rs = runStateOf(ctl.get());
					// 3.2 状态校验
                    if (rs < SHUTDOWN || (rs == SHUTDOWN && firstTask == null)) {
                        // 3.2.1 非法线程状态
                        if (t.isAlive()) throw new IllegalThreadStateException();
                        // 3.2.2 队列状态维护
                        workers.add(w);
                        int s = workers.size();
                        if (s > largestPoolSize) largestPoolSize = s;
                        workerAdded = true;
                    }
                } finally {
                    mainLock.unlock();
                }
                // 3.2 添加成功，启动线程
                if (workerAdded) {
                    t.start();
                    workerStarted = true;
                }
            }
        } finally {
            // 3.3 状态校验，收尾
            if (! workerStarted)
                addWorkerFailed(w);
        }
        return workerStarted;
    }
```

# 任务管理

```java
        Worker(Runnable firstTask) {
            setState(-1); // inhibit interrupts until runWorker
            this.firstTask = firstTask;
            this.thread = getThreadFactory().newThread(this);
        }
```

- ``run``

```java
        public void run() {
            runWorker(this);
        }
```

- ``runWorker``

```java
    final void runWorker(Worker w) {
        Thread wt = Thread.currentThread();
        Runnable task = w.firstTask;
        w.firstTask = null;
        w.unlock(); 
        boolean completedAbruptly = true;
        try {
            // 1. 获取任务
            while (task != null || (task = getTask()) != null) {
                w.lock();
                if ((runStateAtLeast(ctl.get(), STOP) ||
                     (Thread.interrupted() &&
                      runStateAtLeast(ctl.get(), STOP))) &&
                    !wt.isInterrupted())
                    wt.interrupt();
                try {
                    // 2. 执行任务
                    // 2.1 执行前
                    beforeExecute(wt, task);
                    Throwable thrown = null;
                    try {
                        // 2.2 执行任务
                        task.run();
                    } catch (RuntimeException x) {
                        thrown = x; throw x;
                    } catch (Error x) {
                        thrown = x; throw x;
                    } catch (Throwable x) {
                        thrown = x; throw new Error(x);
                    } finally {
                        // 2.3 执行后
                        afterExecute(task, thrown);
                    }
                } finally {
                    // 3. 统计完统计
                    task = null;
                    w.completedTasks++;
                    w.unlock();
                }
            }
            completedAbruptly = false;
            // 4. 任务执行完毕
        } finally {
            processWorkerExit(w, completedAbruptly);
        }
    }
```

# 任务获取

```java
    private Runnable getTask() {
        boolean timedOut = false; 
        for (;;) {
            int c = ctl.get();
            int rs = runStateOf(c);
            // 1. 状态校验
            if (rs >= SHUTDOWN && (rs >= STOP || workQueue.isEmpty())) {
                decrementWorkerCount();
                return null;
            }
            int wc = workerCountOf(c);
            // 2. 是否允许超时
            boolean timed = allowCoreThreadTimeOut || wc > corePoolSize;
			// 3. 条件退出
            // 3.1 线程数量超过最大值
            // 3.2 允许超时且超时了
            // 3.3 非最后一条线程
            // 3.4 队列为空
            if ((wc > maximumPoolSize || (timed && timedOut)) 
                && (wc > 1 || workQueue.isEmpty())) {
                // 3.5 状态校验，改变则需要重新判断
                if (compareAndDecrementWorkerCount(c)) 
                    return null;
                continue;
            }

            try {
                // 获取任务
                Runnable r = timed ?  workQueue.poll(keepAliveTime, TimeUnit.NANOSECONDS) :workQueue.take();
                if (r != null)
                    return r;
                timedOut = true;
            } catch (InterruptedException retry) {
                timedOut = false;
            }
        }
    }
```

# 执行完毕

```java
    private void processWorkerExit(Worker w, boolean completedAbruptly) {
        if (completedAbruptly) 
            decrementWorkerCount();

        final ReentrantLock mainLock = this.mainLock;
        mainLock.lock();
        // 1. 移除自身
        try {
            completedTaskCount += w.completedTasks;
            workers.remove(w);
        } finally {
            mainLock.unlock();
        }
		// 2. 尝试停止
        tryTerminate();
        int c = ctl.get();
        // 3. 未STOP， 继续处理队列任务
        if (runStateLessThan(c, STOP)) {
            if (!completedAbruptly) {
                int min = allowCoreThreadTimeOut ? 0 : corePoolSize;
                if (min == 0 && ! workQueue.isEmpty())
                    min = 1;
                // 3.1 最低核心线程数
                if (workerCountOf(c) >= min)
                    return; 
            }
            // 4. 异常情况补偿核心线程
            addWorker(null, false);
        }
    }
```

