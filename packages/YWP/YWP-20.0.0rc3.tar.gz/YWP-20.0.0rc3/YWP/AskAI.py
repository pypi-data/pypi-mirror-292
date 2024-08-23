"""Ask AIs"""
class YWPAI:
    """Ask YWP AI"""
    def BetaVersion(query: str = "", Name: str = "", OS: str = "", Country: str = "", Work: str = "", Company: str = ""):
        """
            Ask YWP AI 2.1 Beta Version

            Args:
                query (str, required): This is Message. Defaults to "".
                Name (str, optional): Enter Your Name. Defaults to "".
                OS (str, optional): Enter Your Device OS. Defaults to "".
                Country (str, optional): Enter Your Conutry. Defaults to "".
                Work (str, optional): Enter Where are you work. Defaults to "".
                Company (str, optional): Enter Your Company Name (If Available). Defaults to "".
        """
        if query != "":
            import requests
            import json

            # Set the API endpoint and headers
            url = 'https://api.dify.ai/v1/chat-messages'
            headers = {
                'Authorization': 'Bearer app-5i11K3RobeVhPK2bVec4dQKi',
                'Content-Type': 'application/json'
            }

            # Define the request payload
            data = {
                "inputs": {
                    "Name": Name,
                    "OS": OS,
                    "Country": Country,
                    "Work": Work,
                    "Company": Company
                },
                "query": query,
                "response_mode": "streaming",
                "conversation_id": "",
                "user": "abc-123",
                "files": []
            }

            # Send the POST request
            response = requests.post(url, headers=headers, json=data, stream=True)

            responce_text = ""
            responce_image = []
            
            # Process the response
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    json_line = json.loads(decoded_line[6:])  # Strip "data: " from the beginning

                    # Check if it's an agent message or a message file (image)
                    if json_line['event'] == 'agent_message':
                        responce_text += json_line.get('answer', '')
                    elif json_line['event'] == 'message_file' and json_line.get('type') == 'image':
                        responce_image.append(json_line.get('url', ''))
                        
            return {"responce_text": responce_text, "responce_images": responce_image, "error": ""}
        else:
            return {"error": "Query is Required"}
