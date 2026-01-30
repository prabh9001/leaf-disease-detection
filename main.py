import streamlit as st
import requests
import os
from utils import convert_image_to_base64_and_test, create_pdf_report
import datetime

# Set Streamlit theme to wide mode
st.set_page_config(
    page_title="Leaf Disease Detection",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Global Styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
    
    :root {
        --primary: #166534;
        --secondary: #4ade80;
        --accent: #f59e0b;
        --bg-light: #f7f9f7;
        --card-bg: #ffffff;
    }

    .stApp {
        background-color: var(--bg-light);
        font-family: 'Outfit', sans-serif;
    }

    /* Weather Risk Card */
    .weather-card {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Care Calendar Card */
    .calendar-card {
        background: #fdfdfd;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
    }
    
    .calendar-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px dashed #eee;
    }

    /* Dark Mode Support */
    [data-theme="dark"] .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    [data-theme="dark"] .result-card {
        background: #1e293b;
        border-color: #334155;
    }
    [data-theme="dark"] .list-item {
        background: #334155;
        color: #f1f5f9;
        border-left-color: #475569;
    }

    /* Remove excess vertical space at the top */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 5rem !important;
        padding-right: 5rem !important;
        max-width: 95% !important;
    }

    /* Target specific Streamlit elements to reduce gaps */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Elegant Title */
    h1 {
        font-family: 'Playfair Display', serif;
        font-weight: 700 !important;
        color: #2d5a27;
        font-size: 3.5rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
        text-align:center;
    }
    
    p {
        color: #57606f;
        font-size: 1.15rem;
        line-height: 1.6;
        text-align:center;
    }
    
    /* Botanical Card */
    .result-card {
        background: #ffffff;
        border-radius: 20px;
        border: 1px solid #eef2f3;
        box-shadow: 0 10px 40px rgba(45, 90, 39, 0.08);
        padding: 1.5rem;
        margin-top: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    /* Decorative top bar for cards */
    .result-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #4ade80, #166534);
    }
    
    .disease-title {
        font-family: 'Playfair Display', serif;
        color: #1e3a1b;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        line-height: 1.2;
    }
    
    .section-title {
        color: #166534;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-top: 2.5rem;
        margin-bottom: 1.2rem;
        border-bottom: 2px solid #dcfce7;
        padding-bottom: 0.5rem;
        display: inline-block;
    }
    
    /* Badges */

    .info-badge {
        display: inline-flex;
        align-items: center;
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 0.4rem 1rem;
        font-size: 0.9rem;
        font-weight: 500;
        margin-right: 0.6rem;
        margin-bottom: 0.6rem;
        transition: all 0.2s;
    }
    .info-badge:hover {
        background: #dcfce7;
        transform: translateY(-1px);
    }
    
    .severity-badge {
        background: #fef2f2;
        color: #991b1b;
        border-color: #fecaca;
    }
    
    .confidence-badge {
        background: #eff6ff;
        color: #1e40af;
        border-color: #bfdbfe;
    }

    /* List Items */
    .symptom-list, .cause-list, .treatment-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .list-item {
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.6rem;
        border-left: 3px solid #cbd5e1;
        font-size: 1.05rem;
        color: #334155;
    }
    .list-item:hover {
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left-color: #166534;
    }
    
    /* Primary Button */
    .stButton > button {
        background-color: #166534 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(22, 101, 52, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    /* Ensure button text remains white even with Streamlit overrides */
    .stButton > button p, .stButton > button span, .stButton > button div {
        color: white !important;
    }
    .stButton > button:hover {
        background-color: #14532d !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(22, 101, 52, 0.3) !important;
    }
    
    /* Image Lightbox Style */
    .img-container {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        cursor: pointer;
    }
    
    /* Full-screen View on click (using target hack) */
    .lightbox {
        display: none;
        position: fixed;
        z-index: 9999;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.9);
        text-align: center;
        padding: 40px;
    }
    .lightbox:target {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }
    .lightbox img {
        max-width: 90%;
        max-height: 85%;
        border-radius: 8px;
        box-shadow: 0 0 30px rgba(0,0,0,0.5);
    }
    .close-lightbox {
        position: absolute;
        top: 30px;
        right: 40px;
        color: white;
        font-size: 40px;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration (Feature 4 & 7) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3241/3241470.png", width=100)
    st.title("Settings")
    
    # Feature 7: Theme & Premium UI
    ui_mode = st.selectbox("🎨 UI Theme", ["Standard Botanical", "Premium Dark"], index=0)
    if ui_mode == "Premium Dark":
         st.markdown("<style>.stApp { background-color: #0f172a !important; color: #f8fafc !important; } .result-card { background: #1e293b !important; color: #f8fafc !important; }</style>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Feature 4: Real-Time Weather Risk Assessment (Using Open-Meteo - 100% Free)
    st.subheader("🌦️ Environmental Risk")
    location = st.text_input("Enter Location (City Name)", "Delhi")
    
    # Real-time weather integration helper (Using Open-Meteo Open Data)
    def get_botanical_risk(city):
        try:
            # 1. Geocoding: Get Lat/Lon for the city name
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            geo_resp = requests.get(geo_url, timeout=5).json()
            
            if not geo_resp.get('results'):
                return None, f"❌ City not found: {city}"
            
            lat = geo_resp['results'][0]['latitude']
            lon = geo_resp['results'][0]['longitude']
            full_name = geo_resp['results'][0]['name']
            
            # 2. Weather: Get Temperature and Humidity
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
            w_resp = requests.get(weather_url, timeout=5).json()
            
            current = w_resp.get('current', {})
            humidity = current.get('relative_humidity_2m', 0)
            temp = current.get('temperature_2m', 0)
            
            # Risk Calculation Logic
            risk_score = humidity 
            if temp > 30: risk_score += 10 # Heat stress
            if humidity > 80: risk_score = min(95, risk_score + 15) # Fungal spike
            
            risk_level = "Low"
            if risk_score > 40: risk_level = "Medium"
            if risk_score > 70: risk_level = "High"
            
            msg = "Conditions are stable."
            if humidity > 75: msg = "⚠️ High humidity detected. Fungal diseases (Rust, Mildew) move faster now."
            elif temp > 35: msg = "🔥 Heat stress alert. Watch for wilting and leaf burn."
            elif humidity < 30: msg = "🏜️ Very dry air. Check for spider mites and dehydration."
            
            return {
                "score": int(risk_score),
                "level": risk_level,
                "msg": msg,
                "temp": temp,
                "humidity": humidity,
                "city": full_name
            }, None
        except Exception as e:
            return None, f"Connection error: {e}"

    if location:
        with st.spinner("Fetching local climate data..."):
            risk_data, error = get_botanical_risk(location)
            
        if error:
            st.error(error)
        elif risk_data:
            st.session_state.weather_risk = risk_data
            st.markdown(f"""
            <div class='weather-card' style='background: linear-gradient(135deg, {"#991b1b" if risk_data["level"] == "High" else "#1e40af"}, #3b82f6);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 0.9rem; opacity: 0.8;'>Risk Level: <b>{risk_data["level"]}</b></span>
                    <span style='font-size: 0.9rem;'>{risk_data["temp"]}°C | {risk_data["humidity"]}% RH</span>
                </div>
                <div style='font-size: 2.2rem; font-weight: 700; margin: 10px 0;'>{risk_data["score"]}%</div>
                <div style='font-size: 0.85rem; line-height: 1.4;'>{risk_data["msg"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 Tip: Upload multiple leaves for a full plant health audit.")

# --- App Content ---
st.markdown("<div style='text-align: center;'><h1>🌿 Leaf Disease Detector</h1><p>Enterprise AI for Agriculture & Gardening</p></div>", unsafe_allow_html=True)

# Initialize state
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []

def safe_rerun():
    st.rerun()

# --- Feature 5: Batch Processing ---
st.markdown("<h2 style='text-align: center; color: #166534; margin-bottom: 2rem;'>📤 Upload Leaves</h2>", unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Upload one or more leaf images...", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True,
    key="batch_uploader"
)

if uploaded_files:
    if st.button("🚀 Analyze All Leaves"):
        results = []
        progress_bar = st.progress(0)
        for i, file in enumerate(uploaded_files):
            with st.spinner(f"Analyzing leaf {i+1}/{len(uploaded_files)}..."):
                img_bytes = file.getvalue()
                res = convert_image_to_base64_and_test(img_bytes)
                if res:
                    # Pre-generate PDF for instant download and store in results
                    pdf_data = None
                    try:
                        pdf_data = create_pdf_report(res, img_bytes, location=location)
                    except Exception as pdf_err:
                        # Log but don't stall the whole loop
                        pass
                        
                    results.append({
                        "name": file.name, 
                        "data": res, 
                        "bytes": img_bytes,
                        "pdf": pdf_data
                    })
                progress_bar.progress((i + 1) / len(uploaded_files))
        st.session_state.batch_results = results
        st.success(f"Successfully analyzed {len(results)} images!")

# --- Display Results ---
if st.session_state.batch_results:
    st.markdown("---")
    st.subheader(f"📊 Analysis Batch - {len(st.session_state.batch_results)} Items")
    
    for idx, item in enumerate(st.session_state.batch_results):
        with st.expander(f"🍃 Result: {item['name']} - {item['data'].get('plant_name', 'Plant')}", expanded=(idx==0)):
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                st.image(item['bytes'], use_column_width=True)
                
                # Feature 3: PDF Export
                if item.get('pdf'):
                    # Provide Download Option (Most reliable on Deployed apps)
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=item['pdf'],
                        file_name=f"Plant_Report_{idx}_{item['name']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{idx}"
                    )
                else:
                    st.warning("⚠️ PDF generation unavailable for this result.")
            
            with col_info:
                res = item['data']
                
                # Health Badge
                status_color = "#00b894" if not res.get('disease_detected') else "#d63031"
                st.markdown(f"""
                    <div style='background: {status_color}11; border: 1px solid {status_color}; padding: 10px; border-radius: 10px; margin-bottom: 15px;'>
                        <strong style='color: {status_color}'>Status: {'⚠️ Disease Detected' if res.get('disease_detected') else '✅ Healthy'}</strong>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write(f"**Plant:** {res.get('plant_name')} (*{res.get('scientific_name')}*)")
                if res.get('disease_detected'):
                    st.write(f"**Issue:** {res.get('disease_name')}")
                    st.write(f"**Severity:** {res.get('severity', 'Moderate').title()}")
                
                # Feature 6: Personalized Care Calendar
                calendar = res.get('care_calendar')
                if calendar:
                    st.markdown("<div class='section-title'>� Personalized Care Calendar</div>", unsafe_allow_html=True)
                    cal_html = "<div class='calendar-card'>"
                    for activity, notes in calendar.items():
                        if notes:
                            cal_html += f"<div class='calendar-item'><strong>{activity.title()}:</strong> <span>{notes}</span></div>"
                    cal_html += "</div>"
                    st.markdown(cal_html, unsafe_allow_html=True)

                # Diagnostics & Treatment (Tabs)
                tab1, tab2, tab3 = st.tabs(["🩺 Diagnostics", "💊 Treatment", "🌍 Env Insights"])
                with tab1:
                    for s in res.get('symptoms', []):
                        st.markdown(f"<div class='list-item'>{s}</div>", unsafe_allow_html=True)
                with tab2:
                    for t in res.get('treatment', []):
                        st.markdown(f"<div class='list-item'>{t}</div>", unsafe_allow_html=True)
                with tab3:
                    if 'weather_risk' in st.session_state:
                        w = st.session_state.weather_risk
                        st.markdown(f"""
                        <div class='list-item' style='border-left-color: #3b82f6;'>
                            <b>Local Context ({location}):</b><br>
                            Current Humidity: {w['humidity']}% | Temp: {w['temp']}°C<br><br>
                            <i>Advice:</i> {w['msg']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Enter a location in the sidebar to see how your local weather affects this plant.")

    if st.button("🗑️ Clear All Results"):
        st.session_state.batch_results = []
        st.rerun()
else:
    st.info("👋 Upload leaf images above and click 'Analyze All' to start your batch audit.")
