from openai import OpenAI
import time
import requests
import os

class Embed:
    def __init__(self):
        self.client = OpenAI()

    def invoke(self, text):
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
    

class CreaoLLM:
    def __init__(self, bot_name="assistant", bot_content="assistant") -> None:
        self.bot_name = bot_name
        self.bot_content = bot_content
    
    def invoke(self, prompt, schema, component_id="default", pipeline_id="default"):
        """
        Invoke the Creao LLM API
        """
        # The API Gateway endpoint URL
        url = 'https://drk3mkqa6b.execute-api.us-west-2.amazonaws.com/default/minimaxserver'
        api_key= os.environ["CREAO_API_KEY"]
        headers = {"Content-Type":"application/json", "x-api-key":api_key}
        # Payload to be sent to the Lambda function via API Gateway
        payload = {
            "prompt": prompt,
            "schema": schema,
            "bot_name": self.bot_name,
            "bot_content": self.bot_content,
            "component_id": component_id,
            "pipeline_id": pipeline_id
        }
        # Send the request
        response = requests.post(url,headers=headers, json=payload)
        #print("reponse:", response.content)
        try:
            return response.json()
        except Exception as e:
            print(f"CreaoLLM json decode error:{e}, with response:{response.text}")
            return {"reply":""}

class MiniMaxPro:
    def __init__(self, bot_name="assistant", bot_content="assistant"):
        self.bot_name = bot_name
        self.bot_content = bot_content
        group_id = "1820662545770364967" 
        api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJDcmVhbyBBSSIsIlVzZXJOYW1lIjoiQ3JlYW8gQUkiLCJBY2NvdW50IjoiIiwiU3ViamVjdElEIjoiMTgyMDY2MjU0NTc3ODc1MzU3NSIsIlBob25lIjoiMTg2Njc4OTMzOTkiLCJHcm91cElEIjoiMTgyMDY2MjU0NTc3MDM2NDk2NyIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6ImthaUBjcmVhby5haSIsIkNyZWF0ZVRpbWUiOiIyMDI0LTA4LTIwIDAzOjM4OjQ3IiwiaXNzIjoibWluaW1heCJ9.PUSbHFa6t9Po2z8AwbVlJIgWm7-zRL9047AB_RBN8azCQxNzErJE_6wd8u4726xuIS7NZ6768LJW42-etD8i6N7Dza92QsGkAmEg3PHaYAzbOQgQVge0G_OCpJLMnVOCpZi7yOlkPNuu6BDW8-6lOtJoAeNkatxWJqL-vp_O_zyqgUwoz-2DGiY9H7pQI0Z0KGkj832RG05Lg6T-CJZKKVynT4cwnWqVTX4jYidCmsn6vi45MqCrB78o7v1jJtwdCui74iTRY8n23Qxp3Jis6F0cfFY2kIn_OhXBMb2p6QwEOgfxJRzv1zyusf3MTYTg7aqo37Lnda3uWRC34QSGJA"
        url = f"https://api.minimax.chat/v1/text/chatcompletion_pro?GroupId={group_id}"
        headers = {"Content-Type":"application/json", "Authorization":"Bearer " + api_key}
        self.headers = headers
        self.url = url
    def invoke(self, prompt, schema):
        payload = {
            "model": "abab6.5s-chat",
            "tokens_to_generate": 2048,
            "temperature": 0.1,
            "top_p": 0.95,
            "stream": False,
            "reply_constraints": {
                "sender_type": "BOT",
                "sender_name": self.bot_name,
                "glyph": {
                    "type": "json_value",
                    "json_properties": schema
                }
            },
            "sample_messages": [],
            "plugins": [],
            "messages": [
                {
                "sender_type": "USER",
                "sender_name": "用户",
                "text": prompt
                }
            ],
            "bot_setting": [
                {
                "bot_name": self.bot_name,
                "content": self.bot_content
                }
            ]
            }
        i = 0
        status = -1
        while status != 0:
            response = requests.post(self.url, headers=self.headers, json=payload)
            status = response.json()["base_resp"]["status_code"]
            if status == 2045: # hit rate limit
                time.sleep(3)
            i += 1
            if i > 5:
                break
        return response.json()


class OpenAILLM:
    def __init__(self, model_id = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model_id = model_id

    def invoke(self, prompt, schema=None):
        messages = [{"role": "user", "content": prompt}]
        try:
            if schema is None:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    temperature=0,
                    max_tokens=1024,
                )
                return response.choices[0].message.content
            else:
                response = self.client.beta.chat.completions.parse(
                    model=self.model_id,
                    messages=messages,
                    temperature=0,
                    max_tokens=1024,
                    response_format=schema,
                )
            return response.choices[0].message.content
        except Exception as e:
            print(e)
            return None
        
#creaoLM = CreaoLLM()
#r = creaoLM.invoke("hello", {"name":"world"})
#print(r)