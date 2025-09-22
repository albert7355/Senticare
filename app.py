from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import csv
from io import StringIO

app = Flask(__name__, static_folder='.')
CORS(app)  # Allow frontend to call API without CORS issues

# --- Sentiment Dictionaries ---
positive_words = {
    "love": 3, "great": 2, "excellent": 3, "happy": 1.5, "amazing": 2.5, "awesome": 2.5,
    "fantastic": 2, "wonderful": 2.5, "helpful": 1.5, "good": 1, "perfect": 3, "superb": 2.5,
    "brilliant": 2, "gorgeous": 2, "charming": 1.5, "delightful": 2, "exciting": 1.5,
    "joyful": 2, "kind": 1, "lovely": 1.5, "magnificent": 2.5, "pleasure": 2, "satisfied": 1.5,
    "success": 2, "terrific": 2, "thrilled": 2, "victory": 3, "well done": 2.5, "impressive": 2,
    "innovative": 2
}
negative_words = {
    "bad": -2, "terrible": -3, "unfair": -2, "poor": -1.5, "sad": -1, "angry": -2,
    "hate": -2.5, "worst": -3, "disappointed": -2.5, "stupid": -2, "useless": -2.5,
    "horrible": -2.5, "awful": -2.5, "disgusting": -3, "dreadful": -2.5, "frustrated": -1.5,
    "insane": -2, "unhappy": -1.5, "lousy": -2, "miserable": -2.5, "painful": -2, "regret": -1.5,
    "shocking": -2.5, "slow": -1, "unprofessional": -2, "unreliable": -2.5, "waste": -2,
    "annoying": -1.5, "unacceptable": -2.5
}
positive_phrases = {
    "very good": 2.5, "well done": 2, "fantastic work": 2.5, "excellent initiative": 3,
    "good job": 2, "could not be better": 3, "highly recommend": 2.5, "five stars": 3,
    "exceeded expectations": 2.5, "worth the money": 2
}
negative_phrases = {
    "not good": -2.5, "no support": -3, "very bad": -3, "really terrible": -3,
    "does not work": -2.5, "waste of time": -3, "never again": -3, "not worth it": -2.5,
    "poor quality": -2
}

def get_sentiment(text):
    """Analyze sentiment score for a given text."""
    text = text.lower().strip()
    score = 0
    found_phrase = False

    # Check negative phrases first
    for phrase, value in negative_phrases.items():
        if phrase in text:
            score = value
            found_phrase = True
            break

    # Check positive phrases if no negative phrase was found
    if not found_phrase:
        for phrase, value in positive_phrases.items():
            if phrase in text:
                score = value
                found_phrase = True
                break

    # If no phrase matched, check word by word
    if not found_phrase:
        for word, value in positive_words.items():
            if word in text:
                score += value
        for word, value in negative_words.items():
            if word in text:
                score += value

    sentiment = "Neutral"
    if score > 0.5:
        sentiment = "Positive"
    elif score < -0.5:
        sentiment = "Negative"

    return {"sentiment": sentiment, "score": score}


@app.route('/')
def serve_frontend():
    """Serve the main frontend file."""
    return send_from_directory('.', 'index.html')


@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment_endpoint():
    """API endpoint to analyze CSV file with comments."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        stream = StringIO(file.stream.read().decode("utf-8"))
        reader = csv.reader(stream)

        results = []
        positive_count, negative_count, neutral_count = 0, 0, 0

        for row in reader:
            comment = " ".join(row).strip()
            if not comment:
                continue

            sentiment_result = get_sentiment(comment)
            sentiment = sentiment_result['sentiment']

            if sentiment == "Positive":
                positive_count += 1
            elif sentiment == "Negative":
                negative_count += 1
            else:
                neutral_count += 1

            results.append({"comment": comment, "sentiment": sentiment})

        return jsonify({
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "comments": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run Flask on localhost:5000
    app.run(debug=True, host='0.0.0.0', port=5000)
    # In production, consider using a WSGI server like Gunicorn
