# 代理

```java
public class A {

    public static void main(String[] args) {
        // 静态的代理
        AI ai = (AI) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(), new Class[]{AI.class}, (proxy, method, args1) -> {
            if (method.getName().equals("say")) {
                System.err.println(Arrays.toString(args1));
            }
            return Void.TYPE;
        });
        ai.say("hello");
		// 动态代理
        ai = (AI) Enhancer.create(Object.class, new Class[]{AI.class}, (MethodInterceptor) (o, method, objects, methodProxy) -> {
            Object res = null;
            if(method.getName().equals("say")){
                System.err.println(Arrays.toString(objects));
            } else {
                res = method.invoke(o, objects);
            }
            return res;
        });

        ai.say("hahaha");
    }
}

interface AI {
    void say(String words);
}

```

| proxy     | 优点               | 缺点       |
| --------- | ------------------ | ---------- |
| ``proxy`` | 内存消耗低         | 接口传递   |
| ``cglib`` | 继承体系，无需接口 | 内存消耗大 |

