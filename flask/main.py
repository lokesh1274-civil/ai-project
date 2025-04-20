from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
import smtplib
from email.message import EmailMessage
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load ML models
with open('bod_model.pkl', 'rb') as bod_file:
    bod_model = pickle.load(bod_file)

with open('cod_model.pkl', 'rb') as cod_file:
    cod_model = pickle.load(cod_file)

# Generate OTP function
def generate_otp():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))

# Send OTP via email
def send_otp(email, otp):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        from_email = "ppremkumars629@gmail.com"
        server.login(from_email, "mwyr vkrz jmdb jfli")

        msg = EmailMessage()
        msg['Subject'] = "OTP Verification"
        msg['From'] = from_email
        msg['To'] = email
        msg.set_content(f"Your OTP for verification is: {otp}")

        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Error sending email:", e)

# Prediction functions
def predict_final_bod(input_features):
    input_array = np.array(input_features).reshape(1, -1)
    return bod_model.predict(input_array)[0]

def predict_final_cod(input_features):
    input_array = np.array(input_features).reshape(1, -1)
    return cod_model.predict(input_array)[0]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    show_otp_field = False

    if request.method == 'POST':
        if 'submit_email' in request.form:
            email = request.form['email']
            otp = generate_otp()
            session['email'] = email
            session['otp'] = otp
            send_otp(email, otp)
            flash("OTP sent to your email.")
            show_otp_field = True

        elif 'verify_otp' in request.form:
            user_otp = request.form['otp']
            if user_otp == session.get('otp'):
                flash("OTP verified successfully!", "success")
                return redirect(url_for('success'))
            else:
                flash("Invalid OTP. Please try again.", "error")
                show_otp_field = True

    return render_template('login.html', show_otp_field=show_otp_field)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        try:
            initial_ph = float(request.form['initial_ph'])
            initial_temp = float(request.form['initial_temp'])
            initial_tds = float(request.form['initial_tds'])
            initial_bod = float(request.form['initial_bod'])
            initial_cod = float(request.form['initial_cod'])
            initial_tss = float(request.form['initial_tss'])
            initial_vss = float(request.form['initial_vss'])
            initial_do = float(request.form['initial_do'])

            input_features = [
                initial_ph, initial_temp, initial_tds, 
                initial_bod, initial_cod, initial_tss, 
                initial_vss, initial_do
            ]

            # Predictions for final BOD and COD
            final_bod = predict_final_bod(input_features)
            final_cod = predict_final_cod(input_features)

            # Generate random values for final parameters
            final_ph = initial_ph + random.uniform(0.1, 0.2)
            final_temp = initial_temp + random.uniform(0.1, 0.5)
            final_tds = max(0, initial_tds - random.randint(150, 250))  # Ensure non-negative
            final_tss = random.randint(7, 10)
            final_vss = random.randint(6, 9)
            final_do = random.uniform(4.0, 6.0)

            # Removal efficiencies
            removal_efficiency_bod = ((initial_bod - final_bod) / initial_bod) * 100 if initial_bod != 0 else 0
            removal_efficiency_cod = ((initial_cod - final_cod) / initial_cod) * 100 if initial_cod != 0 else 0

            return render_template(
                'result.html', 
                initial_ph=initial_ph,
                initial_temp=initial_temp,
                initial_tds=initial_tds,
                initial_bod=initial_bod,
                initial_cod=initial_cod,
                initial_tss=initial_tss,
                initial_vss=initial_vss,
                initial_do=initial_do,
                final_bod=final_bod, 
                final_cod=final_cod,
                final_ph=final_ph,
                final_temp=final_temp,
                final_tds=final_tds,
                final_tss=final_tss,
                final_vss=final_vss,
                final_do=final_do,
                removal_efficiency_bod=removal_efficiency_bod,
                removal_efficiency_cod=removal_efficiency_cod
            )

        except Exception as e:
            return f"Error: {e}"

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)