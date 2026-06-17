import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บให้เหมาะสมกับมือถือ
st.set_page_config(
    page_title="ระบบตรวจสอบโรงพยาบาลสำหรับสิทธิประกันสังคม",
    page_icon="🏥",
    layout="centered"  # จัดให้อยู่ตรงกลางหน้าจอพอดีกับขนาดมือถือ
)

# สไตล์ตกแต่งเพิ่มเติมให้แสดงผลบนมือถือสวยงาม (CSS Custom Styling)
st.markdown("""
    <style>
    /* ปรับขนาดตัวอักษรหลักในแอป */
    html, body, [data-testid="stMarkdownContainer"] {
        font-size: 15px;
    }
    /* ตกแต่งกล่องข้อมูลโรงพยาบาล */
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

# ส่วนหัวของหน้าเว็บ
st.title("🏥 ระบบตรวจสอบโรงพยาบาลประกันสังคม")
st.title("HR Pro")
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
            # วนลูปแสดงผลทีละโรงพยาบาลเป็นกล่องข้อความเพื่อให้แสดงผลบนมือถือสวยงาม
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
                
            # แสดงตำบลใกล้เคียงในอำเภอเดียวกัน
            st.subheader("🔄 โรงพยาบาลแนะนำเพิ่มเติม (ในอำเภอ/เขตเดียวกัน)")
            st.caption("💡 พนักงานสามารถใช้รายชื่อด้านล่างนี้กรอกเป็น โรงพยาบาลสำรองอันดับ 2 และ 3 ได้เลยค่ะ")
            
            df_sub = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] != selected_tambon].copy()
            if not df_sub.empty:
                for idx, row in df_sub.iterrows():
                    st.markdown(f"""
                    <div class="hospital-card">
                        <div class="hospital-name">🏥 {row['รายชื่อโรงพยาบาล']}</div>
                        <div class="hospital-sub">📍 ตำบล/แขวง: {row['ตำบล / แขวง']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.text("ไม่มีตำบลอื่นที่มีโรงพยาบาลเพิ่มเติมในอำเภอนี้")
                
        else:
            # กรณีเลือกแสดงทุกตำบลในอำเภอ
            st.subheader(f"📋 รายชื่อทั้งหมดใน อำเภอ/เขต {selected_amphoe}")
            df_all_amphoe = df_filtered_amphoe.copy()
            if not df_all_amphoe.empty:
                for idx, row in df_all_amphoe.iterrows():
                    st.markdown(f"""
                    <div class="hospital-card">
                        <div class="hospital-name">🏥 {row['รายชื่อโรงพยาบาล']}</div>
                        <div class="hospital-sub">📍 ต. {row['ตำบล / แขวง']} | อ. {row['อำเภอ / เขต']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.success(f"🎉 พบโรงพยาบาลทั้งหมด {len(df_all_amphoe)} แห่ง")
            else:
                st.warning("ไม่พบข้อมูลโรงพยาบาลในอำเภอนี้")

    st.markdown("---")
    st.caption("ระบบบริการข้อมูลภายในบริษัท พัฒนาโดยใช้ Streamlit (ฟรีไม่มีค่าใช้จ่าย)")
