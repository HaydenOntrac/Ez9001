#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from prettytable import PrettyTable  # Assuming PrettyTable is still used for your table output
import io

# Define your CSV file paths here (use raw strings or double backslashes)
swl_csv = 'excavator_swl.csv'  # Ensure this file exists
bucket_csv = 'bucket_data.csv'  # Make sure this file exists
bhc_bucket_csv = 'bhc_bucket_data.csv'  # Make sure this file exists
dump_truck_csv = 'dump_trucks.csv'  # Path to dump truck CSV

# Load datasets
def load_bucket_data(bucket_csv):
    return pd.read_csv(bucket_csv)

def load_bhc_bucket_data(bhc_bucket_csv):
    return pd.read_csv(bhc_bucket_csv)

def load_dump_truck_data(dump_truck_csv):
    return pd.read_csv(dump_truck_csv)

def load_excavator_swl_data(swl_csv):
    swl_data = pd.read_csv(swl_csv)
    swl_data['boom_length'] = pd.to_numeric(swl_data['boom_length'], errors='coerce')
    swl_data['arm_length'] = pd.to_numeric(swl_data['arm_length'], errors='coerce')
    swl_data['CWT'] = pd.to_numeric(swl_data['CWT'], errors='coerce')
    swl_data['shoe_width'] = pd.to_numeric(swl_data['shoe_width'], errors='coerce')
    swl_data['reach'] = pd.to_numeric(swl_data['reach'], errors='coerce')
    swl_data['class'] = pd.to_numeric(swl_data['class'], errors='coerce')
    return swl_data

# Load the data
dump_truck_data = load_dump_truck_data(dump_truck_csv)
swl_data = load_excavator_swl_data(swl_csv)

# Main Streamlit App UI
def app():
    st.title('Bucket Sizing and Productivity Calculator')

# Streamlit UI
st.title("Excavator and Dump Truck Selection")

# User Inputs
email = st.text_input("Enter your email")

# Excavator inputs
excavator_make = st.selectbox("Select Excavator Make", swl_data['make'].unique())
excavator_model = st.selectbox("Select Excavator Model", swl_data[swl_data['make'] == excavator_make]['model'].unique())

boom_length = st.selectbox("Select Boom Length (m)", swl_data[swl_data['model'] == excavator_model]['boom_length'].unique())
arm_length = st.selectbox("Select Arm Length (m)", swl_data[swl_data['model'] == excavator_model]['arm_length'].unique())
cwt = st.selectbox("Select Counterweight (CWT in kg)", swl_data[swl_data['model'] == excavator_model]['CWT'].unique())
shoe_width = st.selectbox("Select Shoe Width (mm)", swl_data[swl_data['model'] == excavator_model]['shoe_width'].unique())
reach = st.selectbox("Select Reach (m)", swl_data[swl_data['model'] == excavator_model]['reach'].unique())

# Dump truck inputs
truck_brand = st.selectbox("Select Dump Truck Brand", dump_truck_data['brand'].unique())
truck_type = st.selectbox("Select Dump Truck Type", dump_truck_data[dump_truck_data['brand'] == truck_brand]['type'].unique())
truck_model = st.selectbox("Select Dump Truck Model", dump_truck_data[(dump_truck_data['brand'] == truck_brand) & 
                                                                     (dump_truck_data['type'] == truck_type)]['model'].unique())
truck_payload = st.selectbox("Select Dump Truck Payload (tons)", dump_truck_data[dump_truck_data['model'] == truck_model]['payload'].unique())

# Additional Inputs
material_density = st.number_input("Material Density (kg/m³)", min_value=0.0)
quick_hitch_weight = st.number_input("Quick Hitch Weight (kg)", min_value=0.0)
current_bucket_size = st.number_input("Current Bucket Size (m³)", min_value=0.0)
current_bucket_weight = st.number_input("Current Bucket Weight (kg)", min_value=0.0)
machine_swings_per_minute = st.number_input("Machine Swings per Minute", min_value=0.0)

# Checkbox for BHC buckets
select_bhc = st.checkbox("Select from BHC buckets only")

