# 使用七牛云对象存储，实现本地目录与云端快照同步，支持上传和下载操作。
from base64 import urlsafe_b64encode
import qiniu
import hashlib
import os
import conf
import requests

class QiniuS3:
    def __init__(self):
        # 创建Qiniu对象  
        self.q = qiniu.Auth(conf.config['access_key'], conf.config['secret_key'])

        # 初始化BucketManager
        self.bucket = qiniu.BucketManager(self.q)
        
    # 按照预定义的目录和对象，上传更新到七牛的目录/对象存储。 
    def uploadFile(self, key, local_file):       
        if QiniuS3.doRemoteFileCheck(self, key, local_file):
            # 生成上传 Token
            token = self.q.upload_token(conf.config['bucket_name'], key)
            ret, info = qiniu.put_file(token, key, local_file) 
            print(f'{local_file}+已更新')

    def get_md5(fname):
        if os.path.exists(fname) and os.path.isfile(fname):
            hash_md5 = hashlib.md5()
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        else:
            return 'X'

    def doRemoteFileCheck(self, key, local_file):
        # 获取文件的状态信息
        ret, info = self.bucket.stat(conf.config['bucket_name'], key)
        if info.status_code == 200:
            # 提取文件的 MD5 值
            file_md5 = ret['md5']
            if os.path.exists(local_file):
                if os.path.isfile(local_file):
                    if QiniuS3.get_md5(local_file) == file_md5:
                        return False
                    else:
                        return True
                else:
                    return os.path.basename(local_file) != key.replace("/","")
            else:
                return True
        else:
            return True
        assert 'hash' in ret
        
    def upload_directory(self, upDir):
        for root, dirs, files in os.walk(upDir):
            for file in files:
                local_filepath = os.path.join(root, file)
                key = os.path.relpath(local_filepath, upDir).replace('\\', '/')
                self.uploadFile(key, local_filepath)

            for directory in dirs:
                sub_directory = os.path.join(root, directory)
                dir = os.path.relpath(sub_directory, upDir)
                key = dir+'/'
                if QiniuS3.doRemoteFileCheck(self, key, sub_directory):
                    # 生成上传 Token
                    token = self.q.upload_token(conf.config['bucket_name'], key)
                    ret, info = qiniu.put_data(token, key, '')  # 创建目录
                    if info.status_code == 200:
                        print("成功创建文件夹:", directory)
                    else:
                        print("创建文件夹失败:", info.text_body)

    def download_directory(self, downloadDir):
        # 指定前缀（模拟目录）
        prefix = ''
        # 列出存储空间中的对象
        ret, eof, info = self.bucket.list(conf.config['bucket_name'], prefix=prefix)
        if ret is not None:
            for item in ret['items']:
                if QiniuS3.doRemoteFileCheck(self, item['key'], downloadDir  + item['key']):
                    # 创建下载链接
                    # base_url = 'http://%s/%s' % (conf.config['bucket_name'] + '.' + conf.config['endpoint'], urlsafe_b64encode(item['key'].encode()).decode())
                    base_url = 'http://%s/%s' % (conf.config['domain'], item['key'])

                    # 生成私有下载链接，有时效性
                    private_url = self.q.private_download_url(base_url, expires=3600)

                    # 下载到本地文件
                    response = requests.get(private_url)

                    if response.status_code == 200:
                        # 检查文件是否存在  
                        if os.path.exists(downloadDir):  
                            if(item['key'].endswith('/')):
                                os.makedirs(os.path.join(downloadDir, item['key']), exist_ok=True) 
                            else:
                                # 创建新文件  
                                with open(os.path.join(downloadDir, item['key']), "wb") as f:  
                                    f.write(response.content)  
                            print(f"已创建 {item['key']}")  
                        else:  
                            # 创建新目录  
                            os.makedirs(downloadDir, exist_ok=True)  
                            # 在新目录中创建新文件  
                            with open(os.path.join(downloadDir, item['key']), "wb") as f:  
                                f.write(response.content)  
                            print(f"已创建 {item['key']}")
                    else:
                        print('Download failed with status code:', response.status_code)
        else:
            print(info)  # 打印出错误信息
                
qiniu_s3 = QiniuS3()
# qiniu_s3.download_directory(conf.config['local_dir'])    
qiniu_s3.upload_directory(conf.config['local_dir'])
