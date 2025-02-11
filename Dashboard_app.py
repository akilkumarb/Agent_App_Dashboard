import pandas as pd 
import numpy as np
import plotly.express as px
import streamlit as st 

st.set_page_config(page_title='Sales Dashboard', layout='wide')

st.sidebar.header("Upload Files")
device_order_file = st.sidebar.file_uploader("Upload Device Order Summary", type=['xls', 'xlsx'])
fos_file = st.sidebar.file_uploader("Upload FOS Master Details", type=['xls', 'xlsx'])

# Load data only if files are uploaded
device_order_data = pd.read_excel(device_order_file) if device_order_file else None
fos_data = pd.read_excel(fos_file) if fos_file else None

if device_order_data is not None:
    st.sidebar.header("Filters")
    bh = st.sidebar.multiselect("BH:", options=device_order_data["BH_Name"].unique(),
                                default=device_order_data["BH_Name"].unique())
    zone = st.sidebar.multiselect("Zone:", options=device_order_data["Zone"].unique(),
                                   default=device_order_data["Zone"].unique())
    device_model = st.sidebar.multiselect("Device model:", options=device_order_data["device_model"].unique(),
                                          default=device_order_data["device_model"].unique())
    reporting_manager = st.sidebar.multiselect("Reporting Manager:", options=device_order_data["Reporting Manager"].unique(),
                                               default=device_order_data["Reporting Manager"].unique())
    
    device_order_data_selection = device_order_data.query("`BH_Name` == @bh & `Zone` == @zone & `device_model` == @device_model & `Reporting Manager` == @reporting_manager")
    
    st.title("Razorpay Agent App Dashboard")
    st.markdown("##")
    
    device_order_data_selection['check'] = device_order_data_selection['merchant_id'].duplicated(keep='first').map({False: 'unique', True: 'duplicate'})
    device_mis = device_order_data_selection
    
    active_merchant_mis = device_mis[(device_mis['check'] == 'unique') & (~(device_mis['BH_Name'] == 'Test'))]
    active_merchant_mis = active_merchant_mis.groupby(by=['BH_Name', 'Reporting Manager']).agg(
        Till_Date_Cases=pd.NamedAgg(column='merchant_id', aggfunc='nunique'),
        KYC_qualified=pd.NamedAgg(column='pos_kyc_qualified_date', aggfunc='count'),
        Under_Review=pd.NamedAgg(column='pos_activation_status', aggfunc=lambda x: (x == 'under_review').sum()),
        Needs_clarification=pd.NamedAgg(column='pos_activation_status', aggfunc=lambda x: (x == 'needs_clarification').sum()),
        Rejected=pd.NamedAgg(column='pos_activation_status', aggfunc=lambda x: (x == 'rejected').sum()),
        Pending_Status_from_Risk=pd.NamedAgg(column='pos_activation_status', aggfunc=lambda x: x.isna().sum()),
        Installed=pd.NamedAgg(column='installation_date', aggfunc='count'),
        TID_Generation_Pending=pd.NamedAgg(column='tid_received_date', aggfunc=lambda x: ((x.isna()) & (active_merchant_mis.loc[x.index, 'pos_kyc_qualified_date'].notna())).sum()),
        Pending_Installation=pd.NamedAgg(column='installation_date', aggfunc=lambda x: ((x.isna()) & (active_merchant_mis.loc[x.index, 'tid_received_date'].notna())).sum())
    ).reset_index()
    
    st.subheader('MIS Summary')
    st.dataframe(active_merchant_mis)
    
    st.subheader('Device Order Summary Raw Data')
    st.dataframe(device_mis)
else:
    st.warning("Please upload the required files to proceed.")
