import os
import pandas as pd
import streamlit as st
from datetime import datetime

# List of allowed email IDs for uploading
ALLOWED_EMAILS = ["akil.kumarb@razorpay.com", "r.rahul@razorpay.com"]

# Get current user email (only works on Streamlit Community Cloud)
user_email = st.experimental_user.email if st.experimental_user else None

# Directory and file paths for saving data persistently
DATA_DIR = "data"
DEVICE_ORDER_FILE = os.path.join(DATA_DIR, "device_order_data.xlsx")
FOS_MASTER_FILE = os.path.join(DATA_DIR, "fos_data.xlsx")
TIMESTAMP_FILE = os.path.join(DATA_DIR, "timestamp.txt")

# Set Streamlit page configuration
st.set_page_config(page_title='Sales Dashboard', layout='wide')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Show upload option only for allowed users
if user_email in ALLOWED_EMAILS:
    st.sidebar.header("Upload Files")
    device_order_data_file = st.sidebar.file_uploader("Upload Device Order Summary", type=['xls', 'xlsx'])
    fos_data_file = st.sidebar.file_uploader("Upload FOS Master Details", type=['xls', 'xlsx'])

    # If new files are uploaded, save them and update timestamp
    if device_order_data_file:
        with open(DEVICE_ORDER_FILE, "wb") as f:
            f.write(device_order_data_file.getbuffer())
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if fos_data_file:
        with open(FOS_MASTER_FILE, "wb") as f:
            f.write(fos_data_file.getbuffer())
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Load data from saved files
if os.path.exists(DEVICE_ORDER_FILE):
    device_order_data = pd.read_excel(DEVICE_ORDER_FILE)
else:
    device_order_data = None

if os.path.exists(FOS_MASTER_FILE):
    fos_data = pd.read_excel(FOS_MASTER_FILE, sheet_name='FOS Master Details')
else:
    fos_data = None

# Load last update timestamp
if os.path.exists(TIMESTAMP_FILE):
    with open(TIMESTAMP_FILE, "r") as f:
        last_updated = f.read()
else:
    last_updated = "No data uploaded yet."

if device_order_data is not None and fos_data is not None:
    st.title("Razorpay Agent App Dashboard")
    st.write(f"Showing the latest uploaded data (Last updated: {last_updated})")

    



# Process and display data (your existing logic goes here)

