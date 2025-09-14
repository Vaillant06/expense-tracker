/* FLASH MESSAGES */

setTimeout(() => {
    const flashMessages = document.getElementById("flash-messages");
    if (flashMessages) {
      flashMessages.style.transition = "opacity 0.5s ease";
      flashMessages.style.opacity = "0";
      setTimeout(() => flashMessages.remove(), 500);
    }
}, 3000);
