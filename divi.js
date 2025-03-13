document.addEventListener("DOMContentLoaded", function () {
    const payerSelect = document.getElementById("payer");
    const recipientList = document.getElementById("recipient-list");
    const resultList = document.getElementById("result-list");
    const summaryList = document.getElementById("summary-list");
    const shareableLink = document.getElementById("shareable-link");
    let transactions = [];
    
    // localStorage からデータ取得
    const groupUrl = localStorage.getItem("groupUrl");
    const groupName = localStorage.getItem("groupName");
    const members = JSON.parse(localStorage.getItem("members")) || [];

    const groupNameElement = document.getElementById("group-name");
    if (groupName) {
        groupNameElement.textContent = groupName;
      } else {
        groupNameElement.textContent = "No group name set"; // デフォルトテキスト
    }
    
    //もしデータがなければHomeへ
    if (!groupName || members.length === 0) {
        alert("No group data found. Returning to home.");
        window.location.href = "index.html";
        return;
    }
    // メンバー情報を支払者・受取者リストに反映
    members.forEach(member => {
        let option = document.createElement("option");
        option.value = member;
        option.textContent = member;
        payerSelect.appendChild(option);

        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = member;
        checkbox.name = "recipient";

        let label = document.createElement("label");
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(member));
        recipientList.appendChild(label);
    });

    // Purpose選択肢の設定
    const purposeSelect = document.getElementById("purpose");
    const customPurposeInput = document.getElementById("custom-purpose");

    // 目的が「Other」を選択した場合に、手動入力欄を表示
    purposeSelect.addEventListener("change", function () {
        if (purposeSelect.value === "Other") {
            customPurposeInput.style.display = "block";
        } else {
            customPurposeInput.style.display = "none";
        }
    });

    // 取引を追加するボタン
    document.getElementById("add-transaction-btn").addEventListener("click", function () {
        const amount = parseFloat(document.getElementById("amount").value);
        const currency = document.getElementById("currency").value;
        const payer = payerSelect.value;
        const recipients = Array.from(document.querySelectorAll("input[name='recipient']:checked")).map(cb => cb.value);
        const date = document.getElementById("transaction-date").value;
        let purpose = purposeSelect.value;

        // 「Other」が選択されている場合、手動で入力された目的を取得
        if (purpose === "Other") {
            purpose = customPurposeInput.value.trim();
        }

        if (amount && payer && recipients.length > 0 && date && purpose) {
            fetch("http://127.0.0.1:5000/transactions", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    groupUrl: groupUrl,
                    payer: payer,
                    recipients: recipients,
                    amount: amount.toFixed(2),
                    currency: currency,
                    purpose: purpose,
                    date: date
                })
            })
            .then(response => response.json())
            .then(data => {
                transactions.push(data);  // 保存された取引データをローカルに追加
                updateTransactionList();  // 取引リストを更新
                calculateFinalBalances(); // 最終的な清算結果を計算
                document.getElementById("transaction-form").reset();
            })
            .catch(error => {
                let errorMessage = "取引の保存に失敗しました。";
                if (error instanceof TypeError) {
                    errorMessage = "ネットワークエラーが発生しました。インターネット接続を確認してください。";
                } else if (error.message.startsWith("HTTP error!")) {
                    errorMessage = `サーバーエラーが発生しました: ${error.message.split("status: ")[1]}`;
                }
                alert(errorMessage);
            });
        } else {
            alert("Please fill all fields correctly.");
        }
    });

    // 取引一覧の更新
    function updateTransactionList() {
        resultList.innerHTML = "";

        // 配列をコピーしてループ
        transactions.slice().forEach((txn, index) => {
            let resultItem = document.createElement("li");
            resultItem.textContent = `${txn.payer} paid ${txn.recipients.join(", ")} ${txn.amount} ${txn.currency} for ${txn.purpose} on ${txn.date}.`;
            
            // クリックで削除するイベントリスナーを追加
            resultItem.addEventListener("click", function () {
            if (confirm("Are you sure you want to delete this transaction?")) {
                transactions.splice(index, 1);
                updateTransactionList();
                calculateFinalBalances();
            }
        });
            // cursorをpointerに設定
            resultItem.classList.add("clickable");
            resultList.appendChild(resultItem);
        });
    }

    // 最終的な清算結果を計算
    function calculateFinalBalances() {
        const transactionsData = transactions.flatMap(({ payer, amount, recipients }) =>
            recipients.map(recipient => [payer, recipient, amount / recipients.length])
        );

        fetch("http://127.0.0.1:5000/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transactions: transactionsData })
        })
        .then(response => response.json())
        .then(data => {
            summaryList.innerHTML = "";

            if (!Array.isArray(data) || data.length === 0) {
                let item = document.createElement("li");
                item.textContent = "No transactions needed (everyone is settled).";
                summaryList.appendChild(item);
            } else {
                data.forEach(({ from, to, amount }) => {
                    let item = document.createElement("li");
                    item.textContent = `${from} → ${to} ${amount.toFixed(2)}€`;
                    summaryList.appendChild(item);
                });
            }
        })
        .catch(error => {
            let errorMessage = "清算結果の計算に失敗しました。";
            if (error instanceof TypeError) {
                errorMessage = "ネットワークエラーが発生しました。インターネット接続を確認してください。";
            } else if (error.message.startsWith("HTTP error!")) {
                errorMessage = `サーバーエラーが発生しました: ${error.message.split("status: ")[1]}`;
            }
            alert(errorMessage);
            summaryList.innerHTML = "<li>⚠️ エラーが発生しました。</li>";
        });
    }

    // URLを表示する部分
    document.getElementById("copy-btn").addEventListener("click", function () {
        // groupUrlがnullでないことを確認し、リンクを設定
        if (groupUrl) {
            shareableLink.value = groupUrl;  // groupUrlを表示する
        } else {
            alert("グループのURLが保存されていません");
            return;
        }
        // リンクを選択してコピー
        shareableLink.select();
        document.execCommand("copy");
        alert("Link copied to clipboard!");
    });

    // ページが読み込まれたときにURLが表示されるようにする
    window.addEventListener('load', function () {
        const shareableLink = document.getElementById("shareable-link");
    
        if (groupUrl) {
         shareableLink.value = groupUrl;  // ページが読み込まれた時点でURLを表示
        } else {
         shareableLink.value = "グループのURLが保存されていません";  // URLがない場合の表示
        }
    });
    
    // ページ読み込み時にデータを取得
    async function fetchTransactions() {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/transactions", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "Group-Url": groupUrl })
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const data = await response.json();
            transactions = data; // 取得した取引データをローカルに保存
            updateTransactionList(); // 取引リストを更新
        } catch (error) {
            let errorMessage = "取引データの読み込みに失敗しました。";
    
            if (error instanceof TypeError) {
                errorMessage = "ネットワークエラーが発生しました。インターネット接続を確認してください。";
            } else if (error.message.startsWith("HTTP error!")) {
                errorMessage = `サーバーエラーが発生しました: ${error.message.split("status: ")[1]}`;
            }
    
            alert(errorMessage);
        }
    }
    
    // 関数を呼び出す
    fetchTransactions();
    
    // fetch("http://127.0.0.1:5000/api/transactions", {
    //     method: "POST",
    //     headers: { "Content-Type": "application/json" },
    //     body: JSON.stringify({ "Group-Url": groupUrl})
    // })
    // .then(response => response.json())
    // .then(data => {
    //     transactions = data; // 取得した取引データをローカルに保存
    //     updateTransactionList(); // 取引リストを更新
    // })
    // .catch(error => {
    //     let errorMessage = "取引データの読み込みに失敗しました。";
    //     if (error instanceof TypeError) {
    //         errorMessage = "ネットワークエラーが発生しました。インターネット接続を確認してください。";
    //     } else if (error.message.startsWith("HTTP error!")) {
    //         errorMessage = `サーバーエラーが発生しました: ${error.message.split("status: ")[1]}`;
    //     }
    //     alert(errorMessage);
    // });
});