# GFD Print Quantum AI Marketplace V11

A futuristic mobile-first Flask + PWA app for a South African printing marketplace.

## Included modules
- Animated Quantum Cyber 2050 landing page
- AI printer discovery and ranking
- Province/service filters
- Printer cards with Call, WhatsApp, Directions and Website buttons
- Quote calculator with artwork upload
- Admin dashboard for incoming quote requests
- Printer onboarding form
- PWA install support
- Android Studio WebView wrapper for APK builds
- Demo Jetline/PostNet/Minuteman/independent printer network data

## Run on Windows / VS Code
```bash
cd "GFD Print Quantum AI Marketplace V11"
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5000

## Build APK
1. Open `android-webview` in Android Studio.
2. Run the Flask app locally.
3. In Android emulator, the WebView points to `http://10.0.2.2:5000`.
4. For a real phone APK, host the Flask/PWA online and replace the URL in `MainActivity.java` with your live domain.
5. Build > Generate Signed Bundle / APK.

## Important data note
The Jetline entries included are starter/demo records. To list every live Jetline branch with exact phone numbers and current operating info, connect the app to Google Places API or import a verified CSV from Jetline/official branch data.
