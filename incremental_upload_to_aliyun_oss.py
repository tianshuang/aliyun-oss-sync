import base64
import hashlib
import json
import os

import oss2
import requests


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
    if local_file_path.endswith('.DS_Store'):
        return
    oss_object_key = local_file_path[local_dir.__len__():]
    local_file_md5 = content_md5(local_file_path)
    exist = bucket.object_exists(oss_object_key)
    if exist:
        oss_file_head = requests.head('https://' + oss_domain + '/' + oss_object_key)
        if local_file_md5 == oss_file_head.headers['Content-MD5']:
            return

    with open(local_file_path, 'rb') as fileobj:
        print 'Uploading: ' + local_file_path
        result = bucket.put_object(oss_object_key, fileobj, headers={'Content-MD5': local_file_md5})
        if result.status != 200:
            print 'upload error, response information: ' + str(result)
            exit(1)


if __name__ == '__main__':
    oss_config = None
    with open('oss_config.json') as oss_config_file:
        oss_config = json.load(oss_config_file)
        if 'accessKeyId' not in oss_config:
            raise ValueError('No accessKeyId in oss_config.json')
        if 'accessKeySecret' not in oss_config:
            raise ValueError('No accessKeySecret in oss_config.json')
        if 'endpoint' not in oss_config:
            raise ValueError('No endpoint in oss_config.json')
        if 'bucketName' not in oss_config:
            raise ValueError('No bucketName in oss_config.json')
        if 'ossDomain' not in oss_config:
            raise ValueError('No ossDomain in oss_config.json')
        if 'localDir' not in oss_config:
            raise ValueError('No localDir in oss_config.json')
        if not str(oss_config['localDir']).strip().endswith('/'):
            raise ValueError('localDir must end with a slash, example: /Users/Poison/blog/public/')

    auth = oss2.Auth(oss_config['accessKeyId'], oss_config['accessKeySecret'])
    bucket = oss2.Bucket(auth, oss_config['endpoint'], oss_config['bucketName'])
    oss_domain = oss_config['ossDomain']
    local_dir = oss_config['localDir']

    for dirpath, dirnames, filenames in os.walk(local_dir):
        for filename in filenames:
            upload_file_to_aliyun_oss(os.path.join(dirpath, filename))
