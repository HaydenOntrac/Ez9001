#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
import io


# Define custom CSS
st.markdown("""
    <style>
    .custom-font {
        font-family: 'Arial'; /* Change to your desired font */
        font-size: 16px;      /* Adjust the font size */
        font-weight: bold;    /* Make the text bold */
        color: #000000;       /* Customize the text color */
    }
    </style>
    """, unsafe_allow_html=True)

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

# Function to generate CSV data from a DataFrame
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

def generate_csv(comparison_df):
    buffer = io.StringIO()
    comparison_df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

# Email sending function
def send_email_with_csv(email, csv_data):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'ONTRAC XMOR® Bucket Solution Results'
        msg['From'] = 'bucketontrac@gmail.com'
        msg['To'] = email

        # HTML content with a table for the comparison results
        html_content = f"""
        <html>
        <head>
            <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    text-align: left;
                    padding: 10px;
                }}
                th {{
                    background-color: #f2f2f2;
                    padding-top: 12px;
                    padding-bottom: 12px;
                    font-weight: bold;
                }}
                td {{
                    padding-top: 8px;
                    padding-bottom: 8px;
                }}
                    .subheading {{
                    background-color: #e0e0e0;
                    font-weight: bold;
                    text-align: center;
                    padding-top: 10px;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
        <h2>ONTRAC XMOR® Bucket Solution Results</h2>
        <p>G'day from the ONTRAC team! Here's your side-by-side comparison:</p>
        <table>
            <tr>
                <th>Description</th>
                <th>OLD Bucket</th>
                <th>New Bucket</th>
                <th>Difference</th>
                <th>% Difference</th>
            </tr>
        """
        
        for index, row in comparison_df.iterrows():
            # Apply subheading style to specific rows (0, 6, 14, and 21)
            if index in [0, 6, 14, 21]:
                html_content += f"""
                <tr>
                    <td class="subheading" colspan="5">{row['Description']}</td>
                </tr>
                """
            else:
                html_content += f"""
                <tr>
                    <td>{row['Description']}</td>
                    <td>{row['OLD Bucket']}</td>
                    <td>{row['New Bucket']}</td>
                    <td>{row['Difference']}</td>
                    <td>{row['% Difference']}</td>
                </tr>
                """
        
        html_content += """
        </table>
        <p>Thank you for using ONTRAC's bucket optimiser, we hope to hear from you soon!</p>
        </body>
        </html>
        """

        msg.add_alternative(html_content, subtype='html')
        
        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("bucketontrac@gmail.com", "albs gdyi jqzn fxgl")
            smtp.send_message(msg)
        st.success("Email sent successfully!")
         
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

        
# Main Streamlit App UI
def app():
    st.title('ONTRAC XMOR® Bucket Solution')

# Streamlit UI
st.title("ONTRAC XMOR® Bucket Solution\n\n")
st.title("Excavator Selection")

# Excavator inputs
excavator_make = st.selectbox("Select Excavator Make", swl_data['make'].unique())
excavator_model = st.selectbox("Select Excavator Model", swl_data[swl_data['make'] == excavator_make]['model'].unique())

boom_length = st.selectbox("Select Boom Length (m)", swl_data[swl_data['model'] == excavator_model]['boom_length'].unique())
arm_length = st.selectbox("Select Arm Length (m)", swl_data[swl_data['model'] == excavator_model]['arm_length'].unique())
cwt = st.selectbox("Select Counterweight (CWT in kg)", swl_data[swl_data['model'] == excavator_model]['CWT'].unique())
shoe_width = st.selectbox("Select Shoe Width (mm)", swl_data[swl_data['model'] == excavator_model]['shoe_width'].unique())
reach = st.selectbox("Select Reach (m)", swl_data[swl_data['model'] == excavator_model]['reach'].unique())

st.title("Dump Truck Selection")

