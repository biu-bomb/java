# 相等判断

> - 世界上没有完全相同的两片树叶
> - 一个人不可能两次踏入同一条河流

判断一个对象和另一个对象是否相等，一般来说有两种概念

- 物理相等：两个对象都是同一个本体，自身等于自身
- 逻辑相等：两个对象指定属性逻辑运算相等
  - 不同对象可以逻辑相等
  - 同一本体可以逻辑不等

在``JAVA``中的基本比较方式

| operation  | type     | description                  |
| ---------- | -------- | ---------------------------- |
| ``==``     | 物理相等 | 比较对象内存地址判断是否相等 |
| ``equals`` | 逻辑相等 | 默认情况下``==``，可重定义   |

# 哈希容器

## 基础方法

基础的``hashCode``是底层自动生成的，我们可以将其视为一种逻辑相等

```python
def equals(obj1, obj2):
    return obj1.hashCode == obj2.hashCode
```

但是，``hashCode``并不一定是直接的内存地址，受限于算法和硬件，两个既物理不相等，也逻辑不相等的对象的``hashCode``也可能碰撞。

## 容器管理

```python
container = {}
size = 10
def get(key):
    container[key.hashCode % size][key]
    
def put(key, val):
    container[key.hashCode % size] = container.get(key.hashCode % size, []) + [{key:val}]
```

各种受限，我们总需要在一个列表中检索一个特定的数据，也就是==相等检测==

# 检测等级

- 单一数据：列表中仅有一个数据，无需进行检测

- 不同哈希：直接比对``hashCode``，唯一相等返回

- 相同哈希：受限于各种条件，原生``hash``碰撞，进行``equals``检查
- 逻辑相等：唯一``equals``相等，返回唯一数据

> - <font color='red'>严格相等：是否同一个对象</font>

``Java``容器本就是基于==逻辑相等==进行的数据管理，因此不存在==严格相等==的场景。

## ``hashCode``不等

```java
class S{
    Random random = new Random();
    public int hashCode(){
        return random.nextInt(Integer.MAX_VALUE);
    }
    public boolean equals(Object obj){
        return true;
    }
    public static void main(String[] args){
        Set<S> set = new HashSet<>();
        S s = new S();
        set.add(s); // size = 1
        set.add(s); // size = 2
    }
}
```
## ``hashCode``相等

```java
class S{
    public int hashCode(){
        return 3;
    }
    public boolean equals(Object obj){
        return false;
    }
    public static void main(String[] args){
        Set<S> set = new HashSet<>();
        S s = new S();
        set.add(s); // size = 1
        set.add(s); // size = 2
    }
}
```

# 关系维护

如果``equals``相等，我们至少得让数据走到同一个列表中去，需要保证``hashCode``的一致性。

> <font color='red'>对于``equals``相等的对象，``hashCode``必须相等，否则``equals``会完全被``hashCode``阻断。</font>

因此，对于可能使用``hash``容器的情况下，需要进行层级相等关系的维护工作。