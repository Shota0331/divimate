# DiviMate - Easy Expense Splitting App

DiviMate は、割り勘を簡単に管理するためのWebアプリケーションです。登録不要で使える手軽さと、シンプルな操作性が特徴です。友人との旅行、食事会、イベントなど、どんな場面でも素早く支払いを分割できます。

![DiviMate App](static/img/432.png)

## 主な機能

- **アカウント登録不要**: メールアドレスやパスワードの登録なしで即座に利用可能
- **グループ作成**: 支払いを分け合う友人グループを簡単に作成
- **取引記録**: 誰が誰のために何を支払ったかを記録
- **最適計算**: 最も効率的な精算方法を自動計算
- **シェアリンク**: QRコード付きの共有リンクで簡単にグループに招待
- **マルチデバイス対応**: どのデバイスからでもアクセス可能

## 技術スタック

- **フロントエンド**: HTML, CSS, JavaScript
- **バックエンド**: Python, Flask
- **データベース**: SQLite
- **その他**: UUID, QRコード生成

## プロジェクト構造

```
divimate/
├── divi.py                 # メインアプリケーションファイル
├── requirements.txt        # 依存パッケージリスト
├── README.md               # このファイル
├── instance/               # データベースファイル
│   └── group_transactions.db
├── static/                 # 静的ファイル
│   ├── css/                # スタイルシート
│   │   ├── style.css       # ホームページ用スタイル
│   │   └── divi.css        # グループページ用スタイル
│   └── img/                # 画像ファイル
│       ├── 432.png         # メイン画像
│       ├── calculator.png  # 機能説明用画像
│       ├── share.png       # 機能説明用画像
│       └── start.png       # 機能説明用画像
└── templates/              # HTMLテンプレート
    ├── index.html          # ホームページ
    ├── divi.html           # グループページ
    ├── impressum.html      # Impressum (法的情報)
    └── privacy.html        # プライバシーポリシー
```

## セットアップ方法

### 前提条件

- Python 3.7以上
- pip (Pythonパッケージマネージャー)

### インストール手順

1. リポジトリをクローン
   ```bash
   git clone https://github.com/yourusername/divimate.git
   cd divimate
   ```

2. 仮想環境を作成して有効化（推奨）
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linuxの場合
   # または
   venv\Scripts\activate  # Windowsの場合
   ```

3. 依存パッケージをインストール
   ```bash
   pip install flask flask-cors flask-sqlalchemy
   # または
   pip install -r requirements.txt
   ```

4. アプリケーションを実行
   ```bash
   python divi.py
   ```

5. ブラウザで `http://localhost:5000` にアクセス

## 使い方

### グループの作成

1. トップページでグループ名を入力
2. メンバーを追加（「Add Member」ボタンでメンバーを増やせます）
3. 「Create Group」ボタンをクリック
4. 自動的に共有可能なURLが生成されます

### 支出の記録

1. 支払った人（Payer）を選択
2. 受取人（Recipients）をチェック
3. 金額と目的を入力
4. 「Add Transaction」ボタンをクリック

### 結果の確認・共有

- 画面下部に最も効率的な精算方法が表示されます
- 「Copy Link」ボタンでグループのURLをコピー
- QRコードをスキャンして友人と共有


