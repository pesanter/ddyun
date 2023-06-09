# 使用七牛云对象存储，实现本地目录与云端快照同步，支持上传和下载操作。
import qiniu
import hashlib
import os
import conf

class QiniuS3:
    def __init__(self):
        # 创建Qiniu对象  
        self.q = qiniu.Auth(conf.config['access_key'], conf.config['secret_key'])
        
    # 按照预定义的目录和对象，上传更新到七牛的目录/对象存储。 
    def uploadFile(self, key, local_file):       
        if QiniuS3.doRemoteFileCheck(self, key, QiniuS3.get_md5(local_file)):
            # 生成上传 Token
            token = self.q.upload_token(conf.config['bucket_name'], key)
            ret, info = qiniu.put_file(token, key, local_file) 
            print(f'{local_file}+已更新')

    def get_md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def doRemoteFileCheck(self, key, local_file_md5):
        # 初始化BucketManager
        bucket = qiniu.BucketManager(self.q)

        # 获取文件的状态信息
        ret, info = bucket.stat(conf.config['bucket_name'], key)
        if info.status_code == 200:
            # 提取文件的 MD5 值
            file_md5 = ret['md5']
            if local_file_md5 == file_md5 or local_file_md5 == '':
                return False
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
                if QiniuS3.doRemoteFileCheck(self, directory, dir):
                    # 生成上传 Token
                    token = self.q.upload_token(conf.config['bucket_name'], dir+'/')
                    ret, info = qiniu.put_data(token, dir+'/', '')  # 创建目录
                    if info.status_code == 200:
                        print("成功创建文件夹:", directory)
                    else:
                        print("创建文件夹失败:", info.text_body)

                
    
