import streamlit as st
import requests
import os
from utils import convert_image_to_base64_and_test

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease Detection",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Modern Botanical CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
    
    .stApp {
        background-color: #f7f9f7;
        background-image: radial-gradient(#d8e2dc 1px, transparent 1px);
        background-size: 24px 24px;
        font-family: 'Outfit', sans-serif;
        color: #2f3542;
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
        color: #ffffff !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(22, 101, 52, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #14532d !important;
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


st.markdown("<div style='text-align: center;'><h1>🌿 Leaf Disease Detector</h1><p>Upload a leaf photo to diagnose diseases and get treatment advice.</p></div>", unsafe_allow_html=True)

# Initialize state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'current_image_type' not in st.session_state:
    st.session_state.current_image_type = None

# Note: We now process directly using LeafDiseaseDetector for Streamlit Cloud compatibility
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# Main Application Logic
if st.session_state.analysis_result:
    # --- Split Layout (Results Active) ---
    col_left, col_right = st.columns([1, 1.4])
    
    with col_left:
        st.markdown("<h3 style='color: #166534; margin-bottom: 1.5rem; text-align: left;'>📸 Analyzed Image</h3>", unsafe_allow_html=True)
        if st.session_state.current_image:
            st.image(st.session_state.current_image, use_column_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅️ New Analysis"):
            st.session_state.analysis_result = None
            st.session_state.current_image = None
            st.session_state.current_image_type = None
            safe_rerun()

    with col_right:
        result = st.session_state.analysis_result
        html_content = ""
        
        if result.get("disease_type") == "invalid_image":
            html_content = """
            <div class='result-card'>
                <div class='disease-title' style='color: #ff7675;'>⚠️ Invalid Image</div>
                <div style='color: #636e72; font-size: 1.1em;'>Please upload a clear image of a plant leaf.</div>
            </div>
            """
        else:
            # --- 1. Plant Profile Card ---
            plant_name = result.get('plant_name', 'Unknown Plant')
            sci_name = result.get('scientific_name', '')
            description = result.get('description', '')
            taxonomy = result.get('taxonomy', {})
            similar_imgs = result.get('similar_images', [])
            
            html_content += f"""
            <div class='result-card'>
                <div class='section-title' style='margin-top:0;'>🌱 Plant Identity</div>
                <div class='disease-title'>{plant_name}</div>
                <div style='font-style: italic; color: #555; margin-bottom: 1rem; font-size: 1.1rem;'>{sci_name}</div>
            """
            
            if taxonomy:
                html_content += "<div style='margin-bottom: 1.5rem;'>"
                for rank, name in taxonomy.items():
                    if name:
                        html_content += f"<span class='info-badge' style='background: #e0f2f1; color: #00695c;'>{rank.title()}: {name}</span>"
                html_content += "</div>"
            
            if description:
                html_content += f"<div style='line-height: 1.6; color: #444; margin-bottom: 1.5rem;'>{description[:500]}{'...' if len(description)>500 else ''}</div>"

            if similar_imgs:
                html_content += "<div class='section-title'>📸 Reference Images</div>"
                html_content += "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 1rem;'>"
                for i, img_url in enumerate(similar_imgs):
                    lb_id = f"lightbox-{i}"
                    html_content += f"""<div class='img-container'><a href='#{lb_id}'><img src='{img_url}' style='width: 100%; height: 200px; object-fit: cover; display: block; transition: transform 0.3s;' onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'"/></a><a href='{img_url}' download target='_blank' style='position: absolute; bottom: 8px; right: 8px; background: rgba(255,255,255,0.95); padding: 5px 10px; border-radius: 15px; text-decoration: none; color: #166534; font-weight: 600; font-size: 0.75rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 4px; transition: all 0.2s;'><span>⬇️ Save</span></a></div><div id='{lb_id}' class='lightbox'><a href='#' class='close-lightbox'>&times;</a><img src='{img_url}' /><div style='margin-top: 20px;'><a href='{img_url}' download target='_blank' style='background: #166534; color: white; padding: 12px 30px; border-radius: 30px; text-decoration: none; font-weight: 600;'>Download Full Resolution</a></div></div>"""
                html_content += "</div>"
            
            html_content += "</div>"

            # --- 2. Health Assessment Card ---
            if result.get("disease_detected"):
                html_content += "<div class='result-card'>"
                html_content += f"<div class='disease-title'>{result.get('disease_name', 'Unknown Issue')}</div>"
                
                sci_disease = result.get('disease_scientific_name')
                if sci_disease and sci_disease != result.get('disease_name'):
                        html_content += f"<div style='font-style: italic; color: #555; margin-bottom: 1rem; font-size: 1.1rem;'>{sci_disease}</div>"
                
                badges_html = ""
                dtype = result.get('disease_type')
                if dtype and dtype.lower() not in ['unknown', 'none', 'n/a']:
                    badges_html += f"<span class='info-badge'>{dtype.title()}</span>"
                
                severity = result.get('severity')
                if severity and severity.lower() not in ['unknown', 'none', 'n/a']:
                    badges_html += f"<span class='info-badge severity-badge'>Severity: {severity.title()}</span>"
                
                confidence = result.get('confidence')
                if confidence:
                    badges_html += f"<span class='info-badge confidence-badge'>{confidence}% Confidence</span>"
                
                html_content += f"<div>{badges_html}</div>"
                
                if result.get("symptoms"):
                    html_content += "<div class='section-title'>🩺 Diagnostics</div>"
                    for symptom in result.get("symptoms", []):
                        html_content += f"<div class='list-item'>{symptom}</div>"

                if result.get("treatment"):
                    html_content += "<div class='section-title'>💊 Recommended Treatment</div>"
                    for treat in result.get("treatment", []):
                        html_content += f"<div class='list-item'>{treat}</div>"
                
                html_content += f"<div class='timestamp' style='color: #b2bec3; font-size: 0.85rem; margin-top: 2.5rem; text-align: right; font-weight: 500;'>Analysis Time: {result.get('analysis_timestamp', 'Just now')}</div>"
                html_content += "</div>"
            else:
                html_content += f"""
                <div class='result-card'>
                    <div class='disease-title' style='color: #00b894;'>✅ Healthy Plant</div>
                    <div style='color: #636e72; font-size: 1.2em; margin-bottom: 1em;'>Great news! No diseases were detected. Your plant looks vibrant and healthy.</div>
                    <span class='info-badge confidence-badge'>{result.get('confidence', '99')}% Confidence</span>
                </div>
                """
        
        st.markdown(html_content, unsafe_allow_html=True)

else:
    # --- Centered Layout (Initial State) ---
    _, mid_col, _ = st.columns([1, 2, 1])
    
    with mid_col:
        st.markdown("<h2 style='text-align: center; color: #166534; margin-bottom: 2rem;'>📤 Upload Image</h2>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose a leaf image...", type=["jpg", "jpeg", "png"], key="uploader")
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Selected Image", use_column_width=True)
            if st.button("Analyze Plant Health"):
                with st.spinner("🔬 AI is analyzing..."):
                    try:
                        img_bytes = uploaded_file.getvalue()
                        # Direct call to logic instead of API request
                        result = convert_image_to_base64_and_test(img_bytes)
                        
                        if result:
                            st.session_state.analysis_result = result
                            st.session_state.current_image = img_bytes
                            st.session_state.current_image_type = uploaded_file.type
                            safe_rerun()
                        else:
                            st.error("AI Analysis failed. Please check your API key in Streamlit Secrets.")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("👋 Upload a leaf photo above to begin analysis.")
