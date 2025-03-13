from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import json
from collections import defaultdict

app = Flask(__name__)
# CORS設定
# CORS(app, resources={r"/*": {"origins": "*"}})  # すべてのオリジンを許可
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5501"}})  # フロントエンドのオリジンを指定

DATABASE = 'group_transactions.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_url TEXT,
                        payer TEXT,
                        recipients TEXT,
                        amount REAL,
                        currency TEXT,
                        purpose TEXT,
                        date TEXT)''')
        db.commit()

@app.route("/transactions", methods=["POST", "OPTIONS"])
def add_transaction():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    try:
        data = request.json
        if not all(key in data for key in ("groupUrl", "payer", "recipients", "amount", "currency", "purpose", "date")):
            return jsonify({"error": "Missing required fields"}), 400

        group_url = data["groupUrl"]
        payer = data["payer"]
        recipients = data["recipients"]
        amount = data["amount"]
        currency = data["currency"]
        purpose = data["purpose"]
        date = data["date"]

        # データベースに保存
        db = get_db()
        c = db.cursor()
        c.execute('''
            INSERT INTO transactions (group_url, payer, recipients, amount, currency, purpose, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (group_url, payer, json.dumps(recipients), amount, currency, purpose, date))
        db.commit()

        return _corsify_actual_response(jsonify({
            "groupUrl": group_url,
            "payer": payer,
            "recipients": recipients,
            "amount": amount,
            "currency": currency,
            "purpose": purpose,
            "date": date
        }), 201)
    except Exception as e:
        return _corsify_actual_response(jsonify({"error": str(e)}), 500)

@app.route("/api/transactions", methods=["POST", "OPTIONS"])
def get_transactions():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    try:
        body = request.get_json()
        group_url = body.get("Group-Url")
        db = get_db()
        c = db.cursor()
        c.execute('''
            SELECT payer, recipients, amount, currency, purpose, date
            FROM transactions
            WHERE group_url = ?
        ''', (group_url,))
        transactions = c.fetchall()

        return _corsify_actual_response(jsonify([
            {
                "groupUrl": group_url,
                "payer": txn[0],
                "recipients": json.loads(txn[1]),
                "amount": txn[2],
                "currency": txn[3],
                "purpose": txn[4],
                "date": txn[5]
            }
            for txn in transactions
        ]))
    except Exception as e:
        print(e)
        return _corsify_actual_response(jsonify({"error": str(e)}), 500)

@app.route("/calculate", methods=["POST", "OPTIONS"])
def calculate():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    try:
        data = request.json
        transactions = data.get("transactions", [])
        result = settle_debts(transactions)
        return _corsify_actual_response(jsonify(result))
    except Exception as e:
        return _corsify_actual_response(jsonify({"error": str(e)}), 500)

def settle_debts(transactions):
    balances = defaultdict(int)

    for payer, payee, amount in transactions:
        balances[payer] -= amount
        balances[payee] += amount

    debtors = sorted([(p, bal) for p, bal in balances.items() if bal < 0], key=lambda x: x[1])
    creditors = sorted([(p, bal) for p, bal in balances.items() if bal > 0], key=lambda x: x[1], reverse=True)

    results = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, d_amount = debtors[i]
        creditor, c_amount = creditors[j]

        payment = min(-d_amount, c_amount)
        results.append({"from": creditor, "to": debtor, "amount": payment})

        debtors[i] = (debtor, d_amount + payment)
        creditors[j] = (creditor, c_amount - payment)

        if debtors[i][1] == 0: i += 1
        if creditors[j][1] == 0: j += 1
    print("Calculated settlements:", results)
    return results


def _build_cors_preflight_response():
    response = jsonify({"message": "CORS Preflight"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Credentials", "true")  # クレデンシャル対応
    response.status_code = 200  # 明示的に200 OKを設定
    return response

def _corsify_actual_response(response, status=200):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, status

if __name__ == "__main__":
    init_db()  # データベース初期化
    app.run(host="0.0.0.0", port=5000, debug=True)