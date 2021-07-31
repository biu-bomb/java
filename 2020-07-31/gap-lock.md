# 间隙锁

## 基本原则

- 加锁的基本单位为``next-key lock``，遵循前开后闭原则
- 等值查询
  - 唯一索引：升级为行锁
  - 范围查询：向右遍历，最后一个不满足条件时，退化为间隙锁
- 唯一索引范围查询：访问到最后一个不满足条件的数据为止

# 案例介绍

## 基础数据

| id(主键) | c(普通索引) | d(无索引) |
| -------- | ----------- | --------- |
| 5        | 5           | 5         |
| 10       | 10          | 10        |
| 15       | 15          | 15        |
| 20       | 20          | 20        |
| 25       | 25          | 25        |

## 简单示例

```sql
# A，间隙锁(10,15]
begin; select * from t where id = 11 for update;
# B，因为被锁定，该语句被阻塞
insert into t values(12,12,12) 
# A 
commit;
```

## 间隙死锁

```sql
# 间隙锁是不互斥的
# A，间隙锁(10, 15]
begin; select * from t where id = 9 for update;
# B 间隙锁不互斥，因此也能拿到间隙锁(10, 15]
begin; select * from t where id = 6 for update;
# 由于A拿到了间隙锁，是不允许其他事务进行DDL操作，该语句被阻塞
insert into t values(7,7,7);
# A，由于B拿到了间隙锁，不允许其他事务进行DDL操作，该语句被阻塞
insert into t values(7,7,7);
# 最终形成死锁
```

## 等值查询唯一索引

```sql
# A 
# 1. 间隙锁，(5,10]
# 2. 等值查询，最后的10不满足 id = 7, 退化为(5, 10)
begin; update t set d = d + 1 where id = 7;
# B 间隙锁锁定范围，该语句被阻塞
insert into t value(8,8,8);
# C 该部分未加锁，可直接修改
update t set d = d + 1 where id = 10;
```

## 等值查询普通索引

```sql
# A
# 1. next-key lock (0, 5]
# 2. 普通索引，要查询到最后一个不匹配的值，(5, 10]
# 3. 等值查询，排除最后一个相等 (5, 10)
begin; select id from t where c = 5 lock in share mode;
# B 
# 1. 虽然都是5，但是锁的c和我id有啥关系，正常执行
# 2. 但是如果锁定的是id，该语句被阻塞
update t set d = d + 1 where id = 5;
# C 修改c，并且在锁定范围内，该语句被阻塞
insert into t values(7,7,7);
```

---

```sql
# A
# 1. next-key lock (5,10]
# 2. 普通索引找到最后一个不匹配的(10,15]
# 3. 等值查询，进行锁降级(10, 15)
begin; select * from t where c = 10 for update;
# B 锁定范围内，阻塞
insert into t values(12,12,12);
# C 锁定范围外，执行
update t set d = d + 1 where c = 15;
```

## 范围查询唯一索引

```sql
# A
# 1. next-key lock (5,10]
# 2. 唯一索引，找到第一个不匹配的数据，(10, 15]
# 3. 等值查询，升级为行级锁，因此最终锁为[10, 15]
begin; select * from t where id >= 10 and id < 11 from update;
# B 锁范围内，一下两条语句阻塞
insert into t values(8,8,8);
insert into t values(13,13,13);
# C 锁范围内，该语句阻塞
update t set d = d + 1 where id = 15;
```

## 范围查询普通索引

```sql
# A
# 1. next-lock (5, 10]
# 2. 非唯一索引 (10, 15]
# 3. 非等值查询锁不升级为行锁，仍然保持(10， 15]
begin; select * from t where c >= 10 and c < 11 for update;
# B 锁定范围内，阻塞
insert into t values(8,8,8);
# C 锁定范围内，阻塞
update t set d = d + 1 where c = 15;
```

## limit

```sql
# A
# 1. next-key lock (5, 10]
# 2. 由于区间内数据满足limit，不再向后匹配
begin; delete * from t where c = 10 limit 1;
# B 非加锁区间，执行
insert into t values(12,12,12);
# C 非加锁区间，执行
insert into t values(15,15,15);
```

