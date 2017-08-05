# aliyun-oss-sync

### 简介
阿里云 OSS 增量上传脚本，此脚本是用来发布我个人博客 [Poison](https://tianshuang.me/) 而编写的，因为工作中常用语言为 Java，而 Python 仅是副业，代码如有不当之处，敬请指出。

逻辑很简单，递归遍历本地目录，然后判断每个文件在 OSS 里是否存在，如果不存在则直接上传，如果存在则检查 Content-Md5 是否相等，如果不相等则表明该文件内容已经发生变化，则上传该文件，OSS 会自动覆盖同名文件。

值得注意的是检查 Content-Md5 的值是用的 HTTP 的 HEAD 方法，因为我们只需要 header 中的 Content-Md5 字段的值，所以并不需要使用 GET 方法拿到响应体，这样既加快了速度也节省了 OSS 流量。遍历是单个线程在进行遍历，然后将遍历到的文件上传任务放进了线程池，因为上传任务为 I/O 密集型，故使用多线程上传，采用 Python 指定的默认线程数。源代码如下：

```python
max_workers = (os.cpu_count() or 1) * 5
```

关于 ossDomain 的值，你如果在同地域内网的 ECS 上使用该脚本，建议使用内网域名，速度快并且节省了流量费用，否则使用外网域名。

环境要求：
Python 3.2 +

使用方法：

下载 [incremental_upload_to_aliyun_oss.py](https://storage.tianshuang.me/aliyun-oss-sync/incremental_upload_to_aliyun_oss.py)

下载 [oss_config.json](https://storage.tianshuang.me/aliyun-oss-sync/oss_config.json)

将你的 OSS 配置信息替换掉 oss_config.json 中的模版配置，并将以上两个文件放置于同一目录下即可运行。

```Bash
python3 incremental_upload_to_aliyun_oss.py
```

如有建议，敬请指出。