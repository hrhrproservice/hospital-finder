import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบตรวจสอบโรงพยาบาลสำหรับสิทธิประกันสังคม",
    page_icon="🏥",
    layout="centered"
)

# ส่วนหัวของหน้าเว็บ
st.title("🏥 ระบบตรวจสอบโรงพยาบาลในพื้นที่ (ประกันสังคม)")
st.markdown("##### สำหรับให้พนักงานตรวจสอบและเลือกโรงพยาบาลกรอกสิทธิประกันสังคม (กรอก 3 อันดับ)")
st.markdown("---")

# ฟังก์ชันโหลดข้อมูลและซ่อนแคชเพื่อความเร็ว
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
    st.info("💡 วิธีใช้: เลือก จังหวัด และ อำเภอ/เขต เพื่อดูโรงพยาบาลในพื้นที่ของท่าน และพื้นที่ใกล้เคียงสำหรับกรอกอันดับสำรอง")
    
    # 1. กล่องเลือกจังหวัด
    provinces = sorted(df['จังหวัด'].unique())
    selected_province = st.selectbox("📌 ขั้นตอนที่ 1: เลือกจังหวัดของคุณ", provinces)
    
    df_filtered_prov = df[df['จังหวัด'] == selected_province]
    
    # 2. กล่องเลือกอำเภอ/เขต
    amphoes = sorted(df_filtered_prov['อำเภอ / เขต'].unique())
    selected_amphoe = st.selectbox("🔍 ขั้นตอนที่ 2: เลือกอำเภอ / เขต ของคุณ", amphoes)
    
    df_filtered_amphoe = df_filtered_prov[df_filtered_prov['อำเภอ / เขต'] == selected_amphoe]
    
    # 3. กล่องเลือกตำบล/แขวง (เพื่อให้เจาะจงที่อยู่ตัวเองก่อน)
    tambons = sorted(df_filtered_amphoe['ตำบล / แขวง'].unique())
    selected_tambon = st.selectbox("🏠 ขั้นตอนที่ 3: เลือกตำบล / แขวง ที่คุณอยู่ปัจจุบัน", ["-- แสดงทุกตำบลในอำเภอนี้ --"] + tambons)
    
    st.markdown("---")
    
    # --- ส่วนที่ 1: โรงพยาบาลในตำบลที่เลือก (อันดับหลัก) ---
    if selected_tambon != "-- แสดงทุกตำบลในอำเภอนี้ --":
        st.subheader(f"📍 1. โรงพยาบาลใน ตำบล/แขวง {selected_tambon}")
        df_main = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] == selected_tambon].copy()
        
        if not df_main.empty:
            df_main['ลำดับ'] = range(1, len(df_main) + 1)
            st.dataframe(df_main[['ลำดับ', 'รายชื่อโรงพยาบาล', 'ตำบล / แขวง', 'อำเภอ / เขต']], hide_index=True, use_container_width=True)
        else:
            st.warning(f"ไม่พบโรงพยาบาลในตำบล {selected_tambon} โดยตรง (กรุณาเลือกจากตำบลใกล้เคียงด้านล่าง)")
            
        # --- ส่วนที่ 2: โรงพยาบาลแนะนำเพิ่มเติมในตำบลใกล้เคียง (สำหรับอันดับ 2-3) ---
        st.subheader("🔄 2. โรงพยาบาลแนะนำในตำบลใกล้เคียง (ในอำเภอ/เขตเดียวกัน)")
        st.caption("💡 พนักงานสามารถใช้รายชื่อด้านล่างนี้กรอกเป็น โรงพยาบาลอันดับ 2 และอันดับ 3 เผื่อที่แรกเต็มได้เลยครับ")
        
        df_sub = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] != selected_tambon].copy()
        if not df_sub.empty:
            df_sub['ลำดับ'] = range(1, len(df_sub) + 1)
            st.dataframe(df_sub[['ลำดับ', 'รายชื่อโรงพยาบาล', 'ตำบล / แขวง', 'อำเภอ / เขต']], hide_index=True, use_container_width=True)
        else:
            st.text("ไม่มีตำบลอื่นที่มีโรงพยาบาลเพิ่มเติมในอำเภอนี้")
            
    else:
        # ถ้าเลือกแสดงทั้งหมดในอำเภอ
        st.subheader(f"📋 รายชื่อโรงพยาบาลทั้งหมดใน อำเภอ/เขต {selected_amphoe}")
        st.caption("💡 รวมทุกตำบลในพื้นที่ใกล้เคียง พนักงานเลือกกรอกให้ครบ 3 อันดับจากตารางนี้ได้เลย")
        df_all_amphoe = df_filtered_amphoe.copy()
        if not df_all_amphoe.empty:
            df_all_amphoe['ลำดับ'] = range(1, len(df_all_amphoe) + 1)
            st.dataframe(df_all_amphoe[['ลำดับ', 'รายชื่อโรงพยาบาล', 'ตำบล / แขวง', 'อำเภอ / เขต']], hide_index=True, use_container_width=True)
            st.success(f"🎉 พบโรงพยาบาลในพื้นที่ใกล้เคียงทั้งหมด {len(df_all_amphoe)} แห่ง")
        else:
            st.warning("ไม่พบข้อมูลโรงพยาบาลในอำเภอนี้")

    st.markdown("---")
    st.caption("ระบบบริการข้อมูลภายในบริษัท พัฒนาโดยใช้ Streamlit (ฟรีไม่มีค่าใช้จ่าย)")