if device_order_data is not None and fos_data is not None:
    st.sidebar.header("Filters")
    bh = st.sidebar.multiselect("BH:", options=device_order_data["BH_Name"].unique(), default=device_order_data["BH_Name"].unique())
    zone = st.sidebar.multiselect("Zone:", options=device_order_data["Zone"].unique(), default=device_order_data["Zone"].unique())
    device_model = st.sidebar.multiselect("Device model:", options=device_order_data["device_model"].unique(), default=device_order_data["device_model"].unique())
    reporting_manager = st.sidebar.multiselect("Reporting Manager:", options=device_order_data["Reporting Manager"].unique(), default=device_order_data["Reporting Manager"].unique())
    
    device_order_data_selection = device_order_data.query("`BH_Name` == @bh & `Zone` == @zone & `device_model` == @device_model & `Reporting Manager` == @reporting_manager")
    
    st.markdown("##")

    device_order_data_selection['check'] = device_order_data_selection['merchant_id'].duplicated(keep='first').map({False: 'unique', True: 'duplicate'})
    device_mis = device_order_data_selection.copy()

    active_merchant_mis = device_mis[(device_mis['check'] == 'unique') & (~(device_mis['BH_Name'] == 'Test'))]
    active_merchant_mis = active_merchant_mis.groupby(by=['BH_Name', 'Reporting Manager']).agg(
        Till_Date_Cases=('merchant_id', 'nunique'),
        KYC_qualified=('pos_kyc_qualified_date', 'count'),
        Under_Review=('pos_activation_status', lambda x: (x == 'under_review').sum()),
        Needs_clarification=('pos_activation_status', lambda x: (x == 'needs_clarification').sum()),
        Rejected=('pos_activation_status', lambda x: (x == 'rejected').sum()),
        Pending_Status_from_Risk=('pos_activation_status', lambda x: x.isna().sum()),
        Installed=('installation_date', 'count'),
        TID_Generation_Pending=('tid_received_date', lambda x: ((x.isna()) & (device_mis.loc[x.index, 'pos_kyc_qualified_date'].notna())).sum()),
        Pending_Installation=('installation_date', lambda x: ((x.isna()) & (device_mis.loc[x.index, 'tid_received_date'].notna())).sum())
    ).reset_index()
    
    st.markdown("---")
    
    total_device_orders = int(device_order_data_selection['device_count'].sum())
    unique_merchants = len(device_mis['merchant_id'].unique())
    device_order_amount = round(device_mis['order_amount'].sum(), 2)
    total_login_count = device_mis['signup_date'].count()
    
    left_column, middle_column_1, middle_column_2, right_column = st.columns(4)
    with left_column:
        st.subheader('Unique Merchants')
        st.subheader(unique_merchants)
    with middle_column_1:
        st.subheader('Total Order Amount')
        st.subheader(f'{device_order_amount:,}')
    with right_column:
        st.subheader('Total Login Count')
        st.subheader(total_login_count)
    
    st.markdown("---")
    device_order_data_selection['check']=device_order_data_selection['merchant_id'].duplicated(keep='first').map({False: 'unique', True: 'duplicate'})
    device_mis=device_order_data_selection

    #mis_summary_data=pd.merge(left=mis_data,right=device_order_data_selection,on=['BH_Name','Reporting Manager'],how='left')
    active_merchant_mis=device_mis[(device_mis['check']=='unique') & (~(device_mis['BH_Name']=='Test'))]
    active_merchant_mis=active_merchant_mis.groupby(by=['BH_Name','Reporting Manager']).agg(
    Till_Date_Cases=pd.NamedAgg(column='merchant_id',aggfunc='nunique'),KYC_qualified=pd.NamedAgg(column='pos_kyc_qualified_date',aggfunc='count'),
    Under_Review=pd.NamedAgg(column='pos_activation_status',aggfunc=lambda x: (x == 'under_review').sum()),
    Needs_clarification=pd.NamedAgg(column='pos_activation_status',aggfunc=lambda x: (x == 'needs_clarification').sum()),
    Rejected=pd.NamedAgg(column='pos_activation_status',aggfunc=lambda x: (x == 'rejected').sum()),
    Pending_Status_from_Risk=pd.NamedAgg(column='pos_activation_status', aggfunc=lambda x: x.isna().sum()),
    Installed=pd.NamedAgg(column='installation_date', aggfunc='count'),
    TID_Generation_Pending=pd.NamedAgg(column='tid_received_date', aggfunc=lambda x: ((x.isna()) & (active_merchant_mis.loc[x.index, 'pos_kyc_qualified_date'].notna())).sum()),
    Pending_Installation=pd.NamedAgg(column='installation_date', aggfunc=lambda x: ((x.isna()) & (active_merchant_mis.loc[x.index, 'tid_received_date'].notna())).sum())).reset_index()

    ## KPI's
    left_column,middle_column_1,middle_column_2,right_column=st.columns(4)
    with left_column:
        st.subheader('KYC Qualified Cases')
        st.subheader(active_merchant_mis['KYC_qualified'].sum())
    with middle_column_1:
        st.subheader('Under Review Cases')
        st.subheader(active_merchant_mis['Under_Review'].sum())
    with middle_column_2:
        st.subheader('Needs Clarification Cases')
        st.subheader(active_merchant_mis['Needs_clarification'].sum())
    with right_column:
        st.subheader('Installed')
        st.subheader(f'{active_merchant_mis['Installed'].sum()}')
    st.markdown("---")
    left_column,middle_column_1,middle_column_2,right_column=st.columns(4)
    with left_column:
        st.subheader('Rejected')
        st.subheader(active_merchant_mis['Rejected'].sum())
    with middle_column_1:
        st.subheader('Pending_Status_from_Risk')
        st.subheader(active_merchant_mis['Pending_Status_from_Risk'].sum())
    with middle_column_2:
        st.subheader('TID_Generation_Pending')
        st.subheader(active_merchant_mis['TID_Generation_Pending'].sum())
    with right_column:
        st.subheader('Pending_Installation')
        st.subheader(f'{active_merchant_mis['Pending_Installation'].sum()}')
        st.markdown("---")
        total_row = pd.DataFrame({'Till_Date_Cases': [active_merchant_mis['Till_Date_Cases'].sum()],
                             'KYC_qualified' : [active_merchant_mis['KYC_qualified'].sum()],
                             'Under_Review': [active_merchant_mis['Under_Review'].sum()],
                             'Needs_clarification': [active_merchant_mis['Needs_clarification'].sum()],
                             'Rejected':[active_merchant_mis['Rejected'].sum()],
                             'Pending_Status_from_Risk':[active_merchant_mis['Pending_Status_from_Risk'].sum()],
                             'Installed':[active_merchant_mis['Installed'].sum()],
                             'TID_Generation_Pending':[active_merchant_mis['TID_Generation_Pending'].sum()],
                             'Pending_Installation':[active_merchant_mis['Pending_Installation'].sum()]}, index=[('Total')])
        active_merchant_mis = pd.concat([active_merchant_mis, total_row])
    
    st.subheader('MIS Summary')
    st.dataframe(active_merchant_mis)
    
    grouped_df = device_order_data.groupby(by=['BH_Name', 'Reporting Manager']).agg(
        FOS_with_lead=('fos_id', 'nunique'),
        Login_count=('Reporting Manager', 'count')
    ).reset_index()
    
    grp_data_1 = fos_data.groupby(by=['BH_Name', 'Reporting Manager']).agg(Total_FOS=('Name of the FOS', 'nunique'))
    final_data = pd.merge(left=grp_data_1, right=grouped_df, on=['BH_Name', 'Reporting Manager'], how='left')
    final_data['%FOS With Lead Entry'] = round((final_data['FOS_with_lead'] / final_data['Login_count']) * 100, 0)
    final_data.fillna(0, inplace=True)
    
    subtotal = final_data.groupby('BH_Name')[['Total_FOS', 'FOS_with_lead', 'Login_count']].sum().reset_index()
    subtotal['Reporting Manager'] = 'Subtotal'
    subtotal['%FOS With Lead Entry'] = round((subtotal['FOS_with_lead'] / subtotal['Login_count']) * 100, 0)
    subtotal.fillna(0, inplace=True)
    
    final_data_with_subtotals = pd.concat([final_data, subtotal], ignore_index=True)
    final_data_with_subtotals['Sort_Key'] = final_data_with_subtotals['Reporting Manager'].apply(lambda x: 1 if x == 'Subtotal' else 0)
    final_data_with_subtotals.sort_values(by=['BH_Name', 'Sort_Key', 'Reporting Manager'], ascending=[True, True, True], inplace=True)
    final_data_with_subtotals.drop(columns=['Sort_Key'], inplace=True)
    final_data_with_subtotals.reset_index(drop=True, inplace=True)
    
    final_data_selection = final_data_with_subtotals[
    ((final_data_with_subtotals["BH_Name"].isin(bh) & final_data_with_subtotals["Reporting Manager"].isin(reporting_manager)) |
    (final_data_with_subtotals["Reporting Manager"] == "Subtotal"))
    & ~(final_data_with_subtotals["BH_Name"] == "Test")  # Exclude 'Test' BH
    ]


    st.subheader('Adoption Summary')
    st.dataframe(final_data_selection)
    
    st.subheader('Device Order Summary Raw Data')
    st.dataframe(device_mis)
