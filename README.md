# QQ聊天记录统计分析



```sh
tail -c +1025 nt_msg.db > nt_msg.clean.db
```

```sql
.open nt_msg.clean.db
PRAGMA key = 'pass'; PRAGMA kdf_iter = '4000';
ATTACH DATABASE 'plaintext.db' AS plaintext KEY '';
SELECT sqlcipher_export('plaintext');
DETACH DATABASE plaintext;
.exit
```


## Protobuf表头

- 发送人 40033 QQ号
- 接收人
- 接收群 40030
- 时间戳 40050
- 内容 40800 protobuf
    - id 45001
    - 类型 45002
        - 1 普通文本
        - 2 图片
        - 3 文件
        - 6 表情
        - 7 回复
        - 8 提示消息
        - 10 应用
        - 11 自定义表情
        - 21 电话
        - 26 动态消息
    - 文本 45101
    - 自带新大表情 47602
    - 句内默认表情：同一个blob下有多个40800 field，每个表情单独一个field，表情在47602以`/头秃`这样的形式存储，但47601才是真正的表情id，具体对应关系不明。
    - 句内@：单独40800field，在45101中以`@某某某`这样的形式存储，在45103中存储被@人的QQ号
    - 回复消息：多个40800field，第一个field内47403为回复的消息的发送者id

## 已知缺陷

- 引用他人消息时，不会解析其中的表情