import base64
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor

import oss2
import requests


def content_md5(local_file_path):
    with open(local_file_path, 'rb') as file:
        m = hashlib.md5()
        while True:
            d = file.read(8096)
            if not d:
                break
            m.update(d)
        return str(base64.b64encode(m.digest()), 'utf-8')


def upload_file_to_aliyun_oss(local_file_path):
    if is_windows:
        local_file_path = local_file_path.replace('\\', '/')
    if local_file_path.endswith('.DS_Store') or not os.path.isfile(local_file_path):
        return
    oss_object_key = local_file_path[local_dir.__len__():]
    oss_response = requests.head('https://' + oss_domain + '/' + oss_object_key)
    if oss_response.status_code == 200 and content_md5(local_file_path) == oss_response.headers['Content-MD5']:
        return

    print('uploading: ' + local_file_path)
    result = bucket.put_object_from_file(oss_object_key, local_file_path)
    if result.status != 200:
        print('upload error, response information: ' + str(result))
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

    is_windows = False
    if os.name == 'nt':
        is_windows = True

    auth = oss2.Auth(oss_config['accessKeyId'], oss_config['accessKeySecret'])
    bucket = oss2.Bucket(auth, oss_config['endpoint'], oss_config['bucketName'])
    oss_domain = oss_config['ossDomain']
    local_dir = oss_config['localDir']

    with ThreadPoolExecutor() as executor:
        for dirpath, dirnames, filenames in os.walk(local_dir):
            for filename in filenames:
                executor.submit(upload_file_to_aliyun_oss, os.path.join(dirpath, filename))
