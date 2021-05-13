# JWT

```javascript
head.payload.signature
```

## head

- core

```json
{
    "alg":"HS256",
    "typ":"JWT"
}
```

- ``encoding``

```javascript
head = base64UrlEncode(core)
```

## payload

- core（自定义数据）

```json
{
    "name":"name",
    "gender":"gender"
}
```

==官方推荐==

| field                    | description |
| ------------------------ | ----------- |
| ``iss(issuer)``          | 签发人      |
| ``exp(expiration time)`` | 过期时间    |
| ``sub(subject)``         | 主题        |
| ``aud(audience)``        | 受众        |
| ``nbf(not before)``      | 生效时间    |
| ``iat(issued At)``       | 签发时间    |
| ``jti(JWT ID)``          | ``ID``      |

- ``encoding``

```javascript
payload = base64UrlEncode(core)
```

## signature

- secret：自定义``salt``
- signature

```javascript
signature = HMACSHA256(head.payload, secret)
```

> <font color='red'>默认的加密算法是``HMACSHA256``，特殊指定可以在``head``里进行设置，保证一致即可。</font>

## JWT

```shell
jwt = head.payload.signature
```

# base64URL

<font color='red'>有时候``token``需要拼接``url``，为了避免特殊字符影响，需要进行``base64URL``加密转换。</font>