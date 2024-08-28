import psutil
import time
import uuid
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

class DeviceFingerprint:
    def __init__(self, encryption_key: bytes):
        self.encryption_key = encryption_key

    def get_battery_info(self):
        battery = psutil.sensors_battery()
        battery_percentage = battery.percent
        charging_status = battery.power_plugged
        estimated_seconds_remaining = battery.secsleft
        return battery_percentage, charging_status, estimated_seconds_remaining

    def get_timestamp(self):
        return time.time() 

    def get_mac_address(self):
        mac = uuid.getnode()
        mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        return mac_address

    def generate_fingerprint(self):
        battery_percentage, charging_status, estimated_seconds_remaining = self.get_battery_info()
        timestamp = self.get_timestamp()
        mac_address = self.get_mac_address()

        data_string = f"{battery_percentage}|{charging_status}|{estimated_seconds_remaining}|{timestamp}|{mac_address}"
        
        sha256_hash = hashlib.sha256(data_string.encode()).hexdigest()
        return sha256_hash

    def encrypt_data(self, data: str):
        iv = time.time_ns().to_bytes(16, byteorder='big')[:16]  
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted_data  

    def decrypt_data(self, encrypted_data: bytes):
        iv = encrypted_data[:16] 
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(encrypted_data[16:]) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

        return unpadded_data.decode()
