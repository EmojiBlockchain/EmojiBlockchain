document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ explorer_script.js loaded!");

    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("searchInput");
    const resultsContainer = document.getElementById("searchResults");

    if (!searchForm || !searchInput || !resultsContainer) {
        console.error("❌ Missing essential elements! Check HTML.");
        return;
    }

    searchForm.addEventListener("submit", function (e) {
        e.preventDefault();
        let query = searchInput.value.trim();
        if (query === "") {
            console.warn("⚠️ Empty search query!");
            return;
        }

        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log("🔎 Search results:", data);
                displayResults(data);
            })
            .catch(error => console.error("❌ Search error:", error));
    });

    function displayResults(results) {
        resultsContainer.innerHTML = ""; // Clear previous results

        if (!Array.isArray(results) || results.length === 0) {
            resultsContainer.innerHTML = "<p>❌ No results found.</p>";
            return;
        }

        results.forEach(result => {
            console.log("🔍 Processing result:", result);

            let sender = result.sender ? `@${result.sender}` : "❌ Unknown Sender";
            let receiver = result.receiver ? `@${result.receiver}` : "❌ Unknown Receiver";
            let amount = result.amount ? `${result.amount}🔥` : "❌ No Amount";
            let fee = result.fee ? `${result.fee}🔥` : "❌ No Fee";
            let tx_hash = result.tx_hash ? result.tx_hash : null;
            let block = result.block ? `#${result.block}` : "❌ No Block Number";

            // 🔥 Log missing data for debugging
            if (!result.sender) console.warn("⚠️ Missing sender in:", result);
            if (!result.receiver) console.warn("⚠️ Missing receiver in:", result);
            if (!result.tx_hash) console.warn("⚠️ Missing tx_hash in:", result);
            if (!result.block) console.warn("⚠️ Missing block number in:", result);

            // 🛠 If the result is a **block search**, handle separately
            if (!tx_hash && result.block) {
                let blockHTML = `
                    <div class="block-result">
                        🧱 <strong>Block ${block}</strong>
                        | 🔗 Hash: <strong>${result.hash || "❌ No Hash"}</strong>
                    </div>`;
                resultsContainer.innerHTML += blockHTML;
                return;
            }

            // 🛠 Skip invalid transaction entries
            if (!tx_hash && sender === "❌ Unknown Sender") {
                return;
            }

            let resultHTML = `
                <div class="transaction">
                    🚀 <strong>${sender}</strong> ➡️ <strong>${receiver}</strong> 
                    | 💰 Amount: <strong>${amount}</strong> 
                    | 💵 Fee: <strong>${fee}</strong> 
                    | 🔑 Tx Hash: <a href="#" onclick="searchTransactions('${tx_hash}')">${tx_hash || "❌ No Tx Hash"}</a>
                    | 📦 Block: ${block}
                </div>`;
            resultsContainer.innerHTML += resultHTML;
        });
    }
});
