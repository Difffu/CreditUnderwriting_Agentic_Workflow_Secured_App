from google import genai
from google.genai import types
import json
from ..utils.config import settings
from ..prompts.basic import chat_prompt, json_prompt

TEXT_MODEL_NAME = settings.GEMINI_MODEL

client = genai.Client(api_key=settings.GOOGLE_API_KEY)



def genai_call_model(context, prompt):
    """
    Calls the Google GenAI model with the provided context and prompt.
    Returns the response text.
    """
    try:
        # context.append(system_prompt)
        # context.append(prompt)
        multiturn = []
        for x in prompt:
            if x['role'] == 'user':
                multiturn.append(types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=x['content'])]
                ))
            if x['role'] == 'assistant':
                multiturn.append(types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=x['content'])]
                ))
        response = client.models.generate_content(
            model=TEXT_MODEL_NAME,
            contents=[chat_prompt, context] + multiturn
        )
        
        if response and response.text:
            return response.text
    except Exception as e:
        return "No response from the model."



def context_to_json(repo_context):
    """
    Converts the repository context to a JSON format based on credit assessment schema.
    """
    
    # Define the schema for the JSON output
    schema = types.Schema(
        type=types.Type.OBJECT,
        required=["company_name", "industry", "assessment_date", "pillars", "total_score", "decision_zone"],
        properties={
            "company_name": types.Schema(type=types.Type.STRING),
            "industry": types.Schema(type=types.Type.STRING),
            "assessment_date": types.Schema(type=types.Type.STRING),
            "pillars": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    required=["pillar", "weight", "metrics", "pillar_avg", "weighted_score"],
                    properties={
                        "pillar": types.Schema(type=types.Type.STRING),
                        "weight": types.Schema(type=types.Type.NUMBER),
                        "metrics": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(
                                type=types.Type.OBJECT,
                                required=["metric", "definition", "applicant_value", "score"],
                                properties={
                                    "metric": types.Schema(type=types.Type.STRING),
                                    "definition": types.Schema(type=types.Type.STRING),
                                    "applicant_value": types.Schema(
                                        anyOf=[
                                            types.Schema(type=types.Type.STRING),
                                            types.Schema(type=types.Type.NUMBER),
                                        ]
                                    ),
                                    "score": types.Schema(type=types.Type.NUMBER),
                                }
                            )
                        ),
                        "pillar_avg": types.Schema(type=types.Type.NUMBER),
                        "weighted_score": types.Schema(type=types.Type.NUMBER),
                    }
                )
            ),
            "total_score": types.Schema(type=types.Type.NUMBER),
            "decision_zone": types.Schema(type=types.Type.STRING),
        }
    )
    
   
    
    try:
        # Create content for the API call
        contents = [ repo_context,
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=json_prompt)],
            )
        ]
        
        # Configure the generation to return JSON
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        )
        
        # Generate the JSON response
        response = client.models.generate_content(
            model=TEXT_MODEL_NAME,
            contents=contents,
            config=generate_content_config,
        )
        
        # Extract and return the JSON response
        if hasattr(response, 'text'):
            print("Generated JSON response successfully.")
            #print(response.text)
            return json.loads(response.text)
        else:
            print("Error: Could not extract JSON from response")
            return None
            
    except Exception as e:
        print(f"Error generating JSON from context: {e}")
        return None
