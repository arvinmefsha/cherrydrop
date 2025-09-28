# OwlHacks Delivery Platform

A peer-to-peer delivery platform for college students using a points-based system.

## Features

- User authentication with Temple.edu email verification
- Points-based delivery system (no real currency)
- Request deliveries from nearby establishments
- Deliver orders to earn points
- Real-time order tracking
- Photo confirmation for completed deliveries

## Tech Stack

### Frontend
- HTML5
- Tailwind CSS
- Vanilla JavaScript

### Backend
- Python
- FastAPI
- MongoDB Atlas
- JWT Authentication

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run the server: `uvicorn main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory
2. Open `index.html` in a browser or serve with a local server

## Project Structure

```
owlhacks-delivery/
├── backend/
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── utils/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
└── README.md
```