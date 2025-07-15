import requests
import xmlrpc.client

class NewsSiteClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
    
    def authenticate(self, username, password):
        soap_url = f"{self.base_url}/api/soap/"
        server = xmlrpc.client.ServerProxy(soap_url)
        try:
            result = server.authenticate_user(username, password)
            if 'token' in result:
                self.token = result['token']
                return True
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def list_users(self):
        if not self.token:
            print("Not authenticated")
            return None
        
        soap_url = f"{self.base_url}/api/soap/"
        server = xmlrpc.client.ServerProxy(soap_url)
        try:
            result = server.list_users(self.token)
            if 'users' in result:
                return result['users']
            print(f"Error: {result.get('error', 'Unknown error')}")
            return None
        except Exception as e:
            print(f"Error listing users: {e}")
            return None
    
    def create_user(self, user_data):
        if not self.token:
            print("Not authenticated")
            return None
        
        soap_url = f"{self.base_url}/api/soap/"
        server = xmlrpc.client.ServerProxy(soap_url)
        try:
            result = server.create_user(self.token, user_data)
            if 'success' in result and result['success']:
                return result['user']
            print(f"Error: {result.get('error', 'Unknown error')}")
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_articles(self, format='json'):
        url = f"{self.base_url}/api/articles/?format={format}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json() if format == 'json' else response.text
            print(f"Error: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error getting articles: {e}")
            return None

if __name__ == "__main__":
    client = NewsSiteClient("http://localhost:8000")
    if client.authenticate("admin", "password"):
        print("Authenticated successfully")
        users = client.list_users()
        print("Users:", users)
        
        articles = client.get_articles()
        print("Articles:", articles)
    else:
        print("Authentication failed")