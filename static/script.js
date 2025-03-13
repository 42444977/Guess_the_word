document.getElementById("create-room-btn").addEventListener("click", function () {
    let username = document.getElementById("create-username").value;
    let roomCodeInput = document.getElementById("room-code").value;
    let word = document.getElementById("word").value;

    if (!username || !word) {
        alert("請輸入使用者名稱和單字！");
        return;
    }

    fetch("/create_room", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(username)}&room_code=${roomCodeInput}&word=${encodeURIComponent(word)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.room_code) {
            alert(`房間創建成功！房間代碼：${data.room_code}`);
            window.location.href = `/game?room_code=${data.room_code}&username=${encodeURIComponent(username)}`;
        } else {
            alert("房間創建失敗！");
        }
    })
    .catch(error => console.error("錯誤:", error));
});

document.getElementById("join-room-btn").addEventListener("click", function () {
    let username = document.getElementById("join-username").value;
    let roomCode = document.getElementById("room-code-join").value;

    if (!username || !roomCode) {
        alert("請輸入使用者名稱和房間代碼！");
        return;
    }

    fetch("/join_room", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(username)}&room_code=${roomCode}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("成功加入房間！");
            window.location.href = `/game?room_code=${roomCode}&username=${encodeURIComponent(username)}`;
        } else {
            alert("加入房間失敗！");
        }
    })
    .catch(error => console.error("錯誤:", error));
});