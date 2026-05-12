# <p align="center"><img src="https://img.shields.io/badge/MB_BANK-AUTOMATION-blue?style=for-the-badge&logo=appveyor" height="35"> <img src="https://img.shields.io/badge/PYTHON-3.9+-yellow?style=for-the-badge&logo=python" height="35"></p>

<p align="center">
  <i align="center">Giải pháp tự động hóa ngân hàng MB Bank mạnh mẽ, chính xác và bảo mật.</i><br>
  <img src="https://img.shields.io/github/stars/taitestgame/MBank?style=social">
  <img src="https://img.shields.io/github/forks/taitestgame/MBank?style=social">
</p>

---

## 🌈 Tổng quan dự án

Dự án này giúp bạn kết nối trực tiếp vào hệ thống **Internet Banking của MB Bank** mà không cần qua trình duyệt. Thích hợp cho các hệ thống nạp tiền tự động, bot thông báo biến động số dư hoặc quản lý tài chính cá nhân.

> [!IMPORTANT]
> **Tự động vượt Captcha:** Tích hợp OCR sẵn trong nhân xử lý.
> **Mã hóa chuẩn:** Xử lý MD5 và WASM tương thích 100% với server MB.

---

## 🚀 Tính năng nổi bật

| Tính năng | Trạng thái | Mô tả |
| :--- | :---: | :--- |
| 🔑 **Login Auto** | <kbd>STABLE</kbd> | Đăng nhập kèm xử lý Captcha tự động |
| 💰 **Check Balance** | <kbd>ACTIVE</kbd> | Lấy số dư tất cả tài khoản cực nhanh |
| 📋 **History** | <kbd>ACTIVE</kbd> | Truy xuất lịch sử giao dịch chi tiết |
| 🆔 **Device Identity** | <kbd>SECURE</kbd> | Giả lập Device ID chuẩn xác |
| ⚡ **Biometric** | <kbd>BETA</kbd> | Hỗ trợ xác thực NFC/Sinh trắc học |

---

## 🛠 Cài đặt & Cấu trúc

### 1. Yêu cầu hệ thống
Cài đặt các thư viện cần thiết bằng một dòng lệnh:
```bash
pip install requests pillow numpy opencv-python