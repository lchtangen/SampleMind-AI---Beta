"""
SampleMind AI - Assistant-UI Integration with Claude Sonnet 4.5
Backend API endpoint for streaming chat completions
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator
import anthropic
import os
import json
from loguru import logger

router = APIRouter(prefix="/api/assistant", tags=["assistant-ui"])

# Initialize Anthropic client
anthropic_client = anthropic.AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


class Message(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str | List[Dict[str, Any]] = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request"""
    messages: List[Message] = Field(..., description="Conversation history")
    model: str = Field(default="claude-sonnet-4.5-20250514", description="Model to use")
    max_tokens: int = Field(default=8192, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    stream: bool = Field(default=True, description="Enable streaming")


async def stream_anthropic_response(
    messages: List[Message],
    model: str,
    max_tokens: int,
    temperature: float,
) -> AsyncGenerator[str, None]:
    """
    Stream responses from Anthropic Claude API

    Yields data in assistant-ui compatible format:
    - 0:"text-delta" for text chunks
    - 0:"finish" for completion
    """
    try:
        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = None

        for msg in messages:
            if msg.role == "system":
                # Extract system message (Anthropic handles it separately)
                if isinstance(msg.content, str):
                    system_message = msg.content
                else:
                    system_message = msg.content[0].get("text", "")
            else:
                # Handle text content
                if isinstance(msg.content, str):
                    content = msg.content
                elif isinstance(msg.content, list):
                    # Extract text from content array
                    content = ""
                    for part in msg.content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            content += part.get("text", "")
                else:
                    content = str(msg.content)

                anthropic_messages.append({
                    "role": msg.role,
                    "content": content
                })

        logger.info(f"Streaming Claude {model} with {len(anthropic_messages)} messages")

        # Create streaming request
        stream_kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": anthropic_messages,
        }
        if system_message:
            stream_kwargs["system"] = system_message

        async with anthropic_client.messages.stream(**stream_kwargs) as response:
            # Send initial chunk
            yield '0:""\n'

            # Stream text deltas
            async for text in response.text_stream:
                if text:
                    # Escape newlines and quotes for JSON
                    escaped_text = json.dumps(text)[1:-1]  # Remove surrounding quotes
                    yield f'0:"{escaped_text}"\n'

            # Get final message
            final_message = await response.get_final_message()

            # Send finish event with usage data
            finish_data = {
                "type": "finish",
                "usage": {
                    "input_tokens": final_message.usage.input_tokens,
                    "output_tokens": final_message.usage.output_tokens,
                }
            }
            yield f'e:{json.dumps(finish_data)}\n'

            logger.success(
                f"Completed stream - Input: {final_message.usage.input_tokens} tokens, "
                f"Output: {final_message.usage.output_tokens} tokens"
            )

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        error_data = {"type": "error", "error": str(e)}
        yield f'e:{json.dumps(error_data)}\n'

    except Exception as e:
        logger.error(f"Unexpected error in stream: {e}", exc_info=True)
        error_data = {"type": "error", "error": f"Internal server error: {str(e)}"}
        yield f'e:{json.dumps(error_data)}\n'


@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """
    Chat completion endpoint compatible with assistant-ui

    Supports both streaming and non-streaming responses.
    Streaming format follows Vercel AI SDK protocol.
    """
    try:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY environment variable not set"
            )

        if request.stream:
            # Return streaming response
            return StreamingResponse(
                stream_anthropic_response(
                    messages=request.messages,
                    model=request.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable nginx buffering
                },
            )
        else:
            # Non-streaming response
            anthropic_messages = []
            system_message = None

            for msg in request.messages:
                if msg.role == "system":
                    if isinstance(msg.content, str):
                        system_message = msg.content
                else:
                    if isinstance(msg.content, str):
                        content = msg.content
                    elif isinstance(msg.content, list):
                        content = ""
                        for part in msg.content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                content += part.get("text", "")
                    else:
                        content = str(msg.content)

                    anthropic_messages.append({
                        "role": msg.role,
                        "content": content
                    })

            # Build request kwargs
            create_kwargs: Dict[str, Any] = {
                "model": request.model,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "messages": anthropic_messages,
            }
            if system_message:
                create_kwargs["system"] = system_message

            response = await anthropic_client.messages.create(**create_kwargs)

            # Extract text from response
            content_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content_text += block.text

            return {
                "role": "assistant",
                "content": content_text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            }

    except HTTPException:
        raise
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {str(e)}")
    except Exception as e:
        logger.error(f"Chat completion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))

    return {
        "status": "healthy" if has_api_key else "misconfigured",
        "service": "assistant-ui-claude",
        "model": "claude-sonnet-4.5-20250514",
        "api_key_configured": has_api_key,
    }
