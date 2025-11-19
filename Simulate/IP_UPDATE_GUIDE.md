# 🌐 Hướng dẫn cập nhật IP Resolume

## Tính năng mới
Bây giờ bạn có thể thay đổi địa chỉ IP Resolume của ESP32 trực tiếp từ giao diện Python mà không cần phải sửa code và flash lại ESP32.

## 🔧 Cách sử dụng

### 1. Từ giao diện GUI
1. Mở ứng dụng Cube Touch Monitor
2. Trong phần "CONFIG MODE", tìm mục "🌐 Cấu hình IP Resolume"
3. Nhập IP mới vào ô "IP mới"
4. Nhấn nút "🔄 Cập nhật IP Resolume"
5. Xác nhận thay đổi

### 2. Từ command line
```python
# Gửi lệnh UDP trực tiếp
import socket

def update_resolume_ip(new_ip, esp_ip='192.168.0.43'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command = f"RESOLUME_IP:{new_ip}"
    sock.sendto(command.encode(), (esp_ip, 4210))
    sock.close()

# Ví dụ sử dụng
update_resolume_ip("192.168.1.100")
```

## 📋 Định dạng lệnh

### Cập nhật IP
```
RESOLUME_IP:192.168.1.100
```

### Lấy thông tin IP hiện tại
```
GET_IP_CONFIG
```

## 🧪 Test script
Chạy file `test_ip_update.py` để test tính năng:
```bash
python test_ip_update.py
```

## ✅ Xác nhận thành công
- ESP32 sẽ in ra Serial Monitor: "Resolume IP updated to: x.x.x.x"
- GUI sẽ hiển thị IP mới trong:
  - Phần cấu hình IP
  - Footer thông tin hệ thống
  - Log messages

## 🔍 Kiểm tra lỗi
- IP không hợp lệ: ESP32 sẽ báo "Invalid IP format"
- Không kết nối được: GUI sẽ hiển thị thông báo lỗi
- Log sẽ ghi lại tất cả hoạt động

## 📝 Lưu ý
- IP được lưu tạm thời, sẽ reset về mặc định khi restart ESP32
- Để lưu vĩnh viễn, cần cập nhật code ESP32 với IP mặc định mới
- Format IP phải đúng: xxx.xxx.xxx.xxx (0-255 cho mỗi số)

## 🔄 Khôi phục IP mặc định
Gửi lệnh: `RESOLUME_IP:192.168.0.241` hoặc restart ESP32.

## 🐛 Troubleshooting
1. **Không gửi được lệnh**: Kiểm tra kết nối ESP32
2. **IP không thay đổi**: Kiểm tra format IP và log
3. **GUI không cập nhật**: Restart ứng dụng