import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบตรวจสอบโรงพยาบาลในพื้นที่",
    page_icon="🏥",
    layout="centered"
)

# ส่วนหัวของหน้าเว็บ
st.title("🏥 ระบบตรวจสอบโรงพยาบาลในพื้นที่")
st.markdown("---")

# ฟังก์ชันโหลดข้อมูลและซ่อนแคชเพื่อความเร็ว
@st.cache_data
def load_data():
    file_name = "รายชื่อโรงพยาบาลและที่ตั้ง_แยกจังหวัด.xlsx"
    try:
        df_bkk = pd.read_excel(file_name, sheet_name="รพ. กรุงเทพมหานคร")
        df_prov = pd.read_excel(file_name, sheet_name="รพ. ต่างจังหวัดและปริมณฑล")
        # รวมข้อมูลทั้งสองแท็บเข้าด้วยกัน
        df_all = pd.concat([df_bkk, df_prov], ignore_index=True)
        return df_all
    except Exception as e:
        st.error(f"ไม่พบไฟล์ข้อมูล '{file_name}' กรุณาตรวจสอบว่าวางไฟล์คู่กับตัวแอปแล้วหรือยัง")
        return None

df = load_data()

if df is not None:
    st.info("💡 คำแนะนำ: เลือก จังหวัด และ อำเภอ/เขต ด้านล่างเพื่อดูรายชื่อโรงพยาบาลในพื้นที่")
    
    # 1. กล่องเลือกจังหวัด
    provinces = sorted(df['จังหวัด'].unique())
    selected_province = st.selectbox("📌 ขั้นตอนที่ 1: เลือกจังหวัด", provinces)
    
    # กรองข้อมูลตามจังหวัดที่เลือก
    df_filtered_prov = df[df['จังหวัด'] == selected_province]
    
    # 2. กล่องเลือกอำเภอ/เขต (จะเปลี่ยนไปตามจังหวัดที่เลือกอัตโนมัติ)
    amphoes = sorted(df_filtered_prov['อำเภอ / เขต'].unique())
    selected_amphoe = st.selectbox("🔍 ขั้นตอนที่ 2: เลือกอำเภอ / เขต", ["-- แสดงทั้งหมด --"] + amphoes)
    
    st.markdown("### 📋 รายชื่อโรงพยาบาลที่พบ")
    
    # กรองข้อมูลขั้นตอนสุดท้าย
    if selected_amphoe == "-- แสดงทั้งหมด --":
        final_df = df_filtered_prov
    else:
        final_df = df_filtered_prov[df_filtered_prov['อำเภอ / เขต'] == selected_amphoe]
        
    # ปรับลำดับตัวเลขใหม่ให้เริ่มจาก 1
    final_df = final_df.copy()
    final_df['ลำดับ'] = range(1, len(final_df) + 1)
    
    # แสดงผลลัพธ์
    if not final_df.empty:
        # ปรับการแสดงผลตารางให้สวยงาม
        st.dataframe(
            final_df[['ลำดับ', 'รายชื่อโรงพยาบาล', 'ตำบล / แขวง', 'อำเภอ / เขต', 'จังหวัด']],
            hide_index=True,
            use_container_width=True
        )
        st.success(f"🎉 พบโรงพยาบาลทั้งหมด {len(final_df)} แห่ง")
    else:
        st.warning("❌ ไม่พบข้อมูลโรงพยาบาลในพื้นที่นี้")
        
    st.markdown("---")
    st.caption("ระบบบริการข้อมูลภายในบริษัท พัฒนาโดยใช้ Streamlit (ฟรีไม่มีค่าใช้จ่าย)")
