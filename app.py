import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบตรวจสอบโรงพยาบาลประกันสังคม - HR PRO",
    page_icon="🏥",
    layout="centered"
)

# ส่วนหัวของหน้าเว็บ
st.title("🏥 ระบบตรวจสอบ รพ.ประกันสังคม - HR PRO")
st.markdown("##### สำหรับให้พนักงานตรวจสอบและเลือกโรงพยาบาลกรอกสิทธิประกันสังคม ( 3 อันดับ)")
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
    st.info("💡 วิธีใช้: เลือก จังหวัด, อำเภอ/เขต และ ตำบล/แขวง เพื่อดูโรงพยาบาลในพื้นที่และบริเวณใกล้เคียงสำหรับกรอกสิทธิประกันสังคม")
    
    # 1. กล่องเลือกจังหวัด
    provinces = sorted(df['จังหวัด'].unique())
    selected_province = st.selectbox("📌 ขั้นตอนที่ 1: เลือกจังหวัดของคุณ", provinces)
    
    df_filtered_prov = df[df['จังหวัด'] == selected_province]
    
    # 2. กล่องเลือกอำเภอ/เขต (เพิ่มตัวเลือกแสดงทั้งหมดในจังหวัดตามคำขอ)
    amphoes = sorted(df_filtered_prov['อำเภอ / เขต'].unique())
    selected_amphoe = st.selectbox("🔍 ขั้นตอนที่ 2: เลือกอำเภอ / เขต ของคุณ", ["-- แสดงทุกอำเภอในจังหวัดนี้ --"] + amphoes)
    
    st.markdown("---")
    
    # กรณีกดเลือก "แสดงทุกอำเภอในจังหวัดนี้"
    if selected_amphoe == "-- แสดงทุกอำเภอในจังหวัดนี้ --":
        st.subheader(f"📋 รายชื่อโรงพยาบาลทั้งหมดใน จังหวัด {selected_province}")
        st.caption("💡 พนักงานสามารถดูภาพรวมทั้งจังหวัดเพื่อเลือกโรงพยาบาลกรอก 3 อันดับได้จากตารางด้านล่างนี้")
        
        df_all_province = df_filtered_prov.copy()
        if not df_all_province.empty:
            df_all_province['ลำดับ'] = range(1, len(df_all_province) + 1)
            st.dataframe(
                df_all_province[['ลำดับ', 'รายชื่อโรงพยาบาล', 'ตำบล / แขวง', 'อำเภอ / เขต', 'จังหวัด']], 
                hide_index=True, 
                use_container_width=True
            )
            st.success(f"🎉 พบโรงพยาบาลในจังหวัด {selected_province} ทั้งหมด {len(df_all_province)} แห่ง")
        else:
            st.warning(f"ไม่พบข้อมูลโรงพยาบาลในจังหวัด {selected_province}")
            
    else:
        # หากเจาะจงอำเภอ คัดกรองข้อมูลตามอำเภอที่เลือก
        df_filtered_amphoe = df_filtered_prov[df_filtered_prov['อำเภอ / เขต'] == selected_amphoe]
        
        # 3. กล่องเลือกตำบล/แขวง
        tambons = sorted(df_filtered_amphoe['ตำบล / แขวง'].unique())
        selected_tambon = st.selectbox("🏠 ขั้นตอนที่ 3: เลือกตำบล / แขวง ที่คุณอยู่ปัจจุบัน", ["-- แสดงทุกตำบลในอำเภอนี้ --"] + tambons)
        
        st.markdown("---")
        
        # กรณีเจาะจงตำบล
        if selected_tambon != "-- แสดงทุกตำบลในอำเภอนี้ --":
            st.subheader(f"📍 1. โรงพยาบาลใน ตำบล/แขวง {selected_tambon}")
            df_main = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] == selected_tambon].copy()
            
            if not df_main.empty:
                df_main['ลำดับ'] = range(1, len(df_main) + 1)
                st.dataframe(df_main[['ลำดับ', 'รายชื่อโรงพยาบาล', 'ตำบล / แขวง', 'อำเภอ / เขต']], hide_index=True, use_container_width=True)
            else:
                st.warning(f"ไม่พบโรงพยาบาลในตำบล {selected_tambon} โดยตรง (กรุณาเลือกจากตำบลใกล้เคียงด้านล่าง)")
                
            # แสดงตำบลใกล้เคียงในอำเภอเดียวกัน
            st.subheader("🔄 2. โรงพยาบาลแนะนำในตำบลใกล้เคียง (ในอำเภอ/เขตเดียวกัน)")
            st.caption("💡 พนักงานสามารถใช้รายชื่อด้านล่างนี้กรอกเป็น โรงพยาบาลอันดับ 2 และอันดับ 3 เผื่อที่แรกเต็มได้เลยครับ")
            
            df_sub = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] != selected_tambon].copy()
            if not df_sub.empty:
                df_sub['ลำดับ'] = range(1, len(df_sub) + 1)
                st.dataframe(df_sub[['ลำดับ', 'รายชื่อโรงพยาบาล', 'ตำบล / แขวง', 'อำเภอ / เขต']], hide_index=True, use_container_width=True)
            else:
                st.text("ไม่มีตำบลอื่นที่มีโรงพยาบาลเพิ่มเติมในอำเภอนี้")
                
        else:
            # กรณีเลือกแสดงทุกตำบลในอำเภอ
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
