// ✅ Create a Wallet
function createWallet() {
    let username = document.getElementById("username").value.trim();

    if (!username) {
        alert("❌ Please enter a username.");
        return;
    }

    fetch("/create_wallet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("walletResult");
        
        if (data.error) {
            resultDiv.innerHTML = `<span style="color:red;">⚠ ${data.error}</span>`;
            return;
        }

        resultDiv.innerHTML = `
            ✅ Wallet Created! <br>
            <b>Public Key:</b> <span id="publicKey">${data.public_key}</span>
            <button class="copy-btn" onclick="copyToClipboard('publicKey')">📋 Copy</button>
            <br>
            <b>Private Key:</b> <span id="privateKey">${data.private_key}</span>
            <button class="copy-btn" onclick="copyToClipboard('privateKey')">📋 Copy</button>
        `;
    })
    .catch(error => console.error("❌ Error:", error));
}

// ✅ Function to Copy Text to Clipboard
function copyToClipboard(elementId) {
    let text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text);
    
    // ✅ Show Temporary Message
    let button = event.target;
    button.innerText = "✅ Copied!";
    setTimeout(() => button.innerText = "📋 Copy", 2000);
}

// ✅ Make functions globally accessible
window.createWallet = createWallet;
window.copyToClipboard = copyToClipboard;

// ✅ Send a Transaction
function sendTransaction() {
    let sender = document.getElementById("sender").value.trim();
    let privateKey = document.getElementById("privateKey").value.trim();
    let receiver = document.getElementById("receiver").value.trim();
    let amount = parseFloat(document.getElementById("amount").value.trim());

    if (!sender || !privateKey || !receiver || isNaN(amount) || amount <= 0) {
        alert("❌ Please fill in all fields correctly.");
        return;
    }

    fetch("/send_transaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            sender: sender,
            private_key: privateKey,
            receiver: receiver,
            amount: amount
        })
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("transactionResult");
        if (data.error) {
            resultDiv.innerHTML = `<span style="color:red;">⚠ ${data.error}</span>`;
        } else {
            resultDiv.innerHTML = `✅ Transaction Successful! <br> 
                🔗 TX Hash: <a href="http://127.0.0.1:5000/search?q=${data.tx_hash}" 
                target="_blank" style="color: #ffcc00; font-weight: bold;">
                    ${data.tx_hash}
                </a>`;
        }
    })
    .catch(error => {
        console.error("❌ Error:", error);
        document.getElementById("transactionResult").innerHTML = `<span style="color:red;">❌ Transaction failed.</span>`;
    });
}

// ✅ Make function globally accessible
window.sendTransaction = sendTransaction;

// ✅ Check Wallet Balance
function checkBalance() {
    let username = document.getElementById("checkUsername").value.trim();

    if (!username) {
        alert("❌ Please enter a username.");
        return;
    }

    fetch("/check_balance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("balanceResult");
        if (data.error) {
            resultDiv.innerHTML = `<span style="color:red;">⚠ ${data.error}</span>`;
        } else {
            resultDiv.innerHTML = `💰 Balance: <b>${data.balance}</b>`;
        }
    })
    .catch(error => console.error("❌ Error:", error));
}

// ✅ Make sure the function is globally available
window.checkBalance = checkBalance;

// ✅ Copy Private Key to Clipboard
function copyToClipboard() {
    let privateKey = document.getElementById("privateKey").innerText;
    navigator.clipboard.writeText(privateKey);
    alert("✅ Private Key copied to clipboard!");
}

// ✅ Find Username by Public Key
function findUsername() {
    let publicKey = document.getElementById("publicKey").value.trim();

    if (!publicKey) {
        alert("❌ Please enter a public key.");
        return;
    }

    fetch("/find_username", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ public_key: publicKey })
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("findUsernameResult");
        if (data.username) {
            resultDiv.innerHTML = `✅ Username: ${data.username}`;
        } else {
            resultDiv.innerHTML = `❌ Error: ${data.error}`;
        }
    })
    .catch(error => console.error("❌ Error:", error));
}

// ✅ Recover Wallet with Private Key
function recoverWallet() {
    let newUsername = document.getElementById("recoverUsername").value.trim();
    let privateKey = document.getElementById("recoverPrivateKey").value.trim();

    if (!newUsername || !privateKey) {
        alert("❌ Please enter both a username and private key.");
        return;
    }

    fetch("/recover_wallet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: newUsername, private_key: privateKey })
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("recoverWalletResult");
        if (data.message) {
            resultDiv.innerHTML = `✅ ${data.message}`;
        } else {
            resultDiv.innerHTML = `❌ Error: ${data.error}`;
        }
    })
    .catch(error => console.error("❌ Error:", error));
}

async function stakeEMOJI() {
    let username = document.getElementById("stakeUsername").value;
    let privateKey = document.getElementById("stakePrivateKey").value;
    let amount = parseFloat(document.getElementById("stakeAmount").value);

    if (amount < 1000) {
        document.getElementById("stakeResult").innerHTML = "❌ Minimum stake is 1000🔥";
        return;
    }

    let response = await fetch("/stake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, privateKey, amount })
    });

    let data = await response.json();
    document.getElementById("stakeResult").innerHTML = data.message;
}

async function unstakeEMOJI() {
    let username = document.getElementById("unstakeUsername").value;
    let privateKey = document.getElementById("unstakePrivateKey").value;
    let amount = parseFloat(document.getElementById("unstakeAmount").value);

    let response = await fetch("/unstake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, privateKey, amount })
    });

    let data = await response.json();
    document.getElementById("unstakeResult").innerHTML = data.message;
}

async function checkStakeBalance() {
    let username = document.getElementById("stakeBalanceUsername").value;

    let response = await fetch(`/stake_balance?username=${username}`);
    let data = await response.json();
    document.getElementById("stakeBalanceResult").innerHTML = `Staked: ${data.stake}🔥`;
}