# Dump truck inputs
truck_brand = st.selectbox("Select Dump Truck Brand", dump_truck_data['brand'].unique())
truck_type = st.selectbox("Select Dump Truck Type", dump_truck_data[dump_truck_data['brand'] == truck_brand]['type'].unique())
truck_model = st.selectbox("Select Dump Truck Model", dump_truck_data[(dump_truck_data['brand'] == truck_brand) & 
                                                                     (dump_truck_data['type'] == truck_type)]['model'].unique())
truck_payload = st.selectbox("Select Dump Truck Payload (tons)", dump_truck_data[dump_truck_data['model'] == truck_model]['payload'].unique())

# Additional Inputs
st.title("Additional Information")
material_density = st.number_input("Material Density (kg/m³)     e.g. 1500", min_value=0.0)
quick_hitch_weight = st.number_input("Quick Hitch Weight (kg)     Leave as 0 for direct pin", min_value=0.0)
current_bucket_size = st.number_input("Current Bucket Size (m³)", min_value=0.0)
current_bucket_weight = st.number_input("Current Bucket Weight (kg)", min_value=0.0)
machine_swings_per_minute = st.number_input("Machine Swings per Minute", min_value=0.0)

# Checkbox for BHC buckets
select_bhc = st.checkbox("Select from BHC buckets only (Heavy Duty)")

# Find matching SWL and optimal bucket
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
    
# Add a "Calculate" button
calculate_button = st.button("Calculate")