# Function to calculate SWL match
def find_matching_swl(user_data):
    matching_excavator = swl_data[
        (swl_data['make'] == user_data['make']) &
        (swl_data['model'] == user_data['model']) &
        (swl_data['CWT'] == user_data['cwt']) &
        (swl_data['shoe_width'] == user_data['shoe_width']) &
        (swl_data['reach'] == user_data['reach']) &
        (swl_data['boom_length'] == user_data['boom_length']) &
        (swl_data['arm_length'] == user_data['arm_length'])
    ]
    if matching_excavator.empty:
        return None
    swl = matching_excavator.iloc[0]['swl']
    return swl

# Function to calculate bucket load
def calculate_bucket_load(bucket_size, material_density):
    return bucket_size * material_density

def select_optimal_bucket(user_data, bucket_data, swl):
    current_bucket_size = user_data['current_bucket_size']
    optimal_bucket = None
    highest_bucket_size = 0

    selected_model = user_data['model']
    excavator_class = swl_data[swl_data['model'] == selected_model]['class'].iloc[0]

    for index, bucket in bucket_data.iterrows():
        if bucket['class'] > excavator_class + 10:
            continue

        bucket_load = calculate_bucket_load(bucket['bucket_size'], user_data['material_density'])
        total_bucket_weight = user_data['quick_hitch_weight'] + bucket_load + bucket['bucket_weight']

        if total_bucket_weight <= swl and bucket['bucket_size'] > highest_bucket_size:
            highest_bucket_size = bucket['bucket_size']
            optimal_bucket = {
                'bucket_name': bucket['bucket_name'],
                'bucket_size': highest_bucket_size,
                'bucket_weight': bucket['bucket_weight'],
                'total_bucket_weight': total_bucket_weight
            }

    return optimal_bucket

# Get user input data
user_data = {
    'make': excavator_make,
    'model': excavator_model,
    'boom_length': boom_length,
    'arm_length': arm_length,
    'cwt': cwt,
    'shoe_width': shoe_width,
    'reach': reach,
    'material_density': material_density,
    'quick_hitch_weight': quick_hitch_weight,
    'current_bucket_size': current_bucket_size,
    'current_bucket_weight': current_bucket_weight,
    'dump_truck_payload': truck_payload,
    'machine_swings_per_minute': machine_swings_per_minute
}

# Find matching SWL and optimal bucket
# Add a "Calculate" button
calculate_button = st.button("Calculate")

