# llamaverify/client.py
from huggingface_hub import InferenceClient 
import requests
from typing import List

class Client:
    def __init__(self,llamaverify_api_key=None):
        self.api_key_frontend=llamaverify_api_key
        return

    def callDehallucinateEndpoint(self, sources: List[str] =None , summary: str = None):

              # Define the endpoint URL
      url = 'http://127.0.0.1:5000//dehallucinate'  # ?api_key=' + self.api_key_frontend

      if summary:
          url=url+"&summary="+ summary
      if sources:
          url=url+ "&sources=" + str(sources)

      try:
          headers = {
              'Authorization': self.api_key_frontend
          }

          response = requests.post(url, headers=headers)
          # # Send the GET request
          # response = requests.get(url)
          
          # Check if the request was successful
          if response.status_code == 200:
              # Get the response text
              data = response.text
            #   print("Data received:", data)
                 # Extract the old_score, new_score, and new_summary from the response
              old_score = float (data.split("Old Score:")[1].split("\n")[0].strip())
              new_score = float (data.split("New Score:")[1].split("\n")[0].strip())
              new_summary = data.split("Corrected Summary:")[1].strip()
              if (  not new_score is None ) or (not old_score is None) or (not new_summary is None)  :
                   return [old_score,new_score], new_summary
              else:
                   raise ValueError(f"Received Null response from endpoint try again")
          else:
                    # Parse the JSON response
              error_message = response.json().get('error', 'Unknown error occurred')
              if response.status_code == 401:
                 raise ValueError(f" {error_message} (Status Code: {response.status_code})")

      except requests.exceptions.RequestException as e:
          raise requests.exceptions.RequestException(f"Request failed: {e}")


    def generate_api_token( user_id):
        """
        Calls the generate_token endpoint to create a new API token for the given user.

        Parameters:
            base_url (str): The base URL of the Flask app.
            user_id (str): The ID of the user for whom to generate the API token.

        Returns:
            dict: A dictionary containing the API token and any additional response data.
        """
        url = f"http://127.0.0.1:5000/generate_token"
        headers = {'Content-Type': 'application/json'}
        data = {'user_id': user_id}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
            return response.json()  # Returns the JSON response as a dictionary
        except requests.exceptions.RequestException as e:
            print(f"Error calling generate_token endpoint: {e}")
            return None

if __name__ == '__main__':
    ClientInstance=Client(llamaverify_api_key='5b7fdbfa5f9850e19a888f455c3ff5cef8a9576d7d710cf1e0d8b20ae34f9db2')
    
    # token_response = Client.generate_api_token( "dummy_user_1")
    # if token_response:
    #     print("API Token:", token_response.get('api_token'))
    # else:
    #     print("Failed to generate API token.")


    scores, newSummary = ClientInstance.callDehallucinateEndpoint()
    print("Scores :    " + str(scores))
    print("New Summary :    "  + newSummary)