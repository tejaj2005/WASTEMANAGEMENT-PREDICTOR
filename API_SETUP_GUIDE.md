# 🔑 API Setup Guide for Intelligent Waste Segregation System

## 1. Google Gemini API (Required for AI Recommendations)
This API is used to generate intelligent recycling advice, hazard warnings, and disposal instructions based on the detected waste items.

### **Step 1: Go to Google AI Studio**
1.  Open your browser and visit: **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
2.  Sign in with your Google Account.

### **Step 2: Create an API Key**
1.  Click on the blue **"Create API key"** button (usually on the top left or center).
2.  You may be asked to select a Google Cloud project.
    *   **Option A**: Select an existing project if you have one.
    *   **Option B**: Click **"Create API key in new project"** (Recommended for beginners).
3.  Wait a moment for the key to generate.

### **Step 3: Copy Your Key**
1.  A popup will appear with your new API key. It starts with `AIza...`.
2.  Click the **Copy** icon next to the key.
3.  **Important**: Do not share this key publicly.

### **Step 4: Enter Key in the Application**
1.  Go back to your running Streamlit application tab.
2.  Look at the **Sidebar** (left menu).
3.  Find the **"🔑 API Configuration"** section.
4.  Paste your copied key into the text box labeled **"Gemini API Key"**.
5.  Press Enter. You should see a green success message: "✅ API Key configured!".

---

## Troubleshooting
*   **"Quota Exceeded"**: The free tier of Gemini has daily limits. If you hit this, wait for the next day or create a new key in a different Google account.
*   **"API Key Invalid"**: Ensure you copied the entire string without spaces.
*   **Region Not Supported**: If Google AI Studio is not available in your country, you might need to use a VPN or check Google's supported regions list.