def generate_comparison_df(user_data, optimal_bucket, swl):
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

        # Truck Tonnes per hour
        truck_tonnage_per_hour_old = swings_per_hour_old * old_capacity * user_data['material_density'] / 1000
        truck_tonnage_per_hour_new = swings_per_hour_new * new_capacity * user_data['material_density'] / 1000

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

        Productivity = f"{(1.1 * total_tonnage_per_hour_new - total_tonnage_per_hour_old) / total_tonnage_per_hour_old * 100:.0f}%"
        st.session_state.productivity = Productivity
        volume_increase = f"{new_capacity - old_capacity:.1f}"
        st.session_state.volume_increase = volume_increase
        volume_increase_percentage = f"{(new_capacity - old_capacity) / old_capacity * 100:.1f}%"
        st.session_state.volume_increase_percentage = volume_increase_percentage
    


        # Create a DataFrame for the comparison table
        data = {
        'Description': [
            'Side-By-Side Bucket Comparison', 'Capacity (m³)', 'Material Density (kg/m³)', 'Bucket Payload (kg)', 
            'Total Suspended Load (kg)', '', 
            'Loadout Productivity & Truck Pass Simulation', 'Dump Truck Payload (kg)', 'Avg No. Swings to Fill Truck', 
            'Time to Fill Truck (min)', 'Avg Trucks/Hour @ 75% eff', 'Swings/Hour', 'Tonnes/Hour', '', 
            '1000 Swings Side-By-Side Simulation','Number of Swings', 'Tonnes/hr', 'Total Volume (m³)', 
            'Total Tonnes', 'Total Trucks', '', 
            '10% Improved Cycle Time Simulation','Number of Swings', 'Tonnes/hr', 'Total Volume (m³)', 
            'Total Tonnes', 'Total Trucks'
        ],
        'OLD Bucket': [
            '', f"{old_capacity:.1f}", f"{user_data['material_density']:.0f}", f"{old_payload:.0f}", 
            f"{old_total_load:.0f}", '', 
            '', f"{dump_truck_payload:.0f}", f"{swings_to_fill_truck_old:.1f}", 
            f"{time_to_fill_truck_old:.1f}", f"{avg_trucks_per_hour_old:.1f}", f"{swings_per_hour_old:.0f}", f"{truck_tonnage_per_hour_old:.0f}", '', '', 
            '1000', f"{total_tonnage_per_hour_old:.0f}", f"{total_m3_per_day_old:.0f}", 
            f"{total_tonnage_per_day_old:.0f}", f"{total_trucks_per_day_old:.0f}", '', '',
            '1000', f"{total_tonnage_per_hour_old:.0f}", f"{total_m3_per_day_old:.0f}", 
            f"{total_tonnage_per_day_old:.0f}", f"{total_trucks_per_day_old:.0f}"
        ],
        'New Bucket': [
            '', f"{new_capacity:.1f}", f"{user_data['material_density']:.0f}", f"{new_payload:.0f}", 
            f"{new_total_load:.0f}", '', 
            '', f"{dump_truck_payload:.0f}", f"{swings_to_fill_truck_new:.1f}", 
            f"{time_to_fill_truck_new:.1f}", f"{avg_trucks_per_hour_new:.1f}", f"{swings_per_hour_new:.0f}", f"{truck_tonnage_per_hour_new:.0f}", '', '',
            '1000', f"{total_tonnage_per_hour_new:.0f}", f"{total_m3_per_day_new:.0f}", 
            f"{total_tonnage_per_day_new:.0f}", f"{total_trucks_per_day_new:.0f}", '', '',
            '1100', f"{1.1 * total_tonnage_per_hour_new:.0f}", f"{1.1 * total_m3_per_day_new:.0f}", 
            f"{1.1 * total_tonnage_per_day_new:.0f}", f"{1.1 * total_trucks_per_day_new:.0f}"
        ],
        'Difference': [
            '', f"{new_capacity - old_capacity:.1f}", '-', f"{new_payload - old_payload:.0f}", 
            f"{new_total_load - old_total_load:.0f}", '', 
            '', '-', f"{swings_to_fill_truck_new - swings_to_fill_truck_old:.1f}", 
            f"{time_to_fill_truck_new - time_to_fill_truck_old:.1f}", 
            f"{avg_trucks_per_hour_new - avg_trucks_per_hour_old:.1f}", 
            f"{swings_per_hour_new - swings_per_hour_old:.0f}", 
            f"{truck_tonnage_per_hour_new - truck_tonnage_per_hour_old:.0f}", 
            '', '', '-',f"{total_tonnage_per_hour_new - total_tonnage_per_hour_old:.0f}", 
            f"{total_m3_per_day_new - total_m3_per_day_old:.0f}", 
            f"{total_tonnage_per_day_new - total_tonnage_per_day_old:.0f}", 
            f"{total_trucks_per_day_new - total_trucks_per_day_old:.0f}", '', 
            '', '100', f"{1.1 * total_tonnage_per_hour_new - total_tonnage_per_hour_old:.0f}", 
            f"{1.1 * total_m3_per_day_new - total_m3_per_day_old:.0f}", 
            f"{1.1 * total_tonnage_per_day_new - total_tonnage_per_day_old:.0f}", 
            f"{1.1 * total_trucks_per_day_new - total_trucks_per_day_old:.0f}"
        ],
        '% Difference': [
            '', f"{(new_payload - old_payload) / old_payload * 100:.0f}%", '-', f"{(new_payload - old_payload) / old_payload * 100:.0f}%", 
            f"{(new_total_load - old_total_load) / old_total_load * 100:.0f}%", '', 
            '', '-', f"{(swings_to_fill_truck_new - swings_to_fill_truck_old) / swings_to_fill_truck_old * 100:.0f}%", 
            f"{(time_to_fill_truck_new - time_to_fill_truck_old) / time_to_fill_truck_old * 100:.0f}%", 
            f"{(avg_trucks_per_hour_new - avg_trucks_per_hour_old) / avg_trucks_per_hour_old * 100:.0f}%",
            f"{(swings_per_hour_new - swings_per_hour_old) / swings_per_hour_old * 100:.0f}%", 
            f"{(truck_tonnage_per_hour_new - truck_tonnage_per_hour_old) / truck_tonnage_per_hour_old * 100:.0f}%", 
            '', 
            '','-', f"{(total_tonnage_per_hour_new - total_tonnage_per_hour_old) / total_tonnage_per_hour_old * 100:.0f}%", 
            f"{(total_m3_per_day_new - total_m3_per_day_old) / total_m3_per_day_old * 100:.0f}%", 
            f"{(total_tonnage_per_day_new - total_tonnage_per_day_old) / total_tonnage_per_day_old * 100:.0f}%", 
            f"{(total_trucks_per_day_new - total_trucks_per_day_old) / total_trucks_per_day_old * 100:.0f}%", '', 
            '','10%', f"{(1.1 * total_tonnage_per_hour_new - total_tonnage_per_hour_old) / total_tonnage_per_hour_old * 100:.0f}%", 
            f"{(1.1 * total_m3_per_day_new - total_m3_per_day_old) / total_m3_per_day_old * 100:.0f}%", 
            f"{(1.1 * total_tonnage_per_day_new - total_tonnage_per_day_old) / total_tonnage_per_day_old * 100:.0f}%", 
            f"{(1.1 * total_trucks_per_day_new - total_trucks_per_day_old) / total_trucks_per_day_old * 100:.0f}%"
        ]
    }
        comparison_df = pd.DataFrame(data)
        return comparison_df

