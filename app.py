import streamlit as st
import pandas as pd
import numpy as np

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
    .distance-tag {
        display: inline-block;
        background-color: #e2e8f0;
        color: #4a5568;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 3px;
        margin-top: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# แสดงโลโก้บริษัทขนาดเล็กไว้บนสุด (ถ้ามีไฟล์ company_logo.jpg)
try:
    st.image("company_logo.jpg", width=120)
except Exception:
    pass

# ส่วนหัวของหน้าเว็บ
st.title("🏥 ระบบตรวจสอบโรงพยาบาล")
st.markdown("##### ค้นหารายชื่อโรงพยาบาลเพื่อกรอกสิทธิประกันสังคม 3 อันดับ")
st.markdown("---")

# ฟังก์ชันคำนวณระยะทางระหว่างพิกัดสองจุด (Haversine Formula) คืนค่าเป็นกิโลเมตร
def haversine_distance(lat1, lon1, lat2, lon2):
    # แปลงองศาเป็นเรเดียน
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c  # รัศมีเฉลี่ยของโลกในหน่วยกิโลเมตร
    return km

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
                st.warning(f"⚠️ ไม่พบโรงพยาบาลในตำบล {selected_tambon} โดยตรง (โปรดเลือกจากพื้นที่แนะนำอิงตามพิกัดด้านล่าง)")
                
            # --- กลไกคำนวณจากพิกัดละติจูด ลองติจูด ในรัศมีที่ใกล้ที่สุด ---
            st.subheader("🔄 โรงพยาบาลแนะนำเพิ่มเติมในรัศมีใกล้เคียงที่สุด")
            st.caption("💡 คัดเลือกจากโรงพยาบาลที่พิกัดอยู่ใกล้เคียงคุณที่สุด 3 อันดับแรก เพื่อความสะดวกในการเดินทาง")
            
            # ตรวจสอบก่อนว่าในไฟล์ Excel มีคอลัมน์พิกัดครบไหม
            if 'latitude' in df.columns and 'longitude' in df.columns:
                
                # หาพิกัดศูนย์กลาง (ถ้ามี รพ. หลักในตำบลนั้น ให้ใช้พิกัดของรพ. นั้นเลย แต่ถ้าไม่มี ให้หาพิกัดเฉลี่ยของอำเภอนั้นแทน)
                if not df_main.empty and pd.notna(df_main.iloc[0]['latitude']):
                    center_lat = df_main.iloc[0]['latitude']
                    center_lon = df_main.iloc[0]['longitude']
                else:
                    center_lat = df_filtered_amphoe['latitude'].mean()
                    center_lon = df_filtered_amphoe['longitude'].mean()
                
                if pd.notna(center_lat) and pd.notna(center_lon):
                    # ดึงรายชื่อโรงพยาบาลทั้งหมดในจังหวัดนั้น (ยกเว้นตัวโรงพยาบาลหลักที่แสดงด้านบนไปแล้ว)
                    df_pool = df_filtered_prov.copy()
                    if not df_main.empty:
                        df_pool = df_pool[~df_pool['รายชื่อโรงพยาบาล'].isin(df_main['รายชื่อโรงพยาบาล'])]
                    
                    # คัดกรองแถวที่พิกัดไม่ว่าง
                    df_pool = df_pool[df_pool['latitude'].notna() & df_pool['longitude'].notna()]
                    
                    if not df_pool.empty:
                        # คำนวณระยะห่างของโรงพยาบาลทุกแห่งเทียบกับจุดศูนย์กลาง
                        df_pool['distance'] = haversine_distance(
                            center_lat, center_lon, 
                            df_pool['latitude'], df_pool['longitude']
                        )
                        
                        # เรียงลำดับจากระยะทางน้อยไปมาก (ใกล้ที่สุดอยู่บน) แล้วดึงมา 3 อันดับแรก
                        df_recommend_coords = df_pool.sort_values(by='distance').head(3)
                        
                        for idx, row in df_recommend_coords.iterrows():
                            st.markdown(f"""
                            <div class="hospital-card">
                                <div class="hospital-name">🏥 {row['รายชื่อโรงพยาบาล']}</div>
                                <div class="hospital-sub">📍 ต. {row['ตำบล / แขวง']} | อ. {row['อำเภอ / เขต']}</div>
                                <div class="distance-tag">📍 อยู่ห่างออกไปประมาณ {row['distance']:.1f} กม.</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color:gray;'>ไม่มีรายชื่อโรงพยาบาลอื่นในจังหวัดนี้ที่มีพิกัด</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:gray;'>ไม่สามารถคำนวณระยะทางได้เนื่องจากข้อมูลพิกัดในเขตนี้ไม่สมบูรณ์</p>", unsafe_allow_html=True)
            else:
                # ระบบสำรอง (Fallback) กรณีอัปเดตโค้ดแล้วแต่ยังไม่ได้อัปโหลดไฟล์ Excel ที่มีพิกัด ระบบจะดึงตามชื่ออำเภอให้แทนแบบเดิมเพื่อไม่ให้ระบบพัง
                df_sub_amphoe = df_filtered_amphoe[df_filtered_amphoe['ตำบล / แขวง'] != selected_tambon].copy()
                df_other_amphoe = df_filtered_prov[df_filtered_prov['อำเภอ / เขต'] != selected_amphoe].copy()
                df_recommend = pd.concat([df_sub_amphoe, df_other_amphoe], ignore_index=True).drop_duplicates(subset=['รายชื่อโรงพยาบาล'])
                
                if not df_recommend.empty:
                    for idx, row in df_recommend.head(3).iterrows():
                        st.markdown(f"""
                        <div class="hospital-card">
                            <div class="hospital-name">🏥 {row['รายชื่อโรงพยาบาล']}</div>
                            <div class="hospital-sub">📍 ต. {row['ตำบล / แขวง']} | อ. {row['อำเภอ / เขต']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
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
