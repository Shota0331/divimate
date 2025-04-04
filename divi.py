import json
import uuid
from collections import defaultdict
from datetime import datetime

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///group_transactions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app, resources={r"/*": {"origins": ["https://divi-mate.com", "http://127.0.0.1:5501"]}})
db = SQLAlchemy(app)


# データモデルの定義
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_url = db.Column(db.String(200), nullable=False)
    payer = db.Column(db.String(100), nullable=False)
    recipients = db.Column(db.String(500), nullable=False)  # JSON文字列として保存
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(200))
    date = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "groupUrl": self.group_url,
            "payer": self.payer,
            "recipients": json.loads(self.recipients),
            "amount": self.amount,
            "currency": self.currency,
            "purpose": self.purpose,
            "date": self.date,
        }


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), unique=True, nullable=False)
    members = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/impressum")
def impressum():
    return render_template("impressum.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/create_group", methods=["POST"])
def create_group():
    try:
        group_name = request.form.get("group_name")
        members = request.form.getlist("members[]")

        if not group_name or not members:
            return render_template(
                "index.html", error="Group name and at least one member are required"
            )

        # フィルタリング: 空の値を除去
        members = [m.strip() for m in members if m.strip()]

        if not members:
            return render_template(
                "index.html", error="At least one valid member is required"
            )

        # UUIDを使用してユニークなURLを生成
        url = str(uuid.uuid4())

        # グループの保存
        new_group = Group(name=group_name, url=url, members=json.dumps(members))
        db.session.add(new_group)
        db.session.commit()

        # 割り勘ページにリダイレクト
        return redirect(url_for("show_group", group_url=url))
    except Exception as e:
        return render_template("index.html", error=str(e))


@app.route("/group/<group_url>")
def show_group(group_url):
    group = Group.query.filter_by(url=group_url).first_or_404()
    return render_template(
        "divi.html",
        group_name=group.name,
        members=json.loads(group.members),
        group_url=group_url,
    )


@app.route("/transactions", methods=["POST", "OPTIONS"])
def add_transaction():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    try:
        data = request.json
        if not all(
            key in data
            for key in (
                "groupUrl",
                "payer",
                "recipients",
                "amount",
                "currency",
                "purpose",
                "date",
            )
        ):
            return jsonify({"error": "Missing required fields"}), 400

        # 新しいトランザクションの作成
        transaction = Transaction(
            group_url=data["groupUrl"],
            payer=data["payer"],
            recipients=json.dumps(data["recipients"]),
            amount=data["amount"],
            currency=data["currency"],
            purpose=data["purpose"],
            date=data["date"],
        )

        # トランザクションをデータベースに保存
        db.session.add(transaction)
        db.session.commit()

        return _corsify_actual_response(jsonify(transaction.to_dict()), 201)
    except Exception as e:
        return _corsify_actual_response(jsonify({"error": str(e)}), 500)


@app.route("/api/transactions", methods=["POST", "OPTIONS"])
def get_transactions():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    try:
        body = request.get_json()
        group_url = body.get("Group-Url")

        # グループURLに基づいてトランザクションを取得
        transactions = Transaction.query.filter_by(group_url=group_url).all()
        return _corsify_actual_response(jsonify([t.to_dict() for t in transactions]))
    except Exception as e:
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
    """
    取引履歴から借金を精算するための最適な支払い方法を計算
    """
    balances = defaultdict(float)

    # 各ユーザーの収支を計算
    for payer, payee, amount in transactions:
        balances[payer] -= amount
        balances[payee] += amount

    # 債務者（マイナス残高）と債権者（プラス残高）を分類
    debtors = sorted(
        [(p, bal) for p, bal in balances.items() if bal < 0], key=lambda x: x[1]
    )
    creditors = sorted(
        [(p, bal) for p, bal in balances.items() if bal > 0],
        key=lambda x: x[1],
        reverse=True,
    )

    # 精算方法を計算
    results = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, d_amount = debtors[i]
        creditor, c_amount = creditors[j]

        payment = min(-d_amount, c_amount)
        results.append({"from": creditor, "to": debtor, "amount": round(payment, 2)})

        debtors[i] = (debtor, d_amount + payment)
        creditors[j] = (creditor, c_amount - payment)

        if abs(debtors[i][1]) < 0.01:
            i += 1
        if abs(creditors[j][1]) < 0.01:
            j += 1
    print("Calculated settlements:", results)
    return results


def _build_cors_preflight_response():
    response = jsonify({"message": "CORS Preflight"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add(
        "Access-Control-Allow-Credentials", "true"
    )  # クレデンシャル対応
    response.status_code = 200  # 明示的に200 OKを設定
    return response


def _corsify_actual_response(response, status=200):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, status


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # データベーステーブルの作成
    app.run(host="0.0.0.0", port=5000, debug=True)
