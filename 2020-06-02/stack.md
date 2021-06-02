# 栈

| 特点 | 描述               | 利用                                       |
| ---- | ------------------ | ------------------------------------------ |
| 倒序 | 后进先出           | 全部压栈然后弹出                           |
| 缓冲 | 压栈不出，当做存储 | 标识压入，数据缓冲<br />标识弹出，数据处理 |

# 基础使用

![image-20210602172027758](../.imgs/image-20210602172027758.png)

```java
// time: O(n)
// stace: O(n)
class Solution {
    Map<Character, Character> match = new HashMap<>(){
        {
            put(']', '[');
            put('}', '{');
            put(')', '(');
        }
    };
    public boolean isValid(String s) {
        char ch;
         Stack<Character> stack = new Stack<>();
        for(int i = 0; i < s.length(); i++){
            ch = s.charAt(i);
            if(match.containsKey(ch)){
                if(stack.isEmpty() || stack.pop() != match.get(ch)){
                    return false;
                }
            } else {
                stack.push(ch);
            }
        }
        return stack.isEmpty();
    }
}
```

![image-20210602173627511](../.imgs/image-20210602173627511.png)

```java
class Solution {
    public String removeDuplicates(String s) {
		Stack<Character> stack = new Stack<>();
        char ch;
        for(int i = 0; i < s.length(); i++){
            ch = s.charAt(i);
            if(stack.isEmpty() || stack.peek() != ch){
                stack.push(ch);
            } else {
                stack.pop();
            }
        }
        StringBuilder sb = new StringBuilder();
        while(!stack.isEmpty()){
            sb.append(stack.pop());
        }
        return sb.reverse().toString();
    }
}
```

![image-20210602174228007](../.imgs/image-20210602174228007.png)

```java
class Solution {
    public boolean backspaceCompare(String s, String t) {
		Stack<Character> ss = toStack(s);
        Stack<Character> ts = toStack(t);
        if(ss.size() != ts.size()) return false;
        while(!ss.isEmpty()){
            if(ss.pop() != ts.pop()) return false;
        }
        return true;
    }
    
    public Stack<Character> toStack(String s){
        Stack<Character> stack = new Stack<>();
        char ch;
        for(int i = 0; i < s.length(); i++){
            ch = s.charAt(i);
            if('#' == ch){
                if(!stack.isEmpty()){
                    stack.pop();
                }
            } else {
                stack.push(ch);
            }
        }
        return stack;
    }
}
```

# 缓冲区间

![image-20210602195226753](../.imgs/image-20210602195226753.png)

```java
class Solution {
    public String reverseParentheses(String s) {
		S
    }
}
```

