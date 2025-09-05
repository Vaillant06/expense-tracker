function openModal() {
    document.getElementById("budgetModal").style.display = "block";
}

function closeModal() {
    document.getElementById("budgetModal").style.display = "none";
}

function saveBudget() {
    let newBudget = document.getElementById("budgetInput").value;
    if (newBudget) {
        document.getElementById("budgetDisplay").innerText = "Budget: Rs. " + newBudget;
        // send AJAX/Fetch request to backend here
        closeModal();
    }
}