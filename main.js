
// Button Function
let memberCount = 1;

document.getElementById("add-member-btn").addEventListener("click", function() {
    memberCount++;
    const memberList = document.getElementById("member-list");

    const newMemberDiv = document.createElement("div");
    newMemberDiv.classList.add("form-member");

    const newLabel = document.createElement("label");
    newLabel.setAttribute("for", `member-${memberCount}`);
    newLabel.textContent = "Member";

    const inputContainer = document.createElement("div");
    inputContainer.classList.add("form-member_input");

    const newInput = document.createElement("input");
    newInput.setAttribute("id", `member-${memberCount}`);
    newInput.setAttribute("type", "text");
    newInput.setAttribute("placeholder", "New Member");

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Delete";
    removeBtn.classList.add("remove-btn");
    removeBtn.addEventListener("click", function() {
        memberList.removeChild(newMemberDiv);
    });

    // 入力欄とボタンを inputContainer に追加
    inputContainer.appendChild(newInput);
    inputContainer.appendChild(removeBtn);

    // newMemberDiv に label と inputContainer を追加
    newMemberDiv.appendChild(newLabel);
    newMemberDiv.appendChild(inputContainer);
    
    // メンバーリストに newMemberDiv を追加
    memberList.appendChild(newMemberDiv);
});

//「グループ作成」ボタンをクリックしたときの処理
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("save-group-btn").addEventListener("click", function (event) {

        const groupName = document.getElementById("name").value.trim();
        const memberInputs = document.querySelectorAll("#member-list input");
        const members = Array.from(memberInputs)
                            .map(input => input.value.trim())
                            .filter(name => name !== "");

        if (!groupName) {
            alert("Please enter a group name.");
            return;
        }
        if (members.length === 0) {
            alert("Please add at least one member.");
            return;
        }

        // グループ情報をベースにURLを生成
        const groupData = { name: groupName, members: members };
        const groupUrl = generateGroupUrl(groupData);

        // localStorage にデータを保存
        localStorage.setItem("groupUrl", groupUrl);
        localStorage.setItem("groupName", groupName);
        localStorage.setItem("members", JSON.stringify(members));

        // URLを画面に表示
        // displayGroupUrl(groupUrl);

        // 割り勘ページに移動
        window.location.href = "divi.html";
    });
});

// URLを生成する関数
function generateGroupUrl(groupData) {
    // groupName と members を URLのクエリパラメータに変換
    const baseUrl = window.location.origin + '/group';
    const params = new URLSearchParams({
        groupName: groupData.name,
        members: JSON.stringify(groupData.members)
    }).toString();
    
    return `${baseUrl}?${params}`;
}

// 生成したURLを画面に表示する関数
// function displayGroupUrl(groupUrl) {
//     const urlDisplayContainer = document.createElement('div');
//     urlDisplayContainer.classList.add('group-url-display');
    
//     const urlText = document.createElement('p');
//     urlText.textContent = `Your group URL: ${groupUrl}`;

//     const copyButton = document.createElement('button');
//     copyButton.textContent = 'Copy URL';
//     copyButton.addEventListener('click', () => {
//         navigator.clipboard.writeText(groupUrl).then(() => {
//             alert('URL copied to clipboard!');
//         });
//     });

//     urlDisplayContainer.appendChild(urlText);
//     urlDisplayContainer.appendChild(copyButton);
//     document.body.appendChild(urlDisplayContainer);
// }
