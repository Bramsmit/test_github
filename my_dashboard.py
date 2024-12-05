import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set the title of the app
st.title('Simple Streamlit Dashboard')

# Add a sidebar for user input
st.sidebar.header('User Input Parameters')

# Function to generate random data based on user inputs
def generate_data(num_points, data_range):
    np.random.seed(42)
    data = np.random.randint(0, data_range, num_points)
    return pd.DataFrame({'Data': data})

# User inputs for number of points and data range
num_points = st.sidebar.slider('Number of points', min_value=10, max_value=500, value=100, step=10)
data_range = st.sidebar.slider('Data range (0 to X)', min_value=10, max_value=500, value=100, step=10)

# Generate random data based on user inputs
data = generate_data(num_points, data_range)

# Show a table with the generated data
st.write('Generated Data:', data)

# Plot the histogram of the generated data
fig, ax = plt.subplots()
ax.hist(data['Data'], bins=15, color='skyblue', edgecolor='black')
ax.set_xlabel('Value')
ax.set_ylabel('Frequency')
ax.set_title('Histogram of Generated Data')
st.pyplot(fig)

# Add a button to download the data as CSV
st.download_button(
    label='Download Data as CSV',
    data=data.to_csv(index=False),
    file_name='generated_data.csv',
    mime='text/csv'
)

# Add an area for user comments
user_comments = st.text_area("User Comments", "Enter your thoughts here...")
if user_comments:
    st.write("Thank you for your input!")
