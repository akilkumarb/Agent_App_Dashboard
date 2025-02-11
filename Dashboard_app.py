import pandas as pd 
import numpy as np
import plotly.express as px
import streamlit as st 



st.set_page_config(page_title='Sales Dashboard', layout='wide')

st.sidebar.header("Upload Files")
device_order_data= st.sidebar.file_uploader("Upload Device Order Summary", type=['xls', 'xlsx'])
fos_data = st.sidebar.file_uploader("Upload FOS Master Details", type=['xls', 'xlsx'])
#st.set_page_config(page_title='Sales Dashboard',layout='wide')
#device_order_data=pd.read_excel("C:/Users/akil.kumarb/Documents/Python Projects/Device Order Summary 11-2-25.xlsx")

## Sidebar------------ 
st.sidebar.header("Filters")
bh=st.sidebar.multiselect(
    "BH:",
    options=device_order_data["BH_Name"].unique(),
    default=device_order_data["BH_Name"].unique()
)

zone=st.sidebar.multiselect(
    "Zone:",
    options=device_order_data["Zone"].unique(),
    default=device_order_data["Zone"].unique()
)

device_model=st.sidebar.multiselect(
    "Device model:",
    options=device_order_data["device_model"].unique(),
    default=device_order_data["device_model"].unique()
)
reporting_manager=st.sidebar.multiselect(
    "Reporting Manager:",
    options=device_order_data["Reporting Manager"].unique(),
    default=device_order_data["Reporting Manager"].unique()
)

device_order_data_selection=device_order_data.query("`BH_Name` == @bh & `Zone` == @zone & `device_model` == @device_model & `Reporting Manager` == @reporting_manager")
### st.dataframe(device_order_data_selection)

st.title("Razorpay Agent App Dashboard")
st.markdown("##")

# Create the bar chart




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
total_row = pd.DataFrame({'Till_Date_Cases': [active_merchant_mis['Till_Date_Cases'].sum()],
                         'KYC_qualified' : [active_merchant_mis['KYC_qualified'].sum()],
                         'Under_Review': [active_merchant_mis['Under_Review'].sum()],
                         'Needs_clarification': [active_merchant_mis['Needs_clarification'].sum()],
                         'Rejected':[active_merchant_mis['Rejected'].sum()],
                         'Pending_Status_from_Risk':[active_merchant_mis['Pending_Status_from_Risk'].sum()],
                         'Installed':[active_merchant_mis['Installed'].sum()],
                         'TID_Generation_Pending':[active_merchant_mis['TID_Generation_Pending'].sum()],
                         'Pending_Installation':[active_merchant_mis['Pending_Installation'].sum()]}, index=[('Total')])



#mis_summary_data=pd.merge(left=mis_data,right=device_order_data_selection,on=['BH_Name','Reporting Manager'],how='left')


### KPI's 
total_device_orders=int(device_order_data_selection['device_count'].sum())
##unique_merchants=len(device_order_data_selection['merchant_id'].unique())
###device_order_value=round(device_order_data_selection['order_amount'].sum(),2)
tids_received=len(device_order_data_selection[~device_order_data_selection['tid_received_date'].isna()]['tid_received_date'])

unique_merchants=len(device_mis['merchant_id'].unique())
device_order_amount=round(device_mis['order_amount'].sum(),2)
total_login_count=device_mis['signup_date'].count()


left_column,middle_column_1,middle_column_2,right_column=st.columns(4)

with left_column:
    st.subheader('Unique Merchants')
    st.subheader(unique_merchants)
with middle_column_1:
    st.subheader('Total order Amount ')
    st.subheader(f'{device_order_amount:,}')

with right_column:
    st.subheader('Total Login Count')
    st.subheader(total_login_count)

#with right_column:
#st.subheader('Total Order Amount')
#st.subheader(f'{device_order_value:,}')
    
st.markdown("---") 

### KPI's 

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
active_merchant_mis = pd.concat([active_merchant_mis, total_row])
st.subheader('MIS Summary')
st.dataframe(active_merchant_mis)





grouped_df=device_order_data.groupby(by=['BH_Name','Reporting Manager']).agg(FOS_with_lead=pd.NamedAgg(column='fos_id', aggfunc='nunique'),
                                                                             Login_count=pd.NamedAgg(column='Reporting Manager', aggfunc='count'))

grouped_df=grouped_df.reset_index()
#fos_data=pd.read_excel("C:/Users/akil.kumarb/Documents/Python Projects/Razorpay Agent App.xlsx",sheet_name='FOS Master Details')
grp_data_1=fos_data.groupby(by=['BH_Name','Reporting Manager']).agg(Total_FOS=pd.NamedAgg(column='Name of the FOS', aggfunc='nunique'))
final_data=pd.merge(left=grp_data_1,right=grouped_df,on=['BH_Name','Reporting Manager'],how='left')
final_data=final_data[['BH_Name','Reporting Manager','Total_FOS','FOS_with_lead','Login_count']]
final_data.sort_values(by=['BH_Name','Reporting Manager'],inplace=True,ascending=True)
final_data['%FOS With Lead Entry']=round((final_data['FOS_with_lead']/final_data['Login_count'])*100,0)
final_data.replace(np.nan,0,inplace=True)
subtotal = (
    final_data.groupby('BH_Name')[['Total_FOS', 'FOS_with_lead', 'Login_count']]
    .sum()
    .reset_index()
)
subtotal['Reporting Manager'] = 'Subtotal'
subtotal['%FOS With Lead Entry'] = round(
    (subtotal['FOS_with_lead'] / subtotal['Login_count']) * 100, 0
)
subtotal.replace(np.nan, 0, inplace=True)

final_data_with_subtotals = pd.concat([final_data, subtotal], ignore_index=True)

final_data_with_subtotals['Sort_Key'] = final_data_with_subtotals['Reporting Manager'].apply(
    lambda x: 1 if x == 'Subtotal' else 0
)

# Sort to ensure subtotals are always at the bottom of each BH_Name group
final_data_with_subtotals.sort_values(
    by=['BH_Name', 'Sort_Key', 'Reporting Manager'],  # Sort by 'Sort_Key' to push 'Subtotal' last
    inplace=True,
    ascending=[True, True, True]  # Ascending order throughout
)

# Drop the helper column
final_data_with_subtotals.drop(columns=['Sort_Key'], inplace=True)

# Reset index for a cleaner look
final_data_with_subtotals.reset_index(drop=True, inplace=True)

# Display final result
#print(final_data_with_subtotals)
final_data_selection=final_data_with_subtotals.query("`BH_Name` == @bh &  `Reporting Manager` == @reporting_manager")

st.subheader('Adoption Summary')
st.dataframe(final_data_with_subtotals)



fos_data=fos_data[fos_data['Active Status']=='Active']
mis_data=fos_data.groupby(['Reporting Manager','Team','BH_Name','Zone']).agg(Total_FOS=pd.NamedAgg(column='Name of the FOS', aggfunc='nunique'))
#print(mis_data.head(5))


st.subheader('Device Order Summary Raw Data')
st.dataframe(device_mis)
