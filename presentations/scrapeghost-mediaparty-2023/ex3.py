import requests
import openai

def get_details(url):
    response = requests.get(url)

    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "When provided with HTML, return the equivalent JSON in the format {'name': '', 'position': '', 'hired': 'm d, Y'}"},
                {"role": "user", "content": response.text}
            ]
    )
    return resp.choices[0]

resp = get_details("https://scrapple.fly.dev/staff/3")
print(resp.message.content)