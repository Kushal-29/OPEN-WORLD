# 🌍 OpenWorld - Anonymous Video Chat App

OpenWorld is a real-time anonymous video chat application that connects strangers across the world instantly using WebRTC and Socket.IO.

Built with performance, scalability, and privacy in mind.

---

## ✨ Features

- 🎥 Real-time Video Chat (WebRTC)
- 🌐 Random User Matching
- ⚡ Instant Connection via Socket.IO
- 🔒 Anonymous Communication (No Login Required)
- ⏳ Ephemeral Sessions (No chat history stored)
- 🔄 Auto Reconnect to New Users
- 📡 Low-latency peer-to-peer communication

---

## 🧠 How It Works

1. User clicks **Start Chat**
2. Request is sent to the server via Socket.IO
3. Server checks:
   - If another user is waiting → connect instantly
   - Else → user is placed in queue
4. When 2 users are available:
   - Server matches them
   - WebRTC connection is established
5. Users can now **video chat in real-time**

---

## 🏗️ Tech Stack

### Frontend
- React.js
- WebRTC API
- Tailwind CSS

### Backend
- Node.js
- Express.js
- Socket.IO

### Real-Time Communication
- WebRTC (Peer-to-peer video/audio)
- STUN/TURN Servers

---

## 📁 Project Structure

```

OpenWorld/
│
├── client/        # React Frontend
├── server/        # Node.js Backend
├── public/        # Static assets
└── README.md

````

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/openworld.git
cd openworld
````

---

### 2. Install dependencies

#### Client

```bash
cd client
npm install
```

#### Server

```bash
cd ../server
npm install
```

---

### 3. Run the project

#### Start Backend

```bash
cd server
npm start
```

#### Start Frontend

```bash
cd client
npm start
```

---

## 🌐 Environment Variables

Create a `.env` file in server folder:

```env
PORT=5000
```

---

## 📡 WebRTC Configuration

You can use public STUN servers:

```js
const configuration = {
  iceServers: [
    { urls: "stun:stun.l.google.com:19302" }
  ]
};
```

---

## 🚀 Future Enhancements

* 🔐 End-to-End Encryption
* 🌍 Global Chat Rooms
* 🕶️ Anonymous Identity Layers
* 🚫 Moderation & Abuse Detection
* 📱 Mobile App (React Native)
* 🌐 Built-in VPN Requirement
* 💬 Text Chat + Media Sharing

---

## 🧪 Challenges Solved

* Handling real-time user matching
* Managing WebRTC peer connections
* Reducing latency in signaling
* Queue-based matchmaking system
* Handling disconnections gracefully

---

## 📸 Screenshots

*Add your screenshots here*

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 💡 Author

Developed with passion by [Your Name]

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

```

---

# ⚡ Now small improvements (important)

### 🔥 1. Replace these before pushing:
- `your-username`
- `Your Name`
- Add screenshots (VERY IMPORTANT for impact)

---

### 🔥 2. Add a **killer repo description**
On GitHub top:

> "Real-time anonymous video chat app using WebRTC & Socket.IO with instant stranger matching"

---

### 🔥 3. Add topics (tags)
```

webrtc
socket-io
video-chat
react
nodejs
real-time

```

---




