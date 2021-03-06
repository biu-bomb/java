# Redis内存淘汰策略

## 淘汰时机

``redis``设置了``max-memory``，执行新指令添加数据时会进行内存使用检查。

如果已经使用的内存达到``max-memory``，就需要根据设定的内存淘汰策略进行内存淘汰。

## 内存淘汰策略

| 淘汰策略            | 策略描述                                |
| ------------------- | --------------------------------------- |
| ``noeviction``      | 返回``error``，拒绝执行                 |
| ``allkeys-lru``     | 扫描全部``key``，淘汰最近未使用         |
| ``volatile-lru``    | 扫描设置过期的``key``，淘汰最近未使用   |
| ``allkeys-random``  | 扫描全部``key``，随机淘汰               |
| ``volatile-random`` | 扫描设置过期的``key``，随机淘汰         |
| ``volatile-ttl``    | 扫描设置过期的``key``，淘汰即将过期     |
| ``volatile-lfu``    | 扫描设置过期的``key``，淘汰最近最少使用 |
| ``allkeys-lfu``     | 扫描全部``key``，淘汰最近最少使用       |

