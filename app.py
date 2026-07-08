import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="LinkedIn Job Tracker", page_icon="💼", layout="wide")

# 🔒 SECURITY GATE
YOUR_PASSWORD = st.secrets["app_password"]

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

//if not st.session_state["authenticated"]:
//    st.title("🔒 Data Protection Access Gate")
//    user_input = st.text_input("Enter your application password:", type="password")
//    if st.button("Unlock Dashboard"):
//        if user_input == YOUR_PASSWORD:
st.session_state["authenticated"] = True
//            st.rerun()
//       else:
//            st.error("❌ Invalid password. Access Denied.")
//    st.stop()

# --- APPLICATION DASHBOARD ---
st.title("💼 Daily LinkedIn Job Change Auditor")
st.write("Upload your yesterday and today exports below to extract profile workspace shifts.")

col1, col2 = st.columns(2)
with col1:
    file_old = st.file_uploader("📂 Upload Yesterday's CSV File", type=["csv"], key="old_file")
with col2:
    file_new = st.file_uploader("📂 Upload Today's CSV File", type=["csv"], key="new_file")

def parse_linkedin_csv(file_buffer):
    """Dynamically skips LinkedIn disclaimer header lines to parse clean table columns."""
    content = file_buffer.getvalue().decode("utf-8").splitlines()
    start_row = 0
    for idx, line in enumerate(content):
        if "First Name" in line and "Last Name" in line:
            start_row = idx
            break
            
    file_buffer.seek(0)
    df = pd.read_csv(file_buffer, skiprows=start_row)
    df.columns = df.columns.str.strip()
    return df

# Evaluation Trigger
if file_old and file_new:
    if st.button("⚡ Run Comparative Analysis", type="primary"):
        try:
            with st.spinner("Processing large network maps... Please wait."):
                df_old = parse_linkedin_csv(file_old)
                df_new = parse_linkedin_csv(file_new)
                
                # Format text strings and configure stable unique indices
                for df in [df_old, df_new]:
                    df['Unique_ID'] = (
                        df['First Name'].astype(str).str.strip() + "_" + 
                        df['Last Name'].astype(str).str.strip() + "_" + 
                        df['Connected On'].astype(str).str.strip()
                    )
                    df['Company'] = df['Company'].fillna('').astype(str).str.strip()
                    df['Position'] = df['Position'].fillna('').astype(str).str.strip()
                    df['URL'] = df['URL'].fillna('').astype(str).str.strip()

                df_old.set_index('Unique_ID', inplace=True)
                df_new.set_index('Unique_ID', inplace=True)
                
                intersected_profiles = df_old.index.intersection(df_new.index)
                changes_detected = []
                
                for uid in intersected_profiles:
                    old_co = df_old.loc[uid, 'Company']
                    new_co = df_new.loc[uid, 'Company']
                    
                    if isinstance(old_co, pd.Series): old_co = old_co.iloc[0]
                    if isinstance(new_co, pd.Series): new_co = new_co.iloc[0]
                    
                    if old_co != new_co and old_co != "":
                        first_name = df_new.loc[uid, 'First Name']
                        last_name = df_new.loc[uid, 'Last Name']
                        profile_url = df_new.loc[uid, 'URL']
                        
                        if isinstance(first_name, pd.Series): first_name = first_name.iloc[0]
                        if isinstance(last_name, pd.Series): last_name = last_name.iloc[0]
                        if isinstance(profile_url, pd.Series): profile_url = profile_url.iloc[0]
                        
                        full_name = f"{first_name} {last_name}"
                        
                        # Use the direct LinkedIn URL from the export!
                        final_url = profile_url if profile_url else f"https://www.linkedin.com/search/results/people/?keywords={full_name} {new_co}"
                        
                        changes_detected.append({
                            "Name": full_name,
                            "URL": final_url,
                            "Old": old_co,
                            "New": new_co
                        })
                
                # UI Render Module
                # --- NATIVE STREAMLIT UI RENDER MODULE ---
                if changes_detected:
                    st.success(f"🎉 Analysis Complete! Detected {len(changes_detected)} job changes.")
                    
                    # Convert our list of changes into a standard clean DataFrame
                    result_df = pd.DataFrame(changes_detected)
                    
                    # Reorder and rename columns for a polished look
                    result_df = result_df[["Name", "Old", "New", "URL"]]
                    
                    # Render using native Streamlit interactive tables
                    st.dataframe(
                        result_df,
                        column_config={
                            "Name": st.column_config.TextColumn("Connection Name", help="Name of your connection"),
                            "Old": st.column_config.TextColumn("Previous Company"),
                            "New": st.column_config.TextColumn("New Company"),
                            "URL": st.column_config.LinkColumn("LinkedIn Profile", display_text="🔎 View Profile")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("✅ Clear logs! No job changes found between these periods.")
                    
        except Exception as err:
            st.error(f"Failed parsing file configurations. Error: {err}")
