Two Host Podcast Creation from Generic Content

Getting started
This is a streamlit app with a single Python3 file (listVoices.py).
Ensure you have the latest streamlit on the runtime laptop/Cloudtop. https://docs.streamlit.io/get-started/installation
REQUIRED STEPS

Open for editing the listVoices.py file
Change the PROJECT_ID to match yours.
In your PROJECT_ID, create an API Key for Gemini and create a secret entry in Google Secret Manager to store the API Key.
Change the secret name in the listVoice.py to correspond to your own Google secret that corresponds to your Google Gemini API Key (from step 3).

OPTIONAL

If you would like to change the names of the voices (by gender), edit the Python file function assign_voice_names as needed.

Save the file on your own runtime (laptop/Cloudtop instance). Ensure you have all Python libraries installed.

To run the app
python3 -m streamlit run /path/to/your/file/listVoices.py

OR
streamlit run /path/to/your/file/listVoices.py
