from qiniuS3 import QiniuS3
import conf
import os

qiniu_s3 = QiniuS3()
qiniu_s3.download_directory(conf.config['local_dir'])