# Run calculations only when the button is pressed
# Find matching SWL and optimal bucket
if calculate_button:
    swl = find_matching_swl(user_data)
    if swl:
        # Load selected bucket data
        selected_bucket_csv = bhc_bucket_csv if select_bhc else bucket_csv
        bucket_data = load_bucket_data(selected_bucket_csv)
        
        optimal_bucket = select_optimal_bucket(user_data, bucket_data, swl)
        
        if optimal_bucket:
            comparison_df = generate_comparison_df(user_data, optimal_bucket, swl)

            st.success(f"Good news! ONTRAC could improve your productivity by up to {st.session_state.productivity}!")
            st.markdown(f'<p class="custom-font">Your ONTRAC Bucket Solution is the: XMOR® {optimal_bucket["bucket_name"]} ({optimal_bucket["bucket_size"]} m³)</p>',unsafe_allow_html=True) 
            st.success(f"Bucket Payload Increase: +{st.session_state.volume_increase} m³ (+{st.session_state.volume_increase_percentage})")
            st.write(f"Matching Excavator Successfully Found.")
            st.write(f"Your Matching Excavator Safe Working Load at {user_data["reach"]}m reach: {swl} kg")
            st.write(f"Your XMOR® Bucket Total Suspended Load: {optimal_bucket['total_bucket_weight']} kg")
            
            # Display the DataFrame in Streamlit
        else:
            st.write("No suitable bucket found within SWL limits.")
    else:
        st.write("No matching excavator configuration found!")

# Email input
st.write(" ")
st.write(" ")
st.markdown(f'<p class="custom-font">Would you like a side-by-side comparison sent to your email?</p>',unsafe_allow_html=True) 
email = st.text_input("Email Address:")

if st.button("Yes Please!"):
    swl = find_matching_swl(user_data)
    # Generate the comparison DataFrame and CSV data in advance
    selected_bucket_csv = bhc_bucket_csv if select_bhc else bucket_csv
    bucket_data = load_bucket_data(selected_bucket_csv)
    optimal_bucket = select_optimal_bucket(user_data, bucket_data, swl)
    
    comparison_df = generate_comparison_df(user_data, optimal_bucket, swl)
    csv_data = io.StringIO()
    comparison_df.to_csv(csv_data, index=False)
    csv_data.seek(0)  # Reset the pointer to the start of the file-like object
    
    if email and '@' in email:  # Check if email is valid
        send_email_with_csv(email, csv_data)
        st.success("Please check your inbox!")
        # Display the DataFrame in Streamlit        
        # st.write(comparison_df)
    else:
        st.warning("Please enter a valid email address to send the results.")


# Run the Streamlit app
if __name__ == '__main__':
    app()
