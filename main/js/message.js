async function openForm() {
    const closeFormButton = document.getElementById("closeFormButton");
    const messageForm = document.getElementById("messageForm");
    const messageFormElement = document.getElementById("messageFormElement");

    closeFormButton.addEventListener("click", () => {
        messageForm.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === messageForm) {
            messageForm.style.display = "none";
        }
    });

    messageForm.style.display = "flex";
}
