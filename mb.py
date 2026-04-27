import hashlib
import json
import base64
import requests
from datetime import datetime

from utils import get_time_now, generate_device_id, DEFAULT_HEADERS, FPR
from ocr import OCRModel
from wasm_bridge import wasm_encrypt

class MB:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session_id = None
        self.device_id = generate_device_id()
        self.client = requests.Session()
        self.base_url = "https://online.mbbank.com.vn"
        self.ocr_model = OCRModel()

    def login(self):
        rId = get_time_now()
        headers = DEFAULT_HEADERS.copy()
        headers["X-Request-Id"] = rId
        headers["Deviceid"] = self.device_id
        headers["Refno"] = rId

        captcha_payload = {
            "sessionId": "",
            "refNo": rId,
            "deviceIdCommon": self.device_id,
        }

        captcha_res = self.client.post(
            self.base_url + "/api/retail-internetbankingms/getCaptchaImage",
            headers=headers,
            json=captcha_payload
        ).json()

        image_string = captcha_res.get("imageString", "")
        captcha_buffer = base64.b64decode(image_string)

        captcha_content = self.ocr_model.predict(captcha_buffer)

        if not captcha_content or len(captcha_content) != 6:
            return self.login()

        password_md5 = hashlib.md5(self.password.encode('utf-8')).hexdigest()

        request_data = {
            "userId": self.username,
            "password": password_md5,
            "captcha": captcha_content,
            "ibAuthen2faString": FPR,
            "sessionId": None,
            "refNo": get_time_now(),
            "deviceIdCommon": self.device_id,
        }

        data_enc = wasm_encrypt(request_data, "0")

        login_res = self.client.post(
            self.base_url + "/api/retail_web/internetbanking/v2.0/doLogin",
            headers=DEFAULT_HEADERS,
            json={"dataEnc": data_enc}
        ).json()

        result = login_res.get("result", {})

        if result.get("ok"):
            self.session_id = login_res.get("sessionId")
            
            try:
                self.verify_biometric_transaction()
            except Exception as e:
                pass # biometrics not strict to stop login
                
            return login_res
        elif result.get("responseCode") == "GW283":
            return self.login()
        else:
            raise Exception(f"Login failed: ({result.get('responseCode')}): {result.get('message')}")

    def verify_biometric_transaction(self):
        biometric_status = self.mb_request("/api/retail-go-ekycms/v1.0/verify-biometric-nfc-transaction")
        if not biometric_status:
            return False
        result = biometric_status.get("result", {})
        return result.get("responseCode") == "00" and result.get("ok")

    def get_ref_no(self):
        return f"{self.username}-{get_time_now()}"

    def mb_request(self, path, json_data=None):
        if not self.session_id:
            self.login()

        rId = self.get_ref_no()
        headers = DEFAULT_HEADERS.copy()
        headers["X-Request-Id"] = rId
        headers["Deviceid"] = self.device_id
        headers["Refno"] = rId

        body = {
            "sessionId": self.session_id,
            "refNo": rId,
            "deviceIdCommon": self.device_id,
        }
        if json_data:
            body.update(json_data)

        http_res = self.client.post(
            self.base_url + path,
            headers=headers,
            json=body
        ).json()

        result = http_res.get("result", {})

        if not http_res or not result:
            return False
        elif result.get("ok") == True:
            return http_res
        elif result.get("responseCode") == "GW200":
            self.login()
            return self.mb_request(path, json_data)
        else:
            raise Exception(f"Request failed ({result.get('responseCode')}): {result.get('message')}")

    def get_balance(self):
        balance_data = self.mb_request("/api/retail-accountms/accountms/getBalance")
        if not balance_data:
            return None

        balance = {
            "totalBalance": balance_data.get("totalBalanceEquivalent"),
            "currencyEquivalent": balance_data.get("currencyEquivalent"),
            "balances": []
        }

        for acct in balance_data.get("acct_list", []):
            balance["balances"].append({
                "number": acct.get("acctNo"),
                "name": acct.get("acctNm"),
                "currency": acct.get("ccyCd"),
                "balance": acct.get("currentBalance")
            })

        for acct in balance_data.get("internationalAcctList", []):
            balance["balances"].append({
                "number": acct.get("acctNo"),
                "name": acct.get("acctNm"),
                "currency": acct.get("ccyCd"),
                "balance": acct.get("currentBalance")
            })

        return balance

    def get_transactions_history(self, account_number, from_date, to_date):
        fd = datetime.strptime(from_date, "%d/%m/%Y")
        td = datetime.strptime(to_date, "%d/%m/%Y")
        
        body = {
            "accountNo": account_number,
            "fromDate": fd.strftime("%d/%m/%Y"),
            "toDate": td.strftime("%d/%m/%Y"),
        }

        history_data = self.mb_request("/api/retail-transactionms/transactionms/get-account-transaction-history", body)

        if not history_data or "transactionHistoryList" not in history_data:
            return None

        transactions = []
        for tx in history_data.get("transactionHistoryList", []):
            transactions.append({
                "postDate": tx.get("postingDate"),
                "transactionDate": tx.get("transactionDate"),
                "accountNumber": tx.get("accountNo"),
                "creditAmount": tx.get("creditAmount"),
                "debitAmount": tx.get("debitAmount"),
                "transactionCurrency": tx.get("currency"),
                "transactionDesc": tx.get("description"),
                "balanceAvailable": tx.get("availableBalance"),
                "refNo": tx.get("refNo"),
                "toAccountName": tx.get("benAccountName"),
                "toBank": tx.get("bankName"),
                "toAccountNumber": tx.get("benAccountNo"),
                "type": tx.get("transactionType"),
            })

        return transactions
