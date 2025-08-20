⚖️ Prudentia: A Modern Legal Companion App
Prudentia is an AI-powered legal assistant designed to help individuals in India understand their legal rights and navigate the legal system for self-representation (as a Party-in-Person). The app leverages Large Language Models (LLMs) to provide practical guidance, analyze legal issues, and even draft formal petitions for common legal matters.

Key Features
Dynamic Legal Guidance: Users receive step-by-step, actionable advice for specific case types like Consumer Complaints, Property Disputes, and Family Matters.

Petition Drafting: The app can generate a complete, editable draft of a formal petition based on user-provided details.

Jurisdiction & Location Map: An interactive map helps users find nearby courts and key legal contact points.

Secure API Integration: Utilizes OpenRouter.ai to access powerful LLMs while keeping API keys secure.

Multi-lingual Support: The petition drafting feature supports multiple Indian languages (English, Hindi, Tamil, Telugu, Kannada, Malayalam).

Project Setup (For Developers)
Follow these steps to get the project up and running on your local machine.

1. Clone the repository
git clone https://github.com/your-username/prudentia.git
cd prudentia

2. Create a virtual environment
It's a best practice to use a virtual environment to manage dependencies.

# For Python 3
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install dependencies
Install all the required Python libraries using the requirements.txt file.

pip install -r requirements.txt

4. Configure API Keys
This app uses the OpenRouter API for LLM calls. You need to obtain an API key and store it securely.

Create a folder named .streamlit in the root of your project.

Inside the .streamlit folder, create a new file named secrets.toml.

Add your API key to this file in the following format:

OPENROUTER_API_KEY = "your_api_key_here"

Note: NEVER commit your secrets.toml file to your public Git repository. It contains sensitive information.

5. Run the app
Once everything is set up, you can run the Streamlit application from your terminal.

streamlit run app.py

The app should automatically open in your web browser.

Deployment
The easiest way to deploy this app is by using Streamlit Community Cloud.

Push all your code (except for secrets.toml) to a GitHub repository.

Go to Streamlit Community Cloud and log in.

Click "New App" and connect to your GitHub repository.

Specify the branch and the path to your app.py file.

In the "Advanced settings", add your OPENROUTER_API_KEY as an environment variable or secrets in the UI.

The platform will automatically build and deploy your app.

Project Structure
prudentia/
├── .streamlit/
│   └── secrets.toml        # Securely store API keys (not committed to Git)
├── app.py                  # Main Streamlit application file
├── requirements.txt        # Python dependencies
├── img.png                 # Image of the founder
├── logo.png                # App logo
└── upi.png                 # UPI QR code for contributions

How to Contribute
We welcome contributions! Whether you're a developer, a legal professional, or simply a user with feedback, you can help us improve.

Code Contributions: Fork this repository, create a new branch, and submit a pull request with your changes.

Feedback: Use the feedback buttons within the app to let us know what's working and what isn't.

Support: If you find this tool valuable, consider supporting the project by using the "Contribute" button in the app's header.

Models Used
This application uses the following models from OpenRouter.ai:

Legal Guidance: openai/gpt-oss-20b:free

Petition Drafting: google/gemma-3n-e4b-it:free

Credits
Founder: Santhosh

Framework: Streamlit

API: OpenRouter.ai

Mapping: Folium & Streamlit-Folium
