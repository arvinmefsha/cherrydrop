# Deployment Guide

## Prerequisites

1. **Python 3.7+** installed on your system
2. **MongoDB Atlas** account (free tier available)
3. **Web browser** for frontend
4. **Git** (optional, for version control)

## Quick Setup

Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

## Manual Setup

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` file with your settings:
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/owlhacks_delivery
   SECRET_KEY=your-super-secret-jwt-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DEBUG=True
   ```

### 2. MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster (M0 free tier)
4. Create a database user
5. Whitelist your IP address (or use 0.0.0.0/0 for development)
6. Get your connection string and update the `MONGODB_URL` in `.env`

### 3. Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Open the frontend:
   - **Option 1**: Open `frontend/index.html` directly in your browser
   - **Option 2**: Serve with Python:
     ```bash
     cd frontend
     python3 -m http.server 3000
     ```
     Then visit http://localhost:3000

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Features Implemented

### Authentication
- ✅ User registration with temple.edu email validation
- ✅ JWT-based authentication
- ✅ Secure password hashing

### User Management
- ✅ Point system (users start with 100 points)
- ✅ User profiles with username and points display

### Establishments
- ✅ Hardcoded Temple University area restaurants
- ✅ Search functionality
- ✅ Distance-based sorting (with geolocation)

### Order Management
- ✅ Place delivery requests
- ✅ Accept orders for delivery
- ✅ Order status tracking
- ✅ Photo confirmation for completed deliveries
- ✅ Point transfer system

### Frontend
- ✅ Responsive design with Tailwind CSS
- ✅ Two-tab interface (Request Delivery / Deliver)
- ✅ Real-time order tracking
- ✅ Image upload for delivery confirmation

## Configuration Options

### Points System
- New users start with 100 points
- Delivery cost calculated as: 10 base points + 5% of order subtotal
- Points are transferred only when customer confirms receipt

### Establishments
The system includes pre-configured establishments near Temple University:
- Subway
- Chipotle
- Wawa
- McDonald's
- Starbucks
- Dunkin'
- Halal Guys
- Popeyes

### Security Features
- Temple.edu email requirement
- JWT token authentication
- Password hashing with bcrypt
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Verify your connection string in `.env`
   - Check if your IP is whitelisted in MongoDB Atlas
   - Ensure database user has proper permissions

2. **CORS Issues**
   - The backend is configured to allow all origins for development
   - For production, update the CORS settings in `main.py`

3. **Token Expiration**
   - Tokens expire after 30 minutes by default
   - Users will need to log in again
   - Adjust `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env` if needed

4. **Image Upload Issues**
   - Images are stored as base64 in MongoDB
   - Large images may cause performance issues
   - Consider implementing proper file storage for production

### Development Tips

1. **Hot Reload**: The FastAPI server runs with `--reload` flag for automatic restarts
2. **Debug Mode**: Set `DEBUG=True` in `.env` for detailed error messages
3. **Database Browser**: Use MongoDB Compass to browse your database collections
4. **API Testing**: Use the built-in Swagger UI at `/docs` for testing endpoints

## Production Considerations

For production deployment, consider:

1. **Security**:
   - Use strong, unique secret keys
   - Implement rate limiting
   - Add input validation
   - Use HTTPS
   - Restrict CORS origins

2. **Performance**:
   - Implement proper file storage (AWS S3, etc.)
   - Add database indexing
   - Use connection pooling
   - Implement caching

3. **Monitoring**:
   - Add logging
   - Implement health checks
   - Monitor database performance
   - Set up error tracking

4. **Scalability**:
   - Use production WSGI server (Gunicorn)
   - Implement load balancing
   - Consider database sharding
   - Use CDN for static files