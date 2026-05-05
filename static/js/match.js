/**
 * MATCH.JS - Video Chat WebRTC Implementation
 * Handles peer-to-peer video chat with Socket.IO signaling
 * Uses global window.Socket from socket.js
 */

console.log("✅ match.js loaded");

// ==================== GLOBAL STATE ====================
let localStream = null;
let peerConnection = null;
let currentRoom = null;
let currentStrangerId = null;
let isSearching = false;

const config = {
    iceServers: [
        { urls: ['stun:stun.l.google.com:19302'] },
        { urls: ['stun:stun1.l.google.com:19302'] }
    ]
};

// ==================== DOM ELEMENTS ====================
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const startBtn = document.getElementById('startBtn');
const skipBtn = document.getElementById('skipBtn');
const endBtn = document.getElementById('endBtn');
const addFriendBtn = document.getElementById('addFriendBtn');
const stopSearchBtn = document.getElementById('stopSearchBtn');
const statusText = document.getElementById('status');

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', async () => {
    console.log("🎬 Match page initializing...");
    
    // Check socket connection
    if (!window.Socket) {
        console.warn("⚠️ Socket not available yet, waiting...");
        return;
    }

    const socket = window.Socket;
    console.log("✅ Socket connected:", socket.id);

    // Get local media stream
    await initLocalStream();

    // ==================== SOCKET EVENTS ====================

    // Match confirmed - both users connected
    socket.on('match_confirmed', (data) => {
        console.log("🎉 Match confirmed!", data);
        currentRoom = data.room;
        currentStrangerId = data.stranger_id;
        isSearching = false;

        statusText.textContent = `Connected with ${data.stranger_name}!`;

        // Show appropriate buttons
        startBtn.style.display = 'none';
        stopSearchBtn.style.display = 'none';
        skipBtn.style.display = 'inline-block';
        endBtn.style.display = 'inline-block';
        addFriendBtn.style.display = 'inline-block';

        // Initialize WebRTC
        if (data.your_role === 'initiator') {
            console.log("📤 I'm the initiator, creating offer...");
            createPeerConnection('initiator');
        } else {
            console.log("📥 I'm the receiver, waiting for offer...");
            createPeerConnection('receiver');
        }
    });

    // Receive offer from peer
    socket.on('webrtc_offer', async (data) => {
        console.log("📤 Received offer from peer");
        try {
            if (!peerConnection) {
                createPeerConnection('receiver');
            }

            const offer = new RTCSessionDescription(data.offer);
            await peerConnection.setRemoteDescription(offer);

            // Create and send answer
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);

            socket.emit('webrtc_answer', {
                room: currentRoom,
                answer: answer
            });

            console.log("✅ Answer sent");
        } catch (error) {
            console.error("❌ Error handling offer:", error);
        }
    });

    // Receive answer from peer
    socket.on('webrtc_answer', async (data) => {
        console.log("📥 Received answer from peer");
        try {
            if (peerConnection) {
                const answer = new RTCSessionDescription(data.answer);
                await peerConnection.setRemoteDescription(answer);
                console.log("✅ Remote description set");
            }
        } catch (error) {
            console.error("❌ Error handling answer:", error);
        }
    });

    // Receive ICE candidate
    socket.on('webrtc_ice_candidate', async (data) => {
        console.log("🧊 Received ICE candidate");
        try {
            if (peerConnection && data.candidate) {
                const candidate = new RTCIceCandidate(data.candidate);
                await peerConnection.addIceCandidate(candidate);
            }
        } catch (error) {
            console.error("❌ Error adding ICE candidate:", error);
        }
    });

    // Stranger disconnected
    socket.on('stranger_disconnected', (data) => {
        console.log("🔴 Stranger disconnected");
        cleanupVideo();
        statusText.textContent = data.message || "Stranger left the chat";
        startBtn.style.display = 'inline-block';
        stopSearchBtn.style.display = 'none';
        skipBtn.style.display = 'none';
        endBtn.style.display = 'none';
        addFriendBtn.style.display = 'none';
        currentRoom = null;
        currentStrangerId = null;
    });

    // Stranger skipped
    socket.on('stranger_skipped', (data) => {
        console.log("⏭️ Stranger skipped");
        cleanupVideo();
        statusText.textContent = data.message || "Stranger skipped";
        startBtn.style.display = 'inline-block';
        stopSearchBtn.style.display = 'none';
        skipBtn.style.display = 'none';
        endBtn.style.display = 'none';
        addFriendBtn.style.display = 'none';
        currentRoom = null;
        currentStrangerId = null;
    });

    // Status update
    socket.on('status', (message) => {
        console.log("📢 Status:", message);
        statusText.textContent = message;
    });

    // Friend added notification
    socket.on('friend_added_notification', (data) => {
        console.log("👥 Friend added:", data);
        statusText.textContent = `✅ Added ${data.from_name} as friend!`;
    });

    // Error
    socket.on('error', (message) => {
        console.error("❌ Socket error:", message);
        statusText.textContent = `Error: ${message}`;
    });

    // ==================== BUTTON HANDLERS ====================

    startBtn.addEventListener('click', () => {
        console.log("▶️ Start button clicked");
        if (!isSearching) {
            isSearching = true;
            startBtn.style.display = 'none';
            stopSearchBtn.style.display = 'inline-block';
            socket.emit('start_search');
        }
    });

    stopSearchBtn.addEventListener('click', () => {
        console.log("🛑 Stop Search button clicked");
        if (isSearching) {
            isSearching = false;
            socket.emit('end_chat');
            stopSearchBtn.style.display = 'none';
            startBtn.style.display = 'inline-block';
            statusText.textContent = '📱 Click "Start" to find a stranger';
        }
    });

    skipBtn.addEventListener('click', () => {
        console.log("⏭️ Skip button clicked");
        cleanupVideo();
        socket.emit('skip_stranger');
        skipBtn.style.display = 'none';
        endBtn.style.display = 'none';
        addFriendBtn.style.display = 'none';
        stopSearchBtn.style.display = 'inline-block';
    });

    endBtn.addEventListener('click', () => {
        console.log("🛑 End button clicked");
        cleanupVideo();
        socket.emit('end_chat');
        endBtn.style.display = 'none';
        skipBtn.style.display = 'none';
        stopSearchBtn.style.display = 'none';
        addFriendBtn.style.display = 'none';
        startBtn.style.display = 'inline-block';
        statusText.textContent = '📱 Click "Start" to find a stranger';
    });

    addFriendBtn.addEventListener('click', () => {
        console.log("❤️ Add friend clicked");
        if (currentStrangerId && currentRoom) {
            socket.emit('send_friend_request_during_chat', {
                room: currentRoom,
                stranger_id: currentStrangerId
            });
        }
    });

    console.log("✅ Match page ready");
});

