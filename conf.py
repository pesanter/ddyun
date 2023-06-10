import base64  
import pickle
import sys  
from Crypto.Cipher import AES  
from Crypto.Util.Padding import pad, unpad  
import os

# 加密密钥，需要保密存储  
key = '9vMKMlChpZJvWGAj3LxToU9wzXZ0jKlV'  
  
# 加密函数，将配置内容加密并序列化  
def encrypt_config(config, key):  
    # 将密钥和配置内容转换为字节串  
    key = bytes(key, 'utf-8')  
    config_bytes = pickle.dumps(config)  
    # 使用AES加密  
    cipher = AES.new(key, AES.MODE_ECB)  
    encrypted_bytes = cipher.encrypt(pad(config_bytes, AES.block_size))  
    # 对加密结果进行base64编码  
    encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')  
    return encrypted_str  
  
# 从文件中读取并解密配置内容  
def get_config():  
    # 从文件中读取加密后的配置内容
    if os.path.exists(resource_path('config.pickle')):
        with open(resource_path('config.pickle'), 'rb') as f:  
            encrypted_config = f.read().decode('utf-8')  
        # 解密配置内容  
        decrypted_config = decrypt_config(encrypted_config, key)  
    
        # 反序列化配置内容  
        config = pickle.loads(decrypted_config)
    else:
        config = {'access_key': '', 'secret_key': '', 'bucket_name': '', 'local_dir': '', 'domain': ''}
    return config  
  
# 解密函数，将加密后的配置内容解密并反序列化  
def decrypt_config(encrypted_config, key):  
    # 将密钥和加密后的配置内容转换为字节串  
    key = bytes(key, 'utf-8')  
    encrypted_bytes = base64.b64decode(encrypted_config)  
    # 使用AES解密  
    cipher = AES.new(key, AES.MODE_ECB)  
    decrypted_bytes = cipher.decrypt(encrypted_bytes)  
    # 反序列化配置内容并去除补齐字节  
    decrypted_str = unpad(decrypted_bytes, AES.block_size)  
    return decrypted_str
  
# 持久化函数，将加密后的配置内容写入文件  
def persist_config(encrypted_config, filename): 
    with open(resource_path(filename), 'wb') as f:  
        f.write(encrypted_config.encode('utf-8'))  
 
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否 Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)  

# 配置内容，例如：  
config = get_config()
