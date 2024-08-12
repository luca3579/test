from cryptography.fernet import Fernet
from app.utils import AppException


def generate_key():
    """生成新的加密密鑰"""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    """從文件中讀取加密密鑰"""
    try:
        return open("secret.key", "rb").read()
    except FileNotFoundError:
        raise AppException(status_code=500, detail="找不到加密密鑰")


def encrypt_file(file_path):
    """加密指定路徑的文件"""
    try:
        key = load_key()
        fernet = Fernet(key)

        with open(file_path, "rb") as file:
            original_data = file.read()

        encrypted_data = fernet.encrypt(original_data)

        with open(file_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)
    except Exception as e:
        raise AppException(status_code=500, detail=f"加密文件時出錯: {str(e)}")


def decrypt_file(file_path):
    """解密指定路徑的文件"""
    try:
        key = load_key()
        fernet = Fernet(key)

        with open(file_path, "rb") as enc_file:
            encrypted_data = enc_file.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        with open(file_path, "wb") as dec_file:
            dec_file.write(decrypted_data)
    except Exception as e:
        raise AppException(status_code=500, detail=f"解密文件時出錯: {str(e)}")