import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Query
from google import genai
from google.genai import types
from ..utils.logger import logger
from ..utils.config import settings
from ..auth.security import verify_token

# Initialize Gemini client
client = genai.Client(api_key=settings.GOOGLE_API_KEY)
model_name = settings.GEMINI_MODEL


async def authenticate_websocket(websocket: WebSocket, token: str):
    """Authenticate WebSocket connection using JWT token"""
    try:
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return None
        return payload.get("sub")  # Return user email
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Authentication failed")
        return None

router = APIRouter(tags=["Chat"])

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(..., alias="token"),):
    await websocket.accept()

    # Authenticate user
    user_email = await authenticate_websocket(websocket, token)
    if not user_email:
        return

    logger.info(f"Authenticated user: {user_email}")
    logger.info("WebSocket connection established")
    
    try:

        # Initialize conversation history
        conversation = []
        
        while True:
            # Receive message from client
            user_message = await websocket.receive_text()
            logger.info(f"Received message: {user_message}")
            
            # Add user message to conversation
            conversation.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)],
                )
            )
            
            # Create config for streaming
            # generate_content_config = types.GenerateContentConfig(
            #     thinking_config=types.ThinkingConfig(thinking_budget=-1),
            # )
            
            # Stream response from Gemini
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=conversation,
                # config=generate_content_config,
            )
            
            # Stream chunks to client
            full_response = ""
            for chunk in response_stream:
                if chunk.text:
                    await websocket.send_text(chunk.text)
                    full_response += chunk.text
            
            # Add model response to conversation
            conversation.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=full_response)],
                )
            )
            
            logger.info(f"Sent response: {full_response}")
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason=str(e))