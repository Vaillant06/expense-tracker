/* EDIT PROFILE MODAL */

function openEditProfileModal() {
    document.getElementById("editProfileModal").style.display = "block";
}

function closeEditProfileModal() {
    document.getElementById("editProfileModal").style.display = "none";
}

window.onclick = (event) => {
    const editProfileModal = document.getElementById("editProfileModal");
    const budgetModal = document.getElementById("budgetModal");

    if (event.target === editProfileModal) editProfileModal.style.display = "none";
    if (event.target === budgetModal) budgetModal.style.display = "none";
};
