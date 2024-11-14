import jwt
import pymongo
from bson import ObjectId

# JWT and MongoDB Configuration
DB_URI = "mongodb+srv://doadmin:kZ43I56U9m8XC70G@dbaas-db-7264100-23ad3afa.mongo.ondigitalocean.com/admin?authSource=admin&replicaSet=dbaas-db-7264100&tls=true"
JWT_SECRET = "yE!mn8VJds7G!sRwz%^98Tqu2eWQaf5"

# MongoDB Setup
client = pymongo.MongoClient(DB_URI)
db = client['admin']
users_collection = db['users']

# Function to verify user token and return user ID
def verify_user_token(token):
    try:
        # Decode the token to extract user information
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token.get('id')
        if user_id and users_collection.find_one({"_id": ObjectId(user_id)}):
            return user_id
        else:
            return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

# Function to get token details from the client socket
def get_token_details(client_socket, client_address):
    try:
        # Receive the token from the client
        token_message = client_socket.recv(1024).decode().strip()
        if not token_message.startswith("Authorization: Bearer "):
            print(f"Connection refused: Invalid token format from {client_address}")
            client_socket.close()
            return None
        token = token_message.split(" ")[2]
        # Verify the token
        user_id = verify_user_token(token)
        if not user_id:
            print(f"Connection refused: Unauthorized user {client_address}")
            client_socket.close()
            return None
        return user_id
    except Exception as e:
        print(f"Connection refused: Error receiving token from {client_address}. Error: {e}")
        client_socket.close()
        return None
