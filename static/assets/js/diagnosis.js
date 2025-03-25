function createVideoUploadSection(tabId, title) {
    return `
        <h4 class="text-center">${title}</h4>

        <div class="mb-3 px-5">
            <label for="videoUpload${tabId}" class="form-label">Choose a Video File:</label>
            <input type="file" class="form-control pr-5 videoUpload" id="videoUpload${tabId}" accept="video/*" data-video-player="videoPlayer${tabId}" data-button-id="sendButton${tabId}" data-response-id="response${tabId}">
        </div>
        <div class="video-container">
            <div class="text-center mt-4">
                <video id="videoPlayer${tabId}" class="w-100" controls style="display: none;">
                    Your browser does not support the video tag.
                </video>
            </div>
        </div>

        <div class="text-center mt-3">
            <button class="btn btn-primary send-video" id="sendButton${tabId}" data-upload-id="videoUpload${tabId}" style="display: none;">Analyze Video</button>
        </div>

        <!-- Response div to display Flask response -->
        <div id="response${tabId}" class="text-center mt-3 response-message"></div>
    `;
}

document.addEventListener("DOMContentLoaded", function () {
    const tabsConfig = [
        { id: "BodyMotionAnalysis", title: "Body Motion Analysis" },
        { id: "HandTremorAnalysis", title: "Hand Tremor Analysis" }
    ];

    tabsConfig.forEach(tab => {
        const tabElement = document.getElementById(tab.id);
        if (tabElement) {
            tabElement.innerHTML = createVideoUploadSection(tab.id, tab.title);
        }
    });

    // Event Listener for Video Upload (Show Video + Show Button)
    document.querySelectorAll(".videoUpload").forEach(input => {
        input.addEventListener("change", function(event) {
            const file = event.target.files[0];
            if (file) {
                const videoPlayerId = event.target.getAttribute("data-video-player");
                const buttonId = event.target.getAttribute("data-button-id");
                const videoPlayer = document.getElementById(videoPlayerId);
                const sendButton = document.getElementById(buttonId);
                //reset the response div
                const responseDivId = event.target.getAttribute("data-response-id");
                const responseDiv = document.getElementById(responseDivId);
                responseDiv.innerHTML = "";

                videoPlayer.src = URL.createObjectURL(file);
                videoPlayer.style.display = "block";
                videoPlayer.style.width = "360px";
                videoPlayer.style.height = "240px";

                sendButton.style.display = "inline-block"; // Show the button when file is selected


            }
        });
    });

    // Event Listener for Sending Video to Flask Server
    document.querySelectorAll(".send-video").forEach(button => {
        button.addEventListener("click", function() {
            const uploadId = this.getAttribute("data-upload-id");
            const fileInput = document.getElementById(uploadId);
            const file = fileInput.files[0];
            const responseDivId = fileInput.getAttribute("data-response-id");
            const responseDiv = document.getElementById(responseDivId);

            //disable the button
            button.disabled = true;

            if (!file) {
                responseDiv.innerHTML = `<p class="text-danger">Please select a video file before submitting.</p>`;
                return;
            }

            responseDiv.innerHTML = `<p class="text-info">Analyzing video... Please wait.</p>`;

            const formData = new FormData();
            formData.append("video", file);
            formData.append("analysis_type", uploadId.replace("videoUpload", "")); // Send tab ID as analysis type

            fetch(`/analyze_video/${uploadId}`, {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Convert dictionary to key-value HTML format
                let formattedMessage = "";
                for (const [key, value] of Object.entries(data.message)) {
                    formattedMessage += `<p><strong>${key}:</strong> ${value}</p>`;
                }

                // Update the responseDiv without curly brackets
                responseDiv.innerHTML = `<h4 class="text-success">Analysis Result:</h4>${formattedMessage}`;

                // Enable the button
                button.disabled = false;
            })

            .catch(error => {
                console.error("Error:", error);
                responseDiv.innerHTML = `<p class="text-danger">Error Analyzing video.</p>`;
                //enable the button
                button.disabled = false;
            });
        });
    });
});

function createAudioUploadSection(tabId, title) {
    return `
        <h4 class="text-center">${title}</h4>

        <div class="mb-3 px-5">
            <label for="audioUpload${tabId}" class="form-label">Choose an Audio File:</label>
            <input type="file" class="form-control pr-5 audioUpload" id="audioUpload${tabId}" accept="audio/*" data-audio-player="audioPlayer${tabId}" data-button-id="sendButton${tabId}" data-response-id="response${tabId}">
        </div>

        <div class="text-center mt-4">
            <audio id="audioPlayer${tabId}" class="w-100" controls style="display: none;">
                Your browser does not support the audio tag.
            </audio>
        </div>

        <div class="text-center mt-3">
            <button class="btn btn-primary send-audio" id="sendButton${tabId}" data-upload-id="audioUpload${tabId}" style="display: none;">Analyze Audio</button>
        </div>

        <!-- Response div to display Flask response -->
        <div id="response${tabId}" class="text-center mt-3 response-message"></div>
    `;
}

document.addEventListener("DOMContentLoaded", function () {
    const audioTabsConfig = [
        { id: "SpeechSemanticsAnalysis", title: "Speech Semantics Analysis" },
        { id: "SpeechPhonationAnalysis", title: "Speech Phonation Analysis" },
        { id: "SpeechArticulationProsodyAnalysis", title: "Speech Articulation & Prosody Analysis" },
    ];

    audioTabsConfig.forEach(tab => {
        const tabElement = document.getElementById(tab.id);
        if (tabElement) {
            tabElement.innerHTML = createAudioUploadSection(tab.id, tab.title);
        }
    });

    // Event Listener for Audio Upload (Show Audio Player + Show Button)
    document.querySelectorAll(".audioUpload").forEach(input => {
        input.addEventListener("change", function(event) {
            const file = event.target.files[0];
            if (file) {
                const audioPlayerId = event.target.getAttribute("data-audio-player");
                const buttonId = event.target.getAttribute("data-button-id");
                const audioPlayer = document.getElementById(audioPlayerId);
                const sendButton = document.getElementById(buttonId);

                audioPlayer.src = URL.createObjectURL(file);
                audioPlayer.style.display = "block";
                sendButton.style.display = "inline-block"; // Show the button when file is selected
            }
        });
    });

    // Event Listener for Sending Audio to Flask Server
    document.querySelectorAll(".send-audio").forEach(button => {
        button.addEventListener("click", function() {
            const uploadId = this.getAttribute("data-upload-id");
            const fileInput = document.getElementById(uploadId);
            const file = fileInput.files[0];
            const responseDivId = fileInput.getAttribute("data-response-id");
            const responseDiv = document.getElementById(responseDivId);
            //disable the button
            button.disabled = true;
            if (!file) {
                responseDiv.innerHTML = `<p class="text-danger">Please select an audio file before submitting.</p>`;
                return;
            }

            responseDiv.innerHTML = `<p class="text-info">Analyzing audio... Please wait.</p>`;

            const formData = new FormData();
            formData.append("audio", file);
            formData.append("analysis_type", uploadId.replace("audioUpload", "")); // Send tab ID as analysis type

            fetch(`/analyze_audio/${uploadId}`, {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {

                responseDiv.innerHTML = `<h4 class="text-success">Analysis Result: ${data.message}</h4>`;
                //enable the button
                button.disabled = false;
            })
            .catch(error => {
                console.error("Error:", error);
                responseDiv.innerHTML = `<p class="text-danger">Error Analyzing audio.</p>`;
                //enable the button
                button.disabled = false;
            });
        });
    });
});
