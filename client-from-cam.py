import socket
import threading
import base64
import cv2
import time

# Function to handle receiving text messages (Client side)
def receive_messages_client(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if message:
                print(f"Server: {message}")
            else:
                break
        except Exception as e:
            # If any exception occurs, close the connection
            print(f"Connection closed. Error: {e}")
            sock.close()
            break

# Function to handle sending UTF-8 encoded images (Client side)
def send_images(sock):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 24)  # Set webcam to 24 frames per second
    while True:
        try:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                break
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            # Convert to base64 and encode in UTF-8
            encoded_image = base64.b64encode(buffer).decode('utf-8')
            # Append a delimiter to indicate the end of the image
            encoded_image += "<END_OF_IMAGE>"
            # Send the entire encoded image with delimiter as a single chunk
            sock.send(encoded_image.encode())
            time.sleep(1/24)  # Send at 24 frames per second
        except Exception as e:
            print(f"Failed to send image: {e}")
            break

    cap.release()

# Function to act as a client
def start_client(target_ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((target_ip, port))
    print(f"Connected to server at {target_ip}:{port}")
    return client_socket

# Main function to start the client
if __name__ == "__main__":
    target_ip = "127.0.0.1"  # Change this to the server's IP address if needed
    port = 12343
    connection = start_client(target_ip, port)
    # Start threads for receiving text messages from server and sending images continuously
    receive_thread = threading.Thread(target=receive_messages_client, args=(connection,))
    send_thread = threading.Thread(target=send_images, args=(connection,))
    receive_thread.start()
    send_thread.start()
    receive_thread.join()
    send_thread.join()
