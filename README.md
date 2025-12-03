# RoadVision AI – Video Management System with AI Integration

A lightweight Video Management System (VMS) that can handle multiple video streams while running AI models such as road detection and crack/pothole analysis.  
Built with **FastAPI**, **React**, **OpenCV**, and **YOLOv8**.

---

## 🚀 Features

### 🎥 Multi-Stream Input Handling
- Supports more than 10 input sources:
  - Video files (`.mp4`, `.avi`)
  - CCTV/IP Camera (RTSP/HTTP streams)
  - Local camera feeds
  - Image folder loops
- Streams run in parallel using **multithreading**.

### 🧠 AI Model Integration
- Plug-and-play model design
- Available models:
  - `road_detector` – YOLOv8
  - `crack_detector` – Crack/pothole analysis using hybrid edge detection
- Models can be enabled/disabled per stream at runtime.

### 🗄 Backend (FastAPI)
- REST API for managing streams
- SQLite database for storing inference results
- Thumbnail endpoint for live preview
- ThreadPoolExecutor for model inference scheduling
- Safe async broadcasting for WebSocket integration

### 🖥 Frontend (React)
- Command-center themed dashboard
- List of active streams
- Real-time detection JSON panel
- Animated alert banners
- Realtime logs at the bottom
- Add/Delete stream functionality

---

## 📂 Project Structure

roadvision/
│── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── stream_manager.py
│ │ ├── ai_models.py
│ │ ├── crud.py
│ │ ├── db.py
│ │ ├── models.py
│ │ └── schemas.py
│ ├── venv/
│ └── requirements.txt
│
│── frontend/
│ ├── src/
│ │ ├── pages/MonitoringCenter.jsx
│ │ ├── api/api.js
│ │ ├── App.js
│ │ └── monitoring.css
│ ├── package.json
│ └── public/

## 📂 Project Structure

