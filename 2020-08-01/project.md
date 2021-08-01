# 课表聚合

## 功能描述

对接到课程中心、商品、权益、课件、课程信息等服务，完成多种信息聚合操作，为客户端提供统一的展示数据。

## 面临问题

服务本身处理耗时严重，线上出现OOM，并且无容灾方案，紧急扩容后勉强规避问题，但是问题请求无法挽回。

三个目标

- 排查清楚OOM原因并解决
- 提供容灾手段
- 提升服务处理性能

## 问题排查

### OOM排查过程

通过监控查看GC情况发现

- 新生代对象稳定创建，没有瞬时增加的异常情况
- 老年代对象逐步上升
- 频繁GC并没有回收更多内存
- 内存逐渐消耗最终导致OOM

> 初步怀疑程序内部出现内存泄漏，伴随每次请求积累，可用内存逐渐耗尽。

通过CAT查看，单机请求在高峰时段一小时内访问次数约7w，分布比较均匀，无异常激增情况。

平均处理耗时约400ms，最大耗时达到1800s；对比多个时间区间，处理耗时逐渐延长。

> 相同数量的请求，处理耗时逐渐增加，程序内应该伴随着任务的堆积。有可能由于这部分的堆积导致内存泄漏。

通过查看提交记录，当前版本变更有两个修改

- 基础业务需求
- 异步优化(使用CompleteableFuture对每次请求进行异步处理，超时时间20s)

> 怀疑任务处理过程中，由于某些原因导致任务失败，或者处理较慢。
>
> 超时时间过长，没有及时熔断，导致线程池任务不断堆积。

快照没有及时保存，接手时候无可分析工具。

使用运维部门提供的自定义埋点工具，搭建监控大盘；压测后验证存在堆积现象。

### 处理耗时

提交到线程池的任务是一个聚合任务，涉及多个系统的调用聚合。

初步分析，存在如下问题

- 逻辑混杂，无分明业务边界
- 串行处理，有些不相干的聚合串行执行，极大延长了处理时间
- 同步加载，资源处理上，同步进行远程获取，服务耗时极大的依赖下游接口
- 缓存分散，对于单一用户，缓存分散存储，每次单独查询缓存，增加查询消耗

### 熔断机制

当前服务没有具体的限流方案，基础架构提供的sentinel组件存在问题，目前不能够直接使用。

对于课表的全部聚合信息，业务优先级不一，经协商后确认业务需求如下

- 最基本要保证核心链路的功能完整
- 对于其他额外功能模块，能够进行插件式的热插拔
- 并且能够提供多种容灾策略的快速切换

## 方案构思

- 解决OOM
  - 严格控制任务生命时长，能够完成快速处理，避免任务堆积
- 业务隔离
  - 拆分处理模块，严格按照不同业务领域进行划分，并提供插拔功能
- 资源加速
  - 将资源加载异步化处理，降低不同业务处理之间的阻塞时间
  - 变更缓存结构，将离散化缓存收拢，或者使用mget进行批量缓存查询，提升缓存查询效率
  - 使用内存保存缓存副本，降低加快处理性能

## 方案实施

整体结构采用责任链处理模式，统一接口形式为

```java
class interfact ResourceRequestHandler {
  // 通过外部配置控制该处理节点是否生效
  boolean processSwitch();
  // 业务处理，节点间的资源依赖使用ResourceContext进行传递
  void process(ResourceRequest request, ResourceResponse response, ResourceContext context);
  // 节点名称
  String name();
}
```

节点生效策略控制

```java
class HandlerStrategy{
  final static DEFAULT_STRATEGY = "DEFAULT";
  public Map<String, Map<String, Boolean>> strategy; 
  public String enableStrategy;
  
  public Map<String, Boolean> switchOn(String handlerName){
    if(enableStrategy == null || !strategy.containsKey(enableSrategy)){
      enableStrategy = DEFAULT_STRATEGY;
    }
    return strategy.getOrDefault(enableStrategy, true);
  }
}
```

处理节点的统一抽象父类

```java
class abstract class AbstractResourceRequestHandler implements ResourceRequestHandler {
  HandlerStrategy strategy;
  // 返回控制开关配置
  boolean SwitchOn(){
   	return strategy.switchOn(name); 
  }
  
  // 用于子类资源依赖条件判断，如果前置条件检查判断不过，则不执行
  protected boolean executable(ResouceRequest request, ResourceResponse response, ResourceContext context){
    return true;
  }
  
  // 具体处理逻辑
  abstract void doProcess(ResourceRequest request, ResourceResponse response, ResourceContext context);
  
  // 处理逻辑
  public void process(ResourceRequest request, ResourceResponse response, ResourceContext context){
    if(switchOn() && executable(request, response, context)){
      doProcess(request, response, context);
    }
  } 
}
```

``ResourceContext``中属于资源注册表，一般使用资源注册工具进行异步资源加载

```java
class final ResourceLoader {
  Executor executor;
  Integer timeout;
  
  
  class ResourceSupplier implements Supplier{
    
    Future future;
    Object result;
    boolean finished;
    
    public ResourceSupplier(String resourceName, Supplier supplier){
      // RequestContextHolder.getXXX
      future = CompleteFuture.supplierAsync(()->{
        // RequestContentHolder.set(XXX);
        Object result = supplier.get()
        // RequestContextHolder.removeXXX
      }, executor);
    }
    
    public Object get(){
      if(!finshed){
        result = future.get(timeout, TimeUnit.MILLISECOND);
      }
      return result;
    } 
  }
}
class ResourceContext {
  
  Map<String, Supplier> resources = new HashMap<>();
  
  public void register(String resourceName, Object resource){
    if(resource == null) return ;
    if(resource instances of Supplier){
      resources.put(resourceName, (Supplier) resource);
    } else {
      resource.put(resourceName, ()-> resource);
    }
  }
  
  public T <T> findResource(String resourceName){
    if(!resources.containsKey(resourceName)) return null;
   	return (T)(resources.get(resourceName));
  }
}
```

## 方案效果

- 采用责任链完成处理，开关可控，紧急时刻通过策略切换能够熔断问题节点，保证核心链路功能畅通
- 责任链节点业务内聚，发现遗留业务逻辑，剔除无用业务逻辑和重复处理，直接提升了20%处理效率。
- 资源级别异步加载
  - 加载超时控制达到单资源级别，有效控制任务生命时长
  - 有效的异步无依赖关系的资源加载，降低资源加载间阻塞时间
  - ``executable``检测通过``context.getResource``阻塞，衔接资源依赖的不同节点处理
- 缓存批量存储+内存筛查，提升缓存查询消耗

单次请求耗时由400ms降低至100ms左右，并且最大、最小耗时明显下降。

抖动误差由原来的200ms降低至20ms，提升请求处理的稳定性。

从监控面案上，也能够对每个节点的处理耗时、调用次数有直观显示。