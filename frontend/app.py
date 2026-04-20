import streamlit as st
import requests
import os
from PIL import Image

# Debug: show what URL is being used
try:
    API_BASE = st.secrets["API_BASE_URL"]
except:
    API_BASE = os.getenv("API_BASE_URL", "https://prescription-reader-x714.onrender.com")

st.set_page_config(
    page_title="Prescription Reader",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_medicine_card(med, index):
    name     = med.get("medicine") or "Unknown"
    form     = med.get("form") or ""
    dosage   = med.get("dosage") or "—"
    freq     = med.get("frequency") or "—"
    duration = med.get("duration") or "—"
    notes    = med.get("notes") or ""
    if isinstance(notes, str) and notes.strip().startswith("<"):
        notes = ""

    with st.container(border=True):
        if form:
            st.markdown(f"### {name} &nbsp; `{form}`")
        else:
            st.markdown(f"### {name}")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="Dosage", value=dosage)
        with c2:
            st.metric(label="Frequency", value=freq)
        with c3:
            st.metric(label="Duration", value=duration)

        if notes:
            st.caption(f"📝 {notes}")


# ── Header ──────────────────────────────────────────────────────────────────
st.title("💊 Prescription Reader")
st.caption("Upload a doctor's prescription — get a clean, structured medicine list instantly.")

# DEBUG — remove after fixing
st.info(f"🔗 Connected to: `{API_BASE}`")

st.divider()

# ── Layout ──────────────────────────────────────────────────────────────────
col_upload, col_result = st.columns([1, 1.4], gap="large")

with col_upload:
    st.subheader("📎 Upload Prescription")
    uploaded_file = st.file_uploader(
        "Choose file", type=["jpg", "jpeg", "png", "pdf"],
        label_visibility="collapsed"
    )
    st.caption("Supports JPG, PNG, PDF · Max 10MB")

    if uploaded_file:
        if uploaded_file.type != "application/pdf":
            st.image(Image.open(uploaded_file), caption="Uploaded Prescription", use_column_width=True)
        else:
            st.success(f"📄 PDF uploaded: **{uploaded_file.name}**")

    st.markdown("")
    extract_btn = st.button("🔍 Extract Medicines", use_container_width=True, disabled=not uploaded_file)

# ── Results ─────────────────────────────────────────────────────────────────
with col_result:
    st.subheader("🧾 Extracted Information")

    if extract_btn and uploaded_file:
        with st.spinner("Running OCR and AI analysis..."):
            try:
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(
                    f"{API_BASE}/api/extract-medicines",
                    files=files,
                    timeout=120
                )

                st.write(f"Status code: {response.status_code}")
                st.write(f"Raw response: {response.text[:500]}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                    except Exception:
                        st.error("Server returned empty/invalid response.")
                        st.stop()

                    medicines = data.get("medicines", [])
                    raw_text  = data.get("raw_ocr_text", "")

                    if medicines:
                        st.success(f"✅ Found **{len(medicines)}** medicine(s)")
                        for i, med in enumerate(medicines):
                            render_medicine_card(med, i)

                        with st.expander("🔠 View raw OCR text"):
                            st.code(raw_text, language=None)

                        st.warning("⚠️ **Medical Disclaimer:** This output is AI-generated and may contain errors. Always verify with your doctor or pharmacist before taking any medication.")
                    else:
                        st.warning("No medicines could be extracted. Please try a clearer image.")

                else:
                    try:
                        detail = response.json().get("detail", "Unknown error")
                    except Exception:
                        detail = response.text or "Empty response"
                    st.error(f"API Error {response.status_code}: {detail}")

            except requests.exceptions.ConnectionError as e:
                st.error(f"❌ Connection error: {str(e)}")
            except requests.exceptions.Timeout:
                st.error("⏳ Timed out. Try again.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

    elif not uploaded_file:
        st.info("⬅️ Upload a prescription image to get started.")

st.divider()
st.caption("Built with FastAPI · Tesseract · Groq Llama 3.3 · Streamlit")