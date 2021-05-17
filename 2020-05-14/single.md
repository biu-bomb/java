# 懒汉

```java
class Single {
    public static Single INSTANCE;
    // 懒加载，需要时创建
    public static synchronized Single getInstance(){
        if(INSTANCE == null){
            INSTANCE = new Single();
        } 
        return INSTANCE;
    }
}

class Single {
    public static Single INSTANCE;
    // 懒加载，需要时创建
    public static Single getInstance(){
        if(INSTANCE == null){
            synchronized {
              if (INSTANCE == null){
                 INSTANCE = new Single();
              }
            }
        } 
        return INSTANCE;
    }
}
```

# 饿汉

```java
class Single{
    public final static Single INSTANCE = new Single();
    
    public static getInstance(){
        return INSTANCE;
    }
}

class Single{
    public final static Single INSTANCE;
    
    static{
        INSTANCE = new Single():
    }
    
    public static Single getInstance(){
        return INSTANCE;
    }
}
```

# 内部类

```java
class Single {
  class SingleInstanceHolder{
    public static final Single INSTANCE = new Single();
  }
  
  public static Single getInstance{
    return SingleInstanceHolder.INSTANCE;
  }
}
```

