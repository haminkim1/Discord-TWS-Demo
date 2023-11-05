from auth.discord.token import token

# Create a token.py file under auth.discord and enter:
# token = "YOUR_TOKEN"
access_token = token
headers = {
    'authorization': f"{access_token}"
}

        

    



