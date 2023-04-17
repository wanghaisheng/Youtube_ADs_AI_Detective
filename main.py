from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import openai
from PyQt5.QtGui import QIcon

openai.api_key = ""  # OPENAI KEY
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

video_id = ""


class ApiKeyDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("API Key")
        self.setGeometry(100, 100, 800, 600)
        # Create widgets
        self.label = QLabel("<font color='blue'>Please enter your API key:")
        self.api_key_edit = QLineEdit()
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)  # Connect the OK button to the accept() slot

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.api_key_edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def get_api_key(self):
        openai.api_key = self.api_key_edit.text()
        return self.api_key_edit.text()


class video_id_extract(QDialog):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Video URL")
        self.setGeometry(100, 100, 800, 600)
        # Create widgets
        self.label = QLabel("<font color='blue'>Please enter URL:")
        self.videourl_edit = QLineEdit()
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.videourl_edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

        def get_id(url):
            video_url = self.videourl_edit.toPlainText()
            video_id = None
            if 'watch?v=' in video_url:
                video_id = video_url.split('watch?v=')[1]
            elif 'v=' in video_url:
                video_id = video_url.split('v=')[1]
            else:
                QMessageBox.warning(self, "Error", "Invalid YouTube Video URL")
                return video_id


def convert_seconds_to_minutes(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"


def document_chatbot(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are "},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message["content"]


def summarize(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the provided text"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message["content"]


def generate_ads_response(text):
    b = ""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "I will provide you a youtube video transcript and minutes and you are going to say if there is the content of an ad and in what minutes and their durations"},
            {"role": "user", "content": text}
        ]
    )
    messes = response.choices[0].message["content"]
    if messes[:3] == "Yes" or messes[:11] == "There is an":
        b = messes
    return b


MAX_TOKENS = 4096


def split_input_text(text, max_tokens):
    chunks = []
    current_chunk = ''
    for word in text.split():
        if len(current_chunk) + len(word) < max_tokens:
            current_chunk += word + ' '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + ' '
    chunks.append(current_chunk.strip())
    return chunks


response_list = []


class YoutubeTranscriptApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YouTube AI Detector")
        self.setGeometry(100, 100, 800, 600)
        icon = QIcon('C:/Users/murat/OneDrive/Masaüstü/YOUTUBE_AI/images/icon.png')
        self.setWindowIcon(icon)

        self.label = QLabel("<font color='blue'>Enter YouTube Video URL:")
        self.text_edit = QTextEdit()
        self.button = QPushButton("Start the ads detector")
        self.button.clicked.connect(self.get_transcript)
        self.transcript_button = QPushButton("See Transcript")
        self.transcript_button.clicked.connect(self.see_transcript)
        self.summary_button = QPushButton("Summarize the video")
        self.summary_button.clicked.connect(self.summarize)
        self.api_key_label = QLabel("<font color='blue'>Enter OpenAI API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_button = QPushButton("Set API Key")
        self.api_key_button.clicked.connect(self.set_api_key)
        self.videourl_label = QLabel("<font color='blue'>Video URL")
        self.videourl_edit = QLineEdit()
        self.videourl_button = QPushButton("Set Video URL")
        self.videourl_button.clicked.connect(self.set_video_id)
        self.clear_button = QPushButton("Clear Text")
        self.clear_button.clicked.connect(self.clear_text)

        self.clear_button.setStyleSheet('background-color: white; color: red')

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_edit)
        layout.addWidget(self.api_key_button)
        layout.addWidget(self.videourl_label)
        layout.addWidget(self.videourl_edit)
        layout.addWidget(self.videourl_button)
        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.transcript_button)
        layout.addWidget(self.button)
        layout.addWidget(self.summary_button)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def set_video_id(self):
        # Set the OpenAI API key from the input field
        video_url = self.videourl_edit.text().strip()

        video_id = None
        if 'watch?v=' in video_url:
            video_id = video_url.split('watch?v=')[1]
            QMessageBox.information(self, "URL Set", f"URL has been set:{video_url}\nYou can change it manually")
        elif 'v=' in video_url:
            video_id = video_url.split('v=')[1]


        else:
            QMessageBox.warning(self, "Error", "Invalid YouTube Video URL")
        return video_id

    def set_api_key(self):
        # Set the OpenAI API key from the input field
        api_key = self.api_key_edit.text().strip()
        if api_key:
            openai.api_key = api_key
            QMessageBox.information(self, "API Key Set", "OpenAI API key has been set.")
        else:
            QMessageBox.warning(self, "Error",
                                "Please enter a valid API key.\nVisit https://platform.openai.com/account/api-keys for API keys ")

    def clear_text(self):
        self.text_edit.clear()

    def see_transcript(self):
        # Show the transcript in a message box
        video_id = self.set_video_id()

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en', 'tr', 'de'])
            transcript = transcript.fetch()
            text_list = []
            time_list = []
            start_time = []

            for i in range(len(transcript)):
                start = transcript[i]['duration']
                time_list.append(start)

                time = transcript[i]['text']
                text_list.append(time)

                start = transcript[i]['start']
                start_time.append(start)

            start_time_minutes = [convert_seconds_to_minutes(start) for start in start_time]

            df = pd.DataFrame(data={"Text": text_list, "StartTime": start_time_minutes, "Duration": time_list})
            data_str = "\n".join([f"{text} - {start_time}" for text, start_time in zip(text_list, start_time_minutes)])
            self.text_edit.setPlainText(data_str)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch transcript: {str(e)}")

    def get_transcript(self):
        video_id = self.set_video_id()

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en', 'tr', 'de'])
            transcript = transcript.fetch()
            text_list = []
            time_list = []
            start_time = []

            for i in range(len(transcript)):
                start = transcript[i]['duration']
                time_list.append(start)

                time = transcript[i]['text']
                text_list.append(time)

                start = transcript[i]['start']
                start_time.append(start)

            start_time_minutes = [convert_seconds_to_minutes(start) for start in start_time]

            df = pd.DataFrame(data={"Text": text_list, "StartTime": start_time_minutes, "Duration": time_list})
            print(df)
            data_dict = {"Text": text_list, "StartTime": start_time_minutes, "Duration": time_list}

            data_str = "\n".join([f"{text} - {start_time}" for text, start_time in zip(text_list, start_time_minutes)])
            prompt = f"Is there any ads in the following transcript:\n{data_str}\n\n If you find any ad content start the sentence always with 'yes' give me brief answers :"

            # Generate response using GPT-3
            input_text = "This is the video: " + data_str
            input_chunks = split_input_text(data_str, MAX_TOKENS)
            response = "\n"
            for chunk in input_chunks:
                response += "\n" + generate_ads_response(chunk)

            self.text_edit.setPlainText(response)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch transcript: {str(e)}")

    def summarize(self):
        # Show the transcript in a message box
        video_id = self.set_video_id()

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en', 'tr', 'de'])
            transcript = transcript.fetch()
            text_list = []
            time_list = []
            start_time = []

            for i in range(len(transcript)):
                start = transcript[i]['duration']
                time_list.append(start)

                time = transcript[i]['text']
                text_list.append(time)

                start = transcript[i]['start']
                start_time.append(start)

            start_time_minutes = [convert_seconds_to_minutes(start) for start in start_time]

            df = pd.DataFrame(data={"Text": text_list, "StartTime": start_time_minutes, "Duration": time_list})
            data_str = "\n".join([f"{text} - {start_time}" for text, start_time in zip(text_list, start_time_minutes)])
            input_text = data_str
            input_chunks = split_input_text(data_str, MAX_TOKENS)
            response = "\n"
            for chunk in input_chunks:
                response += "\n" + summarize(chunk)

            self.text_edit.setPlainText(response)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch transcript: {str(e)}")


if __name__ == "__main__":
    app = QApplication([])
    window = YoutubeTranscriptApp()
    window.show()
    app.exec_()

