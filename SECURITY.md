# Security Configuration

## Password Protection
Your application is now protected with password authentication.

## Security Features Added

### 1. Authentication System
- Password-protected access to the application
- Session-based authentication
- Secure password hashing using SHA-256
- Logout functionality

### 2. File Upload Security
- File size limit: 50MB per file
- Allowed file types only: PNG, JPG, JPEG, BMP, TIFF, GIF
- Filename sanitization to prevent path traversal
- File validation before processing

### 3. Additional Security Measures
- Temporary file cleanup
- Secure session management
- Error handling without information disclosure

## Deployment Recommendations

### For Production Deployment:

1. **Use HTTPS**: Always deploy behind HTTPS/SSL
2. **Firewall**: Restrict access to trusted networks only
3. **Monitoring**: Set up logging and monitoring
4. **Updates**: Keep dependencies updated regularly

### Running the Application:
```bash
streamlit run streamlit_app.py
```

The application will now require the password "Brisbane2025" before allowing access.

## Security Notes
- The password is hardcoded for simplicity as requested
- Consider environment variables for production deployments
- Monitor for failed login attempts
- Regularly update Python dependencies