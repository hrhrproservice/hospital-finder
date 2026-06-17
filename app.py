import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บให้เหมาะสมกับมือถือ
st.set_page_config(
    page_title="ระบบตรวจสอบโรงพยาบาลสำหรับสิทธิประกันสังคม",
    page_icon="🏥",
    layout="centered"
)

# สไตล์ตกแต่งเพิ่มเติมให้แสดงผลบนมือถือสวยงาม (CSS Custom Styling)
st.markdown("""
    <style>
    html, body, [data-testid="stMarkdownContainer"] {
        font-size: 15px;
    }
    .hospital-card {
        background-color: #f8f9fa;
        border-left: 5px solid #007bff;
        padding: 12px 15px;
        margin-bottom: 10px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .hospital-name {
        font-weight: bold;
        color: #1c3d5a;
        font-size: 16px;
    }
    .hospital-sub {
        color: #6c757d;
        font-size: 13px;
        margin-top: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ส่วนที่แก้ไข: ดึงโลโก้บริษัทเป็นไฟล์ .jpg ไว้บนสุด ---
try:
    st.image("company_logo.jpg", width=120)
except Exception:
    pass

# ส่วนหัวของหน้าเว็บ
st.title("🏥 ระบบตรวจสอบโรงพยาบาล")
st.markdown("##### ค้นหารายชื่อโรงพยาบาลเพื่อกรอกสิทธิประกันสังคม 3 อันดับ")
st.markdown("---")

# ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data():
    file_name = "รายชื่อโรงพยาบาลและที่ตั้ง_แยกจังหวัด.xlsx"
    try:
        df_bkk = pd.read_excel(file_name, sheet_name="รพ. กรุงเทพมหานคร")
        df_prov = pd.read_excel(file_name, sheet_name="รพ. ต่างจังหวัดและปริมณฑล")
        df_all = pd.concat([df_bkk, df_prov], ignore_index=True)
        return df_all
    except Exception as e:
        st.error(f"ไม่พบไฟล์ข้อมูล '{file_name}' กรุณาตรวจสอบชื่อไฟล์บน GitHub")
        return None

df = load_data()

# ดิกชันนารีจับคู่พื้นที่ใกล้เคียง (สำหรับแนะนำข้ามอำเภอ/เขต)
NEARBY_DISTRICTS = {
    # โซนกรุงเทพฯ ใต้ / ฝั่งธน
    "บางขุนเทียน": ["บางบอน", "จอมทอง", "ราษฎร์บูรณะ", "ทุ่งครุ"],
    "บางบอน": ["บางขุนเทียน", "จอมทอง", "หนองแขม", "บางแค"],
    "จอมทอง": ["บางขุนเทียน", "บางบอน", "ราษฎร์บูรณะ", "ภาษีเจริญ"],
    "ราษฎร์บูรณะ": ["ทุ่งครุ", "จอมทอง", "บางขุนเทียน", "พระประแดง"],
    "บางแค": ["ภาษีเจริญ", "หนองแขม", "บางบอน", "ตลิ่งชัน"],
    "หนองแขม":
