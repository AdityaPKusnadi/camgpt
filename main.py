import tkinter as tk
import speech_recognition as sr
import threading
import time
import openai
import cv2
from PIL import Image, ImageTk

# Set up OpenAI API credentials
openai.api_key = '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'

# Create a global variable for storing conversation history
conversation_history = []

# Define the main application window
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech-to-Text Chat App")

        # Create a frame for video display
        self.video_frame = tk.Frame(self, width=640, height=480)
        self.video_frame.grid(row=0, column=0, padx=10, pady=10)

        # Create a canvas to display video frames
        self.video_canvas = tk.Canvas(self.video_frame, width=640, height=480)
        self.video_canvas.pack()

         # Start the camera feed
        self.is_camera_running = False
        self.camera_thread = threading.Thread(target=self.camera_feed)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        # Create a frame for conversation history
        self.conversation_frame = tk.Frame(self, width=400, height=480)
        self.conversation_frame.grid(row=0, column=1, padx=10, pady=10)

        # Create a label to display conversation history
        self.conversation_label = tk.Label(self.conversation_frame, text="Conversation History")
        self.conversation_label.pack()

        # Create a text widget to display conversation history
        self.conversation_text = tk.Text(self.conversation_frame, width=40, height=10)
        self.conversation_text.pack()

        # Create a frame for recording controls
        self.controls_frame = tk.Frame(self, width=400, height=100)
        self.controls_frame.grid(row=1, column=1, padx=10, pady=10)

        # Create a label for the current question
        self.question_label = tk.Label(self.controls_frame, text="Question:")
        self.question_label.pack()

        # Create a text widget for the current question
        self.question_text = tk.Text(self.controls_frame, width=40, height=2)
        self.question_text.pack()

        # Create a button to ask the question
        self.ask_button = tk.Button(self.controls_frame, text="Ask", command=self.ask_question, state=tk.DISABLED)
        self.ask_button.pack()

        # Create a button to start recording
        self.start_button = tk.Button(self.controls_frame, text="Start Recording", command=self.start_recording)
        self.start_button.pack()

        # Create a button to stop recording
        self.stop_button = tk.Button(self.controls_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack()

        # Start a background thread for continuous recording
        self.is_recording = True
        self.background_thread = threading.Thread(target=self.continuous_recording)
        self.background_thread.daemon = True
        self.background_thread.start()

        # Initialize the camera capture object
        self.cap = cv2.VideoCapture(0)


    def start_recording(self):
        # self.is_recording = True
        self.is_camera_running = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.ask_button.configure(state=tk.DISABLED)

    def stop_recording(self):
        # self.is_recording = False
        self.is_camera_running = False
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.ask_button.configure(state=tk.NORMAL)
    
    def camera_feed(self):
        cap = cv2.VideoCapture(0)

        while True:
            if self.is_camera_running:
                ret, frame = cap.read()
                if ret:
                    # Convert the OpenCV frame to PIL format
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)

                    # Update the canvas with the new frame
                    self.video_canvas.create_image(0, 0, anchor=tk.NW, image=image)
                    self.video_canvas.image = image

            # Sleep for 0.01 seconds to avoid high CPU usage
            time.sleep(0.01)

    def ask_question(self):
        question = self.question_text.get("1.0", tk.END).strip()
        self.question_text.delete("1.0", tk.END)
        self.conversation_text.insert(tk.END, f"\nUser: {question}\n")
        self.conversation_text.see(tk.END)
        conversation_history.append(question)

        # Send the question to ChatGPT and get the response
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt='\n'.join(conversation_history),
            max_tokens=50,
            temperature=0.7,
            n=1,
            stop=None,
            timeout=10
        )

        answer = response.choices[0].text.strip()
        self.conversation_text.insert(tk.END, f"ChatGPT: {answer}\n")
        self.conversation_text.see(tk.END)
        conversation_history.append(answer)

    def continuous_recording(self):
        r = sr.Recognizer()

        while True:
            if self.is_camera_running:
                ret, frame = cap.read()
                if ret:
                    # Convert the OpenCV frame to PIL format
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)

                    # Update the canvas with the new frame
                    self.video_canvas.create_image(0, 0, anchor=tk.NW, image=image)
                    self.video_canvas.image = image

            if self.is_recording:
                # print(sr.Microphone(device_index=3))
                with sr.Microphone(device_index=3) as source:
                    # r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                try:
                    text = r.recognize_google(audio)
                    self.conversation_text.insert(tk.END, f"User: {text}\n")
                    self.conversation_text.see(tk.END)
                    conversation_history.append(text)
                    self.ask_button.configure(state=tk.NORMAL)
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

            # Sleep for 0.1 seconds to avoid high CPU usage
            time.sleep(0.1)

# Create an instance of the application
app = App()

# Start the Tkinter event loop
app.mainloop()
