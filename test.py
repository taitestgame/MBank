import time
import sys
import io
from datetime import datetime

# Force UTF-8 encoding for Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from mb import MB


def main():
    # THAY THẾ TÀI KHOẢN CỦA BẠN VÀO ĐÂY
    USERNAME = ""
    PASSWORD = ""

    mb = MB(username=USERNAME, password=PASSWORD)

    try:
        print("Đang tiến hành đăng nhập...")
        mb.login()
        print("✅ Đăng nhập thành công!")

        print("\n--- LẤY THÔNG TIN SỐ DƯ ---")
        balance = mb.get_balance()
        if balance:
            print(f"💰 Tổng số dư: {balance.get('totalBalance')} {balance.get('currencyEquivalent')}")
            for account in balance.get('balances', []):
                print(f"- Tài khoản: {account.get('name')} ({account.get('number')})")
                print(f"  Số dư: {account.get('balance')} {account.get('currency')}")
        
        last_transaction_ref = ""

        def check_transactions():
            nonlocal last_transaction_ref
            if balance and balance.get('balances'):
                account_number = balance['balances'][0]['number']
                
                today_str = datetime.now().strftime("%d/%m/%Y")
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Đang kiểm tra giao dịch mới...")
                try:
                    transactions = mb.get_transactions_history(
                        account_number=account_number,
                        from_date=today_str,
                        to_date=today_str
                    )

                    if transactions and len(transactions) > 0:
                        latest_tx = transactions[0]
                        
                        if latest_tx.get("refNo") != last_transaction_ref:
                            if last_transaction_ref != "":
                                print("\n🔔🔔🔔 PHÁT HIỆN GIAO DỊCH MỚI!")
                            else:
                                print("\n✅ Giao dịch gần nhất hôm nay:")
                                
                            last_transaction_ref = latest_tx.get("refNo")
                            
                            amount = latest_tx.get("creditAmount") or latest_tx.get("debitAmount")
                            tx_type = "NHẬN (+)" if latest_tx.get("creditAmount") else "CHUYỂN (-)"
                            
                            print(f"[{latest_tx.get('transactionDate')}] | {tx_type} {amount} {latest_tx.get('transactionCurrency')}")
                            print(f"  Nội dung: {latest_tx.get('transactionDesc')}")
                            
                            # Đọc thông báo bằng giọng nói nếu là giao dịch nhận tiền
                            
                        else:
                            print("Không có giao dịch mới.")
                    else:
                        print("Chưa có giao dịch nào trong hôm nay.")
                except Exception as e:
                    print(f"Lỗi khi kiểm tra giao dịch: {str(e)}")

        check_transactions()
        
        print("\n⏳ Bắt đầu chế độ theo dõi 15s/lần. (Bấm Ctrl+C trên terminal để dừng)")
        while True:
            time.sleep(15)
            check_transactions()

    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH CHẠY: {str(e)}")

if __name__ == "__main__":
    main()
