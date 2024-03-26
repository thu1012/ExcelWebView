from flask import Flask, request, render_template, redirect, jsonify
import pandas as pd
import os
import json

app = Flask(__name__)
df = None


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            # No file selected
            return redirect(request.url)
        if file:
            global df
            df = pd.read_csv(file)
            columns = df.columns.tolist()
            return render_template('confirm_columns.html', columns=columns, font_sizes=None)
    return render_template('upload.html')


# Directory for saved configurations
CONFIGS_DIR = "saved_configs"


@app.route('/configure', methods=['POST'])
def configure():
    # Ensure the configuration directory exists
    if not os.path.exists(CONFIGS_DIR):
        os.makedirs(CONFIGS_DIR)

    # Retrieve the configuration name from the form
    config_name = request.form.get('configName')
    # Generate the file path
    config_file_path = os.path.join(CONFIGS_DIR, f"{config_name}.json")

    # Retrieve the columns order
    columns_order = json.loads(request.form.get('order'))

    # Collect font sizes for each column
    font_sizes = {}
    for column in columns_order:
        font_size_key = f"fontSize_{column}"
        font_sizes[column] = request.form.get(font_size_key)

    # Construct the configuration data dictionary
    configuration_data = {
        "columns_order": columns_order,
        "font_sizes": font_sizes,
    }

    # Save the configuration data to a JSON file
    with open(config_file_path, 'w') as config_file:
        json.dump(configuration_data, config_file)

    # Optionally, save a copy as 'config.json' in the root or a separate dedicated config directory
    with open('config.json', 'w') as config_file:
        json.dump(configuration_data, config_file)

    # Redirect to a new page or render template with a success message
    return redirect('/success_page')  # Adjust the redirect as needed


@app.route('/upload-config', methods=['POST'])
def upload_config():
    if df is None:
        return redirect('/')
    if 'configFile' not in request.files:
        return redirect(request.url)
    file = request.files['configFile']
    if file.filename == '':
        return redirect(request.url)
    if file:
        # Save the uploaded file temporarily
        config_data = json.load(file)

        # You may want to validate the config_data structure here
        columns = df.columns.tolist()
        if not all(column in columns for column in config_data['columns_order']):
            return jsonify({"error": "Configuration columns do not match Excel columns."}), 400

        # Save the config data as config.json for the application's current use
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file)

        return render_template('confirm_columns.html',
                               columns=config_data['columns_order'], font_sizes=config_data['font_sizes'])


if __name__ == '__main__':
    app.run(debug=True)
