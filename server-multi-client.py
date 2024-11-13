import socket
import threading
import base64
import os
from concurrent.futures import ThreadPoolExecutor

# Thread pool to handle multiple clients efficiently
executor = ThreadPoolExecutor(max_workers=10)

# Function to handle receiving image data (Server side)
def receive_image(sock, client_address):
    # For sending message to client
    # send_thread = threading.Thread(target=send_messages, args=(sock, client_address))
    # send_thread.daemon = True
    # send_thread.start()

    client_ip = client_address[0]
    images_dir = os.path.join("images", client_ip)
    if not os.path.exists(images_dir):  # Create directory for saving images if it does not exist
        os.makedirs(images_dir)
    
    image_count = 0  # Initialize counter for number of images received
    buffer = ""  # Buffer to accumulate image data
    while True:
        try:
            # Receive data in larger chunks to capture entire images
            # sock.settimeout(30.0)  # Set a timeout for receiving data to prevent blocking indefinitely
            message = sock.recv(4096).decode()
            if message:
                buffer += message
                # Use a delimiter to determine end of an image
                while "<END_OF_IMAGE>" in buffer:
                    img_str, buffer = buffer.split("<END_OF_IMAGE>", 1)
                    try:
                        # Convert the received base64 encoded string back to binary image data
                        image_data = base64.b64decode(img_str)
                        image_filename = f"{images_dir}/received_image_{image_count}.jpg"
                        # Save the image to the respective client's directory
                        with open(image_filename, "wb") as img_file:
                            img_file.write(image_data)
                        print(f"Image saved: {image_filename}")
                        # Send the image path back to the client
                        sock.send(f"Image saved at: {image_filename}".encode())
                        image_count += 1
                        print(f"Number of images received from {client_ip}: {image_count}")
                    except base64.binascii.Error:
                        # If decoding fails, continue accumulating
                        print("Decoding error. Continuing to next image.")
                        continue
            else:
                break
        except Exception as e:
            # If any exception occurs, close the connection
            print(f"Connection closed with {client_ip}. Error: {e}")
            sock.close()
            break

# Function to handle sending text messages (Server side)
def send_messages(sock, client_address):
    while True:
        try:
            message = input(f"Server to {client_address[0]}: ")
            sock.send(message.encode())
            sock.send("Check From Send Message".encode())
        except Exception as e:
            print(f"Error sending message to {client_address[0]}: {e}")
            sock.close()
            break

# Function to handle a client connection
def handle_client(client_socket, client_address):
    print(f"Client connected from {client_address}")
    # Handle receiving and sending in separate threads using executor
    receive_thread = threading.Thread(target=receive_image, args=(client_socket, client_address))
    receive_thread.daemon = True
    receive_thread.start()


# Function to act as a server supporting multiple clients
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen(5)
    print(f"Server listening on port {port}...")
    
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            # Start a new thread for each client connection
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
        except Exception as e:
            print(f"Error accepting connections: {e}")

# Main function to start the server
if __name__ == "__main__":
    port = 12343
    start_server(port)
