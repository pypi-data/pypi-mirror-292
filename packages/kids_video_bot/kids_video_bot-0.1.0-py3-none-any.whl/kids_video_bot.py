import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget

class KidsVideoBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kids Video Builder Bot")
        self.setGeometry(100, 100, 600, 400)

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create and add chat history display
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        # Create and add input field
        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        # Create and add send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.on_send)
        layout.addWidget(self.send_button)

        # Set central widget
        self.setCentralWidget(central_widget)

    def on_send(self):
        user_input = self.input_field.text()
        self.chat_history.append(f"You: {user_input}")
        self.input_field.clear()
        
        # Here you would process the user input and generate a response
        # For now, we'll just echo the input
        bot_response = f"Bot: I received your message: {user_input}"
        self.chat_history.append(bot_response)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KidsVideoBot()
    window.show()
    sys.exit(app.exec())
