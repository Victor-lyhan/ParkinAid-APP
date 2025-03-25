import os

from flask import Flask, request, render_template, jsonify

from body_motion import predict_motion

app = Flask(__name__, template_folder='static/templates', static_folder='static')


@app.route('/')
def instruction():
    return render_template('instruction.html')

@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# Set upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/analyze_video/<video_type>", methods=["POST"])
def analyze_video(video_type):
    if "video" not in request.files:
        return jsonify({"message": {"Error": "No file uploaded"}}), 400

    video_file = request.files["video"]
    analysis_type = request.form.get("analysis_type", "Unknown")

    if video_file.filename == "":
        return jsonify({"message": {"Error": "No selected file"}}), 400

    # Save the uploaded file
    video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_file.filename)
    video_file.save(video_path)

    if video_type == "videoUploadBodyMotionAnalysis":

        # Simulate analysis (Replace this with actual video processing logic)
        # analysis_result = {
        #     "Dyskinesia Score": "3.21",
        #     "FoG Ratio": "16.00",
        #     "MiniBestTest Score": "20.23",
        #     "PIGD Score": "7.09",
        #     "TUG dual-task time": "18.12",
        #     "TUG time": "16.30",
        #     "UPDRS-II": "9.56",
        #     "UPDRS-III": "34.34"
        # }
        analysis_result = predict_motion(video_path)
    else:
        # Simulate analysis (Replace this with actual video processing logic)
        analysis_result = f"Video uploaded successfully for {analysis_type} analysis."
        analysis_result = {"Response": analysis_result}


    return jsonify({"message": analysis_result})


@app.route("/analyze_audio/<audio_type>", methods=["POST"])
def analyze_audio(audio_type):
    if "audio" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    audio_file = request.files["audio"]
    print(audio_type)
    analysis_type = request.form.get("analysis_type", "Unknown")

    if audio_file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    # Save the uploaded file
    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_file.filename)
    audio_file.save(audio_path)

    # Simulate analysis (Replace this with actual audio processing logic)
    analysis_result = f"Audio uploaded successfully for {analysis_type} analysis."
    os.remove(audio_path)

    return jsonify({"message": analysis_result, "audio_path": audio_path})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
