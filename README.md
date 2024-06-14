# QQ聊天记录统计分析

## 使用

### 生成明文数据库

这里默认你已经获得了QQNT的数据库文件和key，如果没有请参考：

- Windows：[这里](https://github.com/Mythologyli/qq-nt-db)
- 其他：[这里](https://github.com/QQBackup/qq-win-db-key)

在Windows下，先下载MSYS2，然后打开MSYS2 Mingw64终端，使用如下命令获得明文数据库：

```sh
tail -c +1025 nt_msg.db > nt_msg.clean.db
```

在MSYS2 Mingw64终端下，安装[sqlcipher](https://packages.msys2.org/package/mingw-w64-x86_64-sqlcipher?repo=mingw64)

然后运行：
```sh
sqlcipher
```

执行如下指令，其中pass是你获得的16位字符key：

```sql
.open nt_msg.clean.db
PRAGMA key = 'pass'; PRAGMA kdf_iter = '4000';
ATTACH DATABASE 'plaintext.db' AS plaintext KEY '';
SELECT sqlcipher_export('plaintext');
DETACH DATABASE plaintext;
.exit
```

### 生成统计数据

将上一步生成的plaintext.db文件放到本目录下`input`文件夹，然后编辑`config.json`文件，填写明文数据库路径、需要分析的群号、群成员的昵称字典、以及生成词云时需要排除的词。

然后安装依赖
```sh
pip install -r requirements.txt
```

运行：

```sh
python db2json.py
python json2statistics.py
```

生成的结果在`output`文件夹下，点开`output.md`即可查看。

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