// ==================== WEBRTC FUNCTIONS ====================

/**
 * Initialize local media stream
 */
async function initLocalStream() {
    try {
        console.log("🎥 Requesting camera/mic...");

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('SecureContextError');
        }

        localStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: true
        });

        console.log("✅ Local stream obtained");
        localVideo.srcObject = localStream;

        // Set video to play
        localVideo.onloadedmetadata = () => {
            console.log("🎬 Local video playing");
            localVideo.play();
        };
    } catch (error) {
        console.error("❌ Error getting media:", error);
        if (error.message === 'SecureContextError') {
            alert("❌ Camera access denied. This feature works only on 'localhost' or secured (HTTPS) connections. If you are on LAN, please use HTTPS.");
        } else if (error.name === 'NotAllowedError') {
            alert("❌ Camera/Microphone access denied. Please allow access in browser settings.");
        } else if (error.name === 'NotFoundError') {
            alert("❌ No camera/microphone found. Please check your devices.");
        } else {
            alert(`❌ Error accessing media: ${error.message}`);
        }
    }
}

/**
 * Create peer connection
 */
function createPeerConnection(role) {
    try {
        console.log(`🔗 Creating peer connection (${role})...`);

        peerConnection = new RTCPeerConnection({ iceServers: config.iceServers });

        // Add local stream tracks
        if (localStream) {
            localStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, localStream);
                console.log(`✅ Added ${track.kind} track`);
            });
        }

        // Handle remote stream
        peerConnection.ontrack = (event) => {
            console.log("📹 Received remote track:", event.track.kind);
            if (event.streams && event.streams[0]) {
                remoteVideo.srcObject = event.streams[0];
                remoteVideo.onloadedmetadata = () => {
                    console.log("🎬 Remote video playing");
                    remoteVideo.play();
                };
            }
        };

        // Handle ICE candidates
        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                console.log("🧊 Sending ICE candidate");
                window.Socket.emit('webrtc_ice_candidate', {
                    room: currentRoom,
                    candidate: event.candidate
                });
            }
        };

        // Handle connection state changes
        peerConnection.onconnectionstatechange = () => {
            console.log("🔌 Connection state:", peerConnection.connectionState);
            if (peerConnection.connectionState === 'failed') {
                console.warn("⚠️ Connection failed, attempting restart...");
                peerConnection.restartIce();
            }
        };

        // Handle ICE state changes
        peerConnection.oniceconnectionstatechange = () => {
            console.log("❄️ ICE state:", peerConnection.iceConnectionState);
        };

        // If initiator, create and send offer
        if (role === 'initiator') {
            createAndSendOffer();
        }

        console.log("✅ Peer connection created");
    } catch (error) {
        console.error("❌ Error creating peer connection:", error);
    }
}

/**
 * Create and send offer (initiator only)
 */
async function createAndSendOffer() {
    try {
        console.log("📤 Creating offer...");
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        window.Socket.emit('webrtc_offer', {
            room: currentRoom,
            offer: offer
        });

        console.log("✅ Offer sent");
    } catch (error) {
        console.error("❌ Error creating offer:", error);
    }
}

/**
 * Cleanup video streams
 */
function cleanupVideo() {
    try {
        console.log("🧹 Cleaning up video...");

        // Close peer connection
        if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
            console.log("✅ Peer connection closed");
        }

        // Clear remote video
        remoteVideo.srcObject = null;

        currentRoom = null;
        currentStrangerId = null;
    } catch (error) {
        console.error("❌ Error cleaning up:", error);
    }
}

// ==================== PAGE UNLOAD ====================
window.addEventListener('beforeunload', () => {
    if (peerConnection) {
        peerConnection.close();
    }
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
});

console.log("✅ match.js initialization complete");