# Run calculations only when the button is pressed
if calculate_button:
    swl = find_matching_swl(user_data)
    if swl:
        st.write(f"Matching Excavator SWL: {swl} kg")
    
        # Load selected bucket data
        selected_bucket_csv = bhc_bucket_csv if select_bhc else bucket_csv
        bucket_data = load_bucket_data(selected_bucket_csv)
    
        optimal_bucket = select_optimal_bucket(user_data, bucket_data, swl)
    
        if optimal_bucket:
            st.write(f"Optimal Bucket: {optimal_bucket['bucket_name']} ({optimal_bucket['bucket_size']} m³)")
            st.write(f"Total Bucket Weight: {optimal_bucket['total_bucket_weight']} kg")
        else:
            st.write("No suitable bucket found within SWL limits.")
    else:
        st.write("No matching excavator configuration found!")
    
    def process_user_data(user_data, is_bhc_selected):
        selected_bucket_csv = bhc_bucket_csv if is_bhc_selected else bucket_csv
        bucket_data = load_bucket_data(selected_bucket_csv)
        swl = find_matching_swl(user_data)
        if swl is None:
            return
    
        optimal_bucket = select_optimal_bucket(user_data, bucket_data, swl)
        
        if optimal_bucket:
            old_capacity = user_data['current_bucket_size']
            new_capacity = optimal_bucket['bucket_size']
            old_payload = calculate_bucket_load(old_capacity, user_data['material_density'])
            new_payload = calculate_bucket_load(new_capacity, user_data['material_density'])
    
            dump_truck_payload = user_data['dump_truck_payload'] * 1000
            machine_swings_per_minute = user_data['machine_swings_per_minute']
    
            # Total suspended load
            old_total_load = old_payload + user_data['current_bucket_weight'] + user_data['quick_hitch_weight']
            new_total_load = optimal_bucket['total_bucket_weight']  # Corrected variable
    
    
            # Adjust payload to achieve whole or near-whole swings for the new payload
            swings_to_fill_truck_new = dump_truck_payload / new_payload
            swings_to_fill_truck_old = dump_truck_payload / old_payload
    
            # Time to fill truck in minutes
            time_to_fill_truck_old = swings_to_fill_truck_old / machine_swings_per_minute
            time_to_fill_truck_new = swings_to_fill_truck_new / machine_swings_per_minute
    
            # Average number of trucks per hour at 75% efficiency
            avg_trucks_per_hour_old = (60 / time_to_fill_truck_old) * 0.75 if time_to_fill_truck_old > 0 else 0
            avg_trucks_per_hour_new = (60 / time_to_fill_truck_new) * 0.75 if time_to_fill_truck_new > 0 else 0
    
            # Swings per hour
            swings_per_hour_old = swings_to_fill_truck_old * avg_trucks_per_hour_old
            swings_per_hour_new = swings_to_fill_truck_new * avg_trucks_per_hour_new
    
            # Total swings per hour
            total_swings_per_hour = 60 * machine_swings_per_minute
    
            # Production (t/hr)
            total_tonnage_per_hour_old = total_swings_per_hour * old_capacity * user_data['material_density'] / 1000
            total_tonnage_per_hour_new = total_swings_per_hour * new_capacity * user_data['material_density'] / 1000
    
            # Production (t/hr)
            tonnage_per_hour_old = avg_trucks_per_hour_old * dump_truck_payload / 1000
            tonnage_per_hour_new = avg_trucks_per_hour_new * dump_truck_payload / 1000
    
            # Assuming 1800 swings in a day
            total_m3_per_day_old = 1000 * old_capacity
            total_m3_per_day_new = 1000 * new_capacity
    
            # Total tonnage per day
            total_tonnage_per_day_old = total_m3_per_day_old * user_data['material_density'] / 1000
            total_tonnage_per_day_new = total_m3_per_day_new * user_data['material_density'] / 1000
    
            # Total number of trucks per day
            total_trucks_per_day_old = total_tonnage_per_day_old / dump_truck_payload * 1000
            total_trucks_per_day_new = total_tonnage_per_day_new / dump_truck_payload * 1000
    
            # Create a DataFrame for the comparison table
            data = {
                'Description': [
                    'Side-By-Side Bucket Comparison', 'Capacity (m³)', 'Material Density (kg/m³)', 'Bucket Payload (kg)', 
                    'Total Suspended Load (kg)', '', 
                    'Loadout Productivity & Truck Pass Simulation', 'Dump Truck Payload (kg)', 'Avg No. Swings to Fill Truck', 
                    'Time to Fill Truck (min)', 'Avg Trucks/Hour @ 75% eff', 'Total Swings/Hour', '', 
                    'Swings Per Day Side-By-Side Simulation', 'Total Tonnage/hr', 'Total m³/Day', 
                    'Total Tonnage/Day', 'Total Trucks/Day', '', 
                    'Improved Cycle Time Simulation', 'Total Tonnage/hr', 'Total m³/Day', 
                    'Total Tonnage/Day', 'Total Trucks/Day'
                ],
                'OLD Bucket': [
                    '', f"{old_capacity:.1f}", f"{user_data['material_density']:.1f}", f"{old_payload:.1f}", 
                    f"{old_total_load:.1f}", '', 
                    '', f"{dump_truck_payload:.1f}", f"{swings_to_fill_truck_old:.1f}", 
                    f"{time_to_fill_truck_old:.1f}", f"{avg_trucks_per_hour_old:.1f}", f"{swings_per_hour_old:.1f}", '', 
                    '', f"{total_tonnage_per_hour_old:.1f}", f"{total_m3_per_day_old:.1f}", 
                    f"{total_tonnage_per_day_old:.1f}", f"{total_trucks_per_day_old:.1f}", '', 
                    '', f"{total_tonnage_per_hour_old:.1f}", f"{total_m3_per_day_old:.1f}", 
                    f"{total_tonnage_per_day_old:.1f}", f"{total_trucks_per_day_old:.1f}"
                ],
                'New Bucket': [
                    '', f"{new_capacity:.1f}", f"{user_data['material_density']:.1f}", f"{new_payload:.1f}", 
                    f"{new_total_load:.1f}", '', 
                    '', f"{dump_truck_payload:.1f}", f"{swings_to_fill_truck_new:.1f}", 
                    f"{time_to_fill_truck_new:.1f}", f"{avg_trucks_per_hour_new:.1f}", f"{swings_per_hour_new:.1f}", '', 
                    '', f"{total_tonnage_per_hour_new:.1f}", f"{total_m3_per_day_new:.1f}", 
                    f"{total_tonnage_per_day_new:.1f}", f"{total_trucks_per_day_new:.1f}", '', 
                    '', f"{1.1 * total_tonnage_per_hour_new:.1f}", f"{1.1 * total_m3_per_day_new:.1f}", 
                    f"{1.1 * total_tonnage_per_day_new:.1f}", f"{1.1 * total_trucks_per_day_new:.1f}"
                ],
                'Difference': [
                    '', f"{new_capacity - old_capacity:.1f}", '-', f"{new_payload - old_payload:.1f}", 
                    f"{new_total_load - old_total_load:.1f}", '', 
                    '', '-', f"{swings_to_fill_truck_new - swings_to_fill_truck_old:.1f}", 
                    f"{time_to_fill_truck_new - time_to_fill_truck_old:.1f}", 
                    f"{avg_trucks_per_hour_new - avg_trucks_per_hour_old:.1f}", 
                    f"{swings_per_hour_new - swings_per_hour_old:.1f}", '', 
                    '', f"{total_tonnage_per_hour_new - total_tonnage_per_hour_old:.1f}", 
                    f"{total_m3_per_day_new - total_m3_per_day_old:.1f}", 
                    f"{total_tonnage_per_day_new - total_tonnage_per_day_old:.1f}", 
                    f"{total_trucks_per_day_new - total_trucks_per_day_old:.1f}", '', 
                    '', f"{total_tonnage_per_hour_new - total_tonnage_per_hour_old:.1f}", 
                    f"{total_m3_per_day_new - total_m3_per_day_old:.1f}", 
                    f"{total_tonnage_per_day_new - total_tonnage_per_day_old:.1f}", 
                    f"{total_trucks_per_day_new - total_trucks_per_day_old:.1f}"
                ],
                '% Difference': [
                    '', f"{(new_payload - old_payload) / old_payload * 100:.1f}%", '-', f"{(new_payload - old_payload) / old_payload * 100:.1f}%", 
                    f"{(new_total_load - old_total_load) / old_total_load * 100:.1f}%", '', 
                    '', '-', f"{(swings_to_fill_truck_new - swings_to_fill_truck_old) / swings_to_fill_truck_old * 100:.1f}%", 
                    f"{(time_to_fill_truck_new - time_to_fill_truck_old) / time_to_fill_truck_old * 100:.1f}%", 
                    f"{(avg_trucks_per_hour_new - avg_trucks_per_hour_old) / avg_trucks_per_hour_old * 100:.1f}%", '-', '', 
                    '', f"{(total_tonnage_per_hour_new - total_tonnage_per_hour_old) / total_tonnage_per_hour_old * 100:.1f}%", 
                    f"{(total_m3_per_day_new - total_m3_per_day_old) / total_m3_per_day_old * 100:.1f}%", 
                    f"{(total_tonnage_per_day_new - total_tonnage_per_day_old) / total_tonnage_per_day_old * 100:.1f}%", 
                    f"{(total_trucks_per_day_new - total_trucks_per_day_old) / total_trucks_per_day_old * 100:.1f}%", '', 
                    '', f"{(1.1 * total_tonnage_per_hour_new - total_tonnage_per_hour_old) / total_tonnage_per_hour_old * 100:.1f}%", 
                    f"{(1.1 * total_m3_per_day_new - total_m3_per_day_old) / total_m3_per_day_old * 100:.1f}%", 
                    f"{(1.1 * total_tonnage_per_day_new - total_tonnage_per_day_old) / total_tonnage_per_day_old * 100:.1f}%", 
                    f"{(1.1 * total_trucks_per_day_new - total_trucks_per_day_old) / total_trucks_per_day_old * 100:.1f}%"
                ]
            }
            
            df = pd.DataFrame(data)
            return df
        else:
            return None

else:
    st.write("Please select options and press 'Calculate' to proceed.")
        
# Function to generate Excel file
def generate_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Productivity Study')
    # Return the Excel content as bytes
    return output.getvalue()

# Show table
df = process_user_data(user_data, select_bhc)
if df is not None:
    st.dataframe(df)
    excel_file = generate_excel(df)
    st.download_button(
        label="Download Excel File",
        data=excel_file,
        file_name="productivity_study.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Run the Streamlit app
if __name__ == '__main__':
    app()


