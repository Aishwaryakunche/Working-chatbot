const sendchtbtn = document.querySelector(".chat-input span");
const inputbtn = document.querySelector(".chat-input textarea");
const chatbox = document.querySelector(".chatbox");
const openchtbot = document.querySelector("body");
const closebtn = document.querySelector(".chatbot header .close-btn");
const chttgler = document.querySelector(".chatbot-toggler");

const showingcht = () => {
    openchtbot.classList.toggle("show");
}

const createchatli = (message, className) => {
    const chatli = document.createElement("li");
    chatli.classList.add("chat", className);
    let chatcont = className === "outgoing" ? `<p></p>` : `<span><img src="hire.jpeg" alt="logo"></span><p></p>`;
    chatli.innerHTML = chatcont;
    chatli.querySelector("p").textContent = message;
    return chatli;
}

const sendMessageToBackend = (message) => {
    fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        chatbox.appendChild(createchatli(data.response, "incoming"));
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

const handlechat = () => {
    let usermsg = inputbtn.value.trim();
    if (!usermsg) return;
    inputbtn.value = "";
    chatbox.appendChild(createchatli(usermsg, "outgoing"));
    sendMessageToBackend(usermsg);
    setTimeout(() => inputbtn.focus(), 0); // Return focus to the textarea after appending the message
}

const handle = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Prevent newline on Enter
        let usermsg = inputbtn.value.trim();
        if (!usermsg) return;
        inputbtn.value = "";
        chatbox.appendChild(createchatli(usermsg, "outgoing"));
        sendMessageToBackend(usermsg);
        setTimeout(() => inputbtn.focus(), 0); // Return focus to the textarea after appending the message
    }
}

sendchtbtn.addEventListener("click", handlechat);
inputbtn.addEventListener("keypress", handle);
closebtn.addEventListener("click", showingcht);
chttgler.addEventListener("click", showingcht);
