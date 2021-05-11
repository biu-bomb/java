# 基础属性
```java
public final class String implements java.io.Serializable, Comparable<String>, CharSequence {
    private final char value[];
	...
}
```

- 不可继承
  - 因为``class``使用``final``修饰
- 不可变
  - 具体存储采用``char[]``，使用``final``进行修饰，内容无法更改

# 类型和分布

| 类型              | 例子                               | 存储区域     |
| ----------------- | ---------------------------------- | ------------ |
| 字面量/字符串常量 | ``String s = "hello"``             | 字符串常量池 |
| 字符串对象        | ``String s = new String("hello")`` | 堆           |

## 字符串常量池

字符串常量池中存储了程序中的全部字符串常量，并为每一个字符串常量维持强引用，不必担心被垃圾回收。

直接使用字符串字面量时

1. 字符串常量池中存在该字面量，返回字符串常量池中的引用
2. 将该字面量放入字符串常量池，引用指向字符串常量池对象

```java
public static void main(String[] args){
    String a = "hello";
    String b = "hello";
    System.out.println(a == b); // true
}
```

因为引用的都是字符串常量池中的同一个对象。

## 堆空间

如果使用的不是字面量，而是直接创建的对象，每次创建的对象维护自身的引用。

```java
public static void main(String[] args){
    String a = new String("abc");
    String b = new String("abc");
    System.out.println(a == b); // false
}
```

# 对象操作

## 相等判断

不论是字面量还是字符串对象，对于``equals``，他们比对的都是``char[]``内容是否相等，而不是``==``物理相等。

```java
public static void main(String[] args){
    String a = "abc";
    String b = new String("abc");
    String c = new String("abc");
    
    System.out.println(b == c); // false
    System.out.println(a.equals(b) && b.equals(c)); // true
}
```

## 对象常量

```java
public static void main(String args){
    String a = new String("abc");
    a.intern();
}
```

对于一个字符串对象，使用``intern``能够在字符串常量池中维护一个相同的字面量。

> <font color='red'>问题是只有特殊创建的才需要如此，否则``new String("abc")``语句中的字面量已经被记录在了字符串常量池中。</font>

## 特殊拼接

``java``提供``+``直接进行字符串的拼接

```java
public static void main(String[] args){
    String a = "A" + "B";
    String b = a + new String("C");
}
```

这种拼接存在两种情况

- 纯常量拼接
  - 该情况下，编译期完成操作，并将拼接字符放入字符串常量池
- 杂对象拼接
  - 创建``StringBuilder``进行字符串的拼接操作。

```java
public static void main(String[] args){
    String a = "A" + "B"; // 编译时期自动完成，编译代码 String a = "AB";
    String b = a + new String("C";)
    // (new StringBuuilder()).append(a).append(new String("C")).toString();
    String c = "A" + getStr();
    System.out.println(a == c); // false，方法调用，编译期间不能直接完成拼接，转成了String对象
}

public String getStr(){
    return "B";
}
```

# 简单测验

```java
// 创建了几个对象
public static void main(String[] args){
    String a = new String("A" + "B");
    String b = new String("C") + new String("C"); 
}
```

==a==

| operation            | count  | description      |
| -------------------- | ------ | ---------------- |
| ``A``                | ``+1`` | ``A``字面量      |
| ``B``                | ``+1`` | ``B``字面量      |
| ``AB``               | ``+1`` | 拼接``AB``字面量 |
| ``new String("AB")`` | ``+1`` | 创建对象         |
| ``String a``         | ``+1`` | 对象引用         |

==b==

| operation           | count  | description  |
| ------------------- | ------ | ------------ |
| ``C``               | ``+1`` | ``C``字面量  |
| ``new String("C")`` | ``+2`` | 两次创建操作 |
| ``+``               | ``+1`` | 拼接转换对象 |
| ``String b``        | ``+1`` | 对象引用     |

