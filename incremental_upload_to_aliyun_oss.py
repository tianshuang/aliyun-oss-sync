import base64
import hashlib
import os

import oss2
import requests

auth = oss2.Auth('AccessKeyId', 'AccessKeySecret')
bucket = oss2.Bucket(auth, 'Endpoint', 'BucketName')
oss_public_domain = 'OssDomain'

local_dir = "/Users/Poison/blog/public/"


def content_md5(local_file_path):
    with open(local_file_path, 'rb') as fileobj:
        m = hashlib.md5()
        while True:
            d = fileobj.read(8096)
            if not d:
                break
            m.update(d)
        return str(base64.b64encode(m.digest()))


def upload_file_to_aliyun_oss(local_file_path):
    if local_file_path.endswith(".DS_Store"):
        return
    oss_object_key = local_file_path[local_dir.__len__():]
    local_file_md5 = content_md5(local_file_path)
    exist = bucket.object_exists(oss_object_key)
    if exist:
        oss_file_head = requests.head("http://" + oss_public_domain + "/" + oss_object_key)
        if local_file_md5 == oss_file_head.headers["Content-MD5"]:
            return

    with open(local_file_path, 'rb') as fileobj:
        print "Uploading: " + local_file_path
        result = bucket.put_object(oss_object_key, fileobj, headers={'Content-MD5': local_file_md5})
        if result.status != 200:
            print "upload error, response information: " + str(result)
            exit(1)


for dirpath, dirnames, filenames in os.walk(local_dir):
    for filename in filenames:
        upload_file_to_aliyun_oss(os.path.join(dirpath, filename))
