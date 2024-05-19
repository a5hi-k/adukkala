function openChat() {
    document.getElementById("chat-box").style.display = "block";
    }

    function closeChat() {
    document.getElementById("chat-box").style.display = "none";
    }
    

    function sendMessage() {
    var userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;
    appendMessage("user", userInput);

    // Send message to Django backend
    fetch('/chatbot/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'message=' + encodeURIComponent(userInput),
    })
    .then(response => response.json())
    .then(data => {
        // Handle response from Django backend (if needed)
        // For demonstration, let's just append the bot's reply to the chat
        appendMessage("bot", data.reply);
        // Add audio play button
        // addAudioWidget(data.reply);
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle error (if needed)
    });

    document.getElementById("user-input").value = "";
    }


    function appendMessage(role, message) {
    var chatBody = document.getElementById("chat-body");
    var messageElement = document.createElement("div");
    messageElement.classList.add("message", role);
    
    // Add icon or symbol based on the message role
    var icon = role === "user" ? "👤" : "🤖";
    
    // Append the message with the icon or symbol
    messageElement.innerHTML = `<span class="message-icon">${icon}</span> ${message}`;
    
    chatBody.appendChild(messageElement);
    }


    // function addAudioWidget(text) {
    //     var chatBody = document.getElementById("chat-body");
    //     var audioElement = document.createElement("audio");
    //     audioElement.controls = true;
      
    //     // Convert text to speech using SpeechSynthesis
    //     var speechSynthesisUtterance = new SpeechSynthesisUtterance(text);
    //     window.speechSynthesis.speak(speechSynthesisUtterance);
      
    //     audioElement.addEventListener('play', function() {
    //       window.speechSynthesis.speak(speechSynthesisUtterance);
    //     });
      
    //     audioElement.addEventListener('pause', function() {
    //       window.speechSynthesis.cancel();
    //     });
      
    //     var audioContainer = document.createElement("div");
    //     audioContainer.appendChild(audioElement);
      
    //     chatBody.appendChild(audioContainer);
    //   } 