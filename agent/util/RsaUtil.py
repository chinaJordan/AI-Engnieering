import base64
import hashlib
import os

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


# ========== 生成RSA公钥/私钥（一次性生成，项目启动时执行） ==========
# 生成2048位RSA密钥对，非对称加密核心
rsa_key = RSA.generate(2048)
# 私钥（后端保存，用于解密前端加密的密码）
RSA_PRIVATE_KEY = rsa_key.export_key()
# 公钥（传给前端，用于加密密码）
RSA_PUBLIC_KEY = rsa_key.publickey().export_key().decode("utf-8")

# ========== 工具函数（加密/解密/哈希） ==========
def rsa_decrypt(cipher_text):
    """后端RSA私钥解密：解密密文→明文密码"""
    private_key = RSA.import_key(RSA_PRIVATE_KEY)
    cipher = PKCS1_v1_5.new(private_key)
    # 前端传的是base64编码，先解码再解密
    decrypt_text = cipher.decrypt(base64.b64decode(cipher_text), None)
    return decrypt_text.decode("utf-8")

def gen_salt(length=16):
    """生成随机盐值：用于密码加盐哈希"""
    return os.urandom(length).hex()

def pwd_hash(password, salt):
    """SHA256加盐哈希：密码+盐值 → 不可逆哈希值（最终存储到数据库）"""
    sha256 = hashlib.sha256()
    sha256.update((password + salt).encode("utf-8"))
    return sha256.hexdigest()