# Calories Prediction API Deployment Guide

## Directory Structure
```
calories-api/
├── app.py
├── wsgi.py
├── requirements.txt
├── README.md
└── model/
    └── Calories_Prediction_model.pkl
```

## PythonAnywhere Deployment Steps

1. Sign up for a PythonAnywhere account at https://www.pythonanywhere.com/

2. Upload your files:
   - Go to the Files tab
   - Create a new directory (e.g., `calories-api`)
   - Create a subdirectory called `model`
   - Upload these files:
     - `app.py` → calories-api/
     - `wsgi.py` → calories-api/
     - `requirements.txt` → calories-api/
     - `Calories_Prediction_model.pkl` → calories-api/model/

3. Set up a virtual environment:
   ```bash
   # In PythonAnywhere bash console
   cd calories-api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Configure the web app:
   - Go to the Web tab
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Select Python version (3.8 or higher)
   - Set the following configurations:
     - Source code: /home/YOUR_USERNAME/calories-api
     - Working directory: /home/YOUR_USERNAME/calories-api
     - WSGI configuration file: /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py

5. Update the WSGI configuration:
   - In the Web tab, click on the WSGI configuration file link
   - Replace the content with:
     ```python
     import sys
     import os
     
     # Add your project directory to the sys.path
     path = '/home/YOUR_USERNAME/calories-api'
     if path not in sys.path:
         sys.path.append(path)
     
     from wsgi import application
     ```

6. Configure static files (if needed):
   - In the Web tab, add any static file mappings
   - URL: /static/
   - Directory: /home/YOUR_USERNAME/calories-api/static

7. Enable CORS:
   - The app already has CORS enabled for all origins
   - If you need to restrict it, modify the CORS settings in app.py

8. Check file permissions:
   ```bash
   # In PythonAnywhere bash console
   cd calories-api
   chmod 755 .
   chmod 755 model
   chmod 644 model/Calories_Prediction_model.pkl
   ```

9. Reload the web app:
   - Click the "Reload" button in the Web tab

## Testing the Deployed API

Test your API using curl:
```bash
curl -X POST https://YOUR_USERNAME.pythonanywhere.com/predict \
     -H "Content-Type: application/json" \
     -d '{
         "Age": 25,
         "Height": 170,
         "Weight": 65,
         "Duration": 30,
         "Heart_Rate": 80,
         "Body_Temp": 37,
         "Gender": 1
     }'
```

## Frontend Configuration

Update your frontend Vite configuration to point to the production API:

```typescript
// vite.config.ts
export default defineConfig({
  // ... other config
  server: {
    proxy: {
      '/api': {
        target: 'https://YOUR_USERNAME.pythonanywhere.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
```

## Troubleshooting

1. If you see "Internal Server Error":
   - Check the error logs in the Web tab
   - Verify all required files are uploaded
   - Check the virtual environment has all dependencies
   - Verify the model file is in the correct location (model/Calories_Prediction_model.pkl)

2. If you see CORS errors:
   - Verify the frontend URL is making requests to the correct endpoint
   - Check the Network tab in browser dev tools for the actual request URL

3. If the model fails to load:
   - Check the file permissions of the model file and directories
   - Verify the model file was uploaded to the correct location
   - Check the error logs for specific error messages

4. Common issues:
   - Model file not found: Make sure it's in the `model` directory
   - Permission denied: Run the chmod commands in step 8
   - Import errors: Make sure all requirements are installed in the virtual environment 