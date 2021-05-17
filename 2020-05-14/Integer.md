# 自动装箱

```java
    public static Integer valueOf(int i) {
        return i >= -128 && i <= Integer.IntegerCache.high ? Integer.IntegerCache.cache[i + 128] : new Integer(i);
    }
```

# 自动拆箱

```java
    public int intValue() {
        return this.value;
    }
```

