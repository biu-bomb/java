# JOIN

两张表关联的时候，如果没有特殊要求，其实就是相关数据两两组合，最终生成的笛卡尔积。

- ``A``

| a_id | a    |
| ---- | ---- |
| 1    | 1    |
| 2    | 2    |
| 3    | 3    |

- ``B``

| b_id | b    |
| ---- | ---- |
| 1    | a    |
| 2    | b    |
| 4    | d    |

# ``right join``

```sql
select * from A right join B on A.a_id = B.b_id;
```

| a_id | a    | b_id | b    |
| ---- | ---- | ---- | ---- |
| 1    | 1    | 1    | a    |
| 2    | 2    | 2    | b    |
| null | null | 4    | d    |

# ``left join``

```sql
select * from A left join B on a.a_id = B.b_id;
```

| a_id | a    | b_id | b    |
| ---- | ---- | ---- | ---- |
| 1    | 1    | 1    | a    |
| 2    | 2    | 2    | b    |
| 3    | 3    | null | null |

# ``inner join``

```sql
select * from A inner join B on A.a_id = B.b_id; 
```

| a_id | a    | b_id | b    |
| ---- | ---- | ---- | ---- |
| 1    | 1    | 1    | a    |
| 2    | 2    | 2    | b    |

# 笛卡尔积

- ``full_join``

```sql
select * from A full join B;
```

| a_id | a    | b_id | b    |
| ---- | ---- | ---- | ---- |
| 1    | 1    | 1    | a    |
| 2    | 2    | 1    | a    |
| 3    | 3    | 1    | a    |
| 1    | 1    | 2    | b    |
| 2    | 2    | 2    | b    |
| 3    | 3    | 2    | b    |
| 1    | 1    | 4    | d    |
| 2    | 2    | 4    | d    |
| 3    | 3    | 4    | d    |

不加限制的情况下，其实就是每条数据的相互组合。

- ``inner join``

```sql
// 两边都存在
select * from A, B where A.id = B.id;
// 等价
select * from full_join where A.id = B.id;
```

# 总结

| join  | A数据存在 | B数据存在 |
| ----- | --------- | --------- |
| full  | 一定存在  | 一定存在  |
| left  | 一定存在  | 不确定    |
| right | 不确定    | 一定存在  |

可以看做是量表通过``ids``或者其他的方式分别进行查询，然后根据``on``的条件进行组合。

但是``full``取得的是``a_ids``和``b_ids``的交集，而``left``或者``right``都是单纯的以一边的``ids``为准。

如果匹配存在匹配数据，就组合，不存在数据的话，就直接填充``null``.