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

# แสดงโลโก้บริษัทขนาดเล็กไว้บนสุด (ถ้ามีไฟล์ company_logo.png)
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

if df is not None:
    # ส่วนฟิลเตอร์สำหรับเลือกพื้นที่
    with st.container():
        provinces = sorted(df['จังหวัด'].unique())
        selected_province = st.selectbox("📌 1. เลือกจังหวัดของคุณ", provinces)
        
        df_filtered_prov = df[df['จังหวัด'] == selected_province]
        
        amphoes = sorted(df_filtered_prov['อำเภอ / เขต'].unique())
        selected_amphoe = st.selectbox("🔍 2. เลือกอำเภอ / เขต ของคุณ", ["-- แสดงทุกอำเภอในจังหวัดนี้ --"] + amphoes)

    st.markdown("---")
    
    # 1. กรณีกดเลือก "แสดงทุกอำเภอในจังหวัดนี้"
    if selected_amphoe == "-- แสดงทุกอำเภอในจังหวัดนี้ --":
        st.subheader(f"📋 รายชื่อทั้งหมดใน จังหวัด {selected_province}")
        st.caption("💡 แนะนำให้เลือกโรงพยาบาลใกล้ตัวกรอกสิทธิให้ครบ 3 อันดับ")
        
        df_all_province = df_filtered_prov.copy()
        if not df_all_province.empty:
            for idx, row in df_all_province.iterrows():
                st.markdown(f"""
                <div class="hospital-card">
                    <div class="hospital-name">🏥 {row['รายชื่อโรงพยาบาล']}</div>
                    <div class="hospital-sub">📍 ต. {row['ตำบล / แขวง']} | อ. {row['อำเภอ / เขต']} | จ. {row['จังหวัด']}</div>
                </div>
                """, unsafe_allow_html=True)
            st.success(f"🎉 พบโรงพยาบาลทั้งหมด {len(df_all_province)} แห่ง")
        else:
            st.warning(f"ไม่พบข้อมูลโรงพยาบาลในจังหวัด {selected_province}")
            
    else:
        # หากเจาะจงอำเภอ
        df_filtered_amphoe = df_filtered_prov[df_filtered_prov['อำเภอ / เขต'] == selected_amphoe]
        
        # 3. กล่องเลือกตำบล/แขวง
        tambons = sorted(df_filtered_amphoe['ตำบล / แขวง'].unique())
        selected_tambon = st.selectbox("🏠 3. เลือกตำบล / แขวง ปัจจุบันของคุณ", ["-- แสดงทุกตำบลในอำเภอนี้ --"] + tambons)
        
        st.markdown("---")
        
        # กรณีเจาะจงตำบล
        if selected_tambon != "-- แสดงทุกตำบลในอำเภอนี้ --":
            st.subheader(f"📍 โรงพยาบาลใน ตำบล/แขวง {selected_tambon}")
            df_main = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] == selected_tambon].copy()
            
            if not df_main.empty:
                for idx, row in df_main.iterrows():
                    st.markdown(f"""
                    <div class="hospital-card" style="border-left-color: #28a745;">
                        <div class="hospital-name">🏥 {row['รายชื่อโรงพยาบาล']}</div>
                        <div class="hospital-sub">📍 ตำบล/แขวง: {row['ตำบล / แขวง']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ ไม่พบโรงพยาบาลในตำบล {selected_tambon} โดยตรง (โปรดเลือกพื้นที่ใกล้เคียงด้านล่าง)")
                
            # --- จุดที่ปรับปรุง: ดึงโรงพยาบาลแนะนำในอำเภอเดียวกัน มาแสดงผลจำกัดแค่ 3 ที่พอดีๆ ---
            st.subheader("🔄 โรงพยาบาลแนะนำเพิ่มเติมในพื้นที่ใกล้เคียง")
            st.caption("💡 แนะนำเพิ่มเติมในอำเภอเดียวกันสูงสุด 3 แห่ง สำหรับเลือกเป็นอันดับสำรอง")
            
            df_sub = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] != selected_tambon].copy()
            if not df_sub.empty:
                # ดึงมาแค่ 3 รายการแรก (.head(3)) เพื่อไม่ให้ล้นหน้าจอมือถือ
                df_sub_limit = df_sub.head(3)
                for idx, row in df_sub_limit.iterrows():
                    st.markdown(f"""
                    <div class="hospital-card">
                        <div class="hospital-name">🏥 {row['รายชื่อโรงพยาบาล']}</div>
                        <div class="hospital-sub">📍 ตำบล/แขวง: {row['ตำบล / แขวง']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.text
