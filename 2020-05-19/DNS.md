# 什么是DNS

``DNS``：``Domain Name System``。域名系统。提供域名和``IP``的映射查询。

![img](../.imgs/dns)

> 根服务器：最顶级的``DNS``服务器，世界仅仅12台。

# DNS查询

| 查询方式 | 查询动作                                                     |
| -------- | ------------------------------------------------------------ |
| 本地解析 | 本地缓存，查到直接返回                                       |
| 直接解析 | 查找设定的``DNS``服务器，查到返回                            |
| 递归查询 | 将查询委托扔给``DNS``服务器，服务器查询上一级服务器，最终层级返回 |
| 迭代查询 | ``DNS``服务器返回下一个查询地址，客户端访问新的``DNS``服务器 |

# DNS劫持

>  劫持，主要是说控制了域名到``IP``的映射关系。

当恶意修改两者的映射，就会使得域名访问不通，或者引导到钓鱼网站，泄漏个人隐私。

---

一般为了查询加速，每一级的``DNS``并不会每次都重新查询，而是会将上一级的映射存储到本地缓存。

人为或者无意制造的一些错误缓存，也会导致映射不对，此类为**DNS污染**.