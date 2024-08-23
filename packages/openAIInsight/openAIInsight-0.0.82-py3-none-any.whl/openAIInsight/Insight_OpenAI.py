import requests, json, traceback
from flask import request
import loggerutility as logger
import commonutility as common
import os
from openai import OpenAI

class InsightOpenAI:
    userId = ""
    def getCompletionEndpoint(self,jsonData,final_instruction):
        try:
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"\njsonData openAI class::: {jsonData}","0")

            # licenseKey      = jsonData['license_key']
            # openai_api_key   =  jsonData['openAI_APIKey'] 
            openai_api_key = "sk-svcacct-xoSzrEWzvU4t1fbEluOkT3BlbkFJkj7Pvc8kU98y1P3LdI1c"
            insightInput    = jsonData['insight_input']
            enterpriseName  = jsonData['enterprise']  
            
            if 'userId' in jsonData.keys():
                self.userId = jsonData['userId'] 

            client = OpenAI(
                                api_key = openai_api_key 
                            )

            if self.userId and self.userId != "":
                response = client.chat.completions.create(
                                                            model="gpt-4o-mini",
                                                            messages= final_instruction,
                                                            temperature=0.25,
                                                            max_tokens=350,
                                                            top_p=0.5,
                                                            frequency_penalty=0,
                                                            presence_penalty=0,
                                                            user=self.userId,
                                                            )
            else:
                response = client.chat.completions.create(
                                                         	model="gpt-4o-mini",
                                                        	messages= final_instruction,
                                                        	temperature=0.25,
                                                        	max_tokens=350,
                                                        	top_p=0.5,
                                                        	frequency_penalty=0,
                                                        	presence_penalty=0,
                                                    		)
            logger.log(f"\n\nResponse openAI ChatCompletion endpoint::::: {response} \n{type(response)}","0")
            finalResult=str(response.choices[0].message.content)
            logger.log(f"\n\nOpenAI ChatCompletion endpoint finalResult ::::: {finalResult} \n{type(finalResult)}","0")
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)
