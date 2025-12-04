import openai
import anthropic
import google.generativeai as genai
#from core_logic import rag_pipeline
import requests
import os
from dotenv import load_dotenv
import re

load_dotenv()


# --- Vimeo transcript helpers ---
def clean_vtt_or_srt(text: str) -> str:
    """Clean VTT/SRT style transcript text by removing timestamps, cue numbers and headers.

    Returns a cleaned single string containing transcript sentences.
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        # skip WEBVTT header
        if line_strip.upper().startswith("WEBVTT"):
            continue
        # skip sequence numbers in SRT
        if line_strip.isdigit():
            continue
        # skip lines that are timestamps or contain the arrow separator
        if "-->" in line_strip:
            continue
        # remove bracketed timestamps like [00:01:23]
        line_strip = re.sub(r"\[\d{1,2}:\d{2}(?::\d{2})?\]", "", line_strip)
        # remove inline timestamps mm:ss or hh:mm:ss patterns
        line_strip = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", "", line_strip)
        # collapse whitespace
        line_strip = re.sub(r"\s+", " ", line_strip).strip()
        if line_strip:
            cleaned_lines.append(line_strip)

    cleaned = " ".join(cleaned_lines)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def fetch_vimeo_transcript(vimeo_url: str, vimeo_token: str = None, timeout: int = 10) -> str:
    """Fetch the transcript for a Vimeo video URL.

    Strategy:
    - If vimeo_token is provided, use the Vimeo API v3 to get transcripts with auth
    - Otherwise, extract Vimeo numeric id from the URL and query the player config
    - Download the first suitable text track (prefer English)
    - Clean timestamps and return plain text

    Args:
        vimeo_url: URL of the Vimeo video
        vimeo_token: Optional Vimeo API token for authenticated requests
        timeout: Request timeout in seconds

    Returns cleaned transcript string or empty string if not found.
    """
    if not vimeo_url:
        return ""
    
    vimeo_url = vimeo_url.strip()
    if not vimeo_url:
        return ""
    
    # Extract numeric id from URL
    m = re.search(r"vimeo\.com/(?:.*?/)?(\d+)", vimeo_url)
    if not m:
        raise ValueError(f"Could not extract Vimeo video id from URL: {vimeo_url}")
    vid = m.group(1)
    print(f"[DEBUG] Extracted Vimeo video ID: {vid}")

    # If token is provided, try the authenticated API endpoint
    if vimeo_token:
        try:
            print(f"[DEBUG] Attempting to fetch transcript with API token for video {vid}")
            api_url = f"https://api.vimeo.com/videos/{vid}/texttracks"
            headers = {
                "Authorization": f"Bearer {vimeo_token}",
                "Accept": "application/vnd.vimeo.*+json;version=3.4"
            }
            resp = requests.get(api_url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            
            print(f"[DEBUG] API response: {data}")
            
            if "data" in data and data["data"]:
                # Find English track or use first available
                track = None
                for t in data["data"]:
                    lang = t.get("language", "").lower()
                    if lang and lang.startswith("en"):
                        track = t
                        break
                if not track:
                    track = data["data"][0]
                
                print(f"[DEBUG] Selected track: {track}")
                
                # Download the transcript file
                track_url = track.get("link")
                if track_url:
                    print(f"[DEBUG] Downloading transcript from: {track_url}")
                    tt_resp = requests.get(track_url, timeout=timeout)
                    tt_resp.raise_for_status()
                    raw_text = tt_resp.text
                    print(f"[DEBUG] Downloaded transcript, size: {len(raw_text)} bytes")
                    cleaned = clean_vtt_or_srt(raw_text)
                    print(f"[DEBUG] Cleaned transcript, size: {len(cleaned)} characters")
                    return cleaned
        except Exception as e:
            print(f"[DEBUG] API method failed: {type(e).__name__}: {e}")
            # Fall back to player config method if API fails

    # Fallback: use player config (works for public videos)
    try:
        print(f"[DEBUG] Attempting to fetch transcript from player config for video {vid}")
        config_url = f"https://player.vimeo.com/video/{vid}/config"
        resp = requests.get(config_url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"[DEBUG] Player config response keys: {data.keys()}")

        # locate text tracks
        text_tracks = []
        # common places where text tracks appear in the config
        if isinstance(data.get("request"), dict):
            files = data["request"].get("files", {})
            text_tracks = files.get("text_tracks") or data["request"].get("text_tracks") or []
        text_tracks = text_tracks or data.get("text_tracks") or []

        print(f"[DEBUG] Found {len(text_tracks)} text tracks")
        
        if not text_tracks:
            print(f"[DEBUG] No text tracks found in player config")
            return ""

        # prefer english track
        track = None
        for t in text_tracks:
            lang = t.get("lang", "").lower()
            if lang and lang.startswith("en"):
                track = t
                break
        if not track:
            track = text_tracks[0]

        print(f"[DEBUG] Selected track: {track}")
        
        track_url = track.get("url")
        if not track_url:
            print(f"[DEBUG] No URL in track")
            return ""

        print(f"[DEBUG] Downloading transcript from: {track_url}")
        tt_resp = requests.get(track_url, timeout=timeout)
        tt_resp.raise_for_status()
        raw_text = tt_resp.text
        print(f"[DEBUG] Downloaded transcript, size: {len(raw_text)} bytes")
        cleaned = clean_vtt_or_srt(raw_text)
        print(f"[DEBUG] Cleaned transcript, size: {len(cleaned)} characters")
        return cleaned
    except Exception as e:
        print(f"[DEBUG] Player config method failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return ""

# fetching api key for LLM interactions
def get_api_key(service_name, context=None):
    """Retrieve API key from context (preferred) or environment variables."""
    # 1) Prefer keys passed from the Streamlit app
    if context and "api_keys" in context:
        key_from_context = context["api_keys"].get(service_name)
        if key_from_context:
            return key_from_context

    # 2) Fallback to environment variables (.env or deployment secrets)
    env_var_name = f"{service_name.upper()}_API_KEY"
    api_key = os.getenv(env_var_name)

    if not api_key:
        raise ValueError(f"API key for {service_name} not found in context or environment variables.")

    return api_key

# chat history formatting for different LLMs
def format_chat_history(chat_history, family):
    """Format chat history based on LLM family."""
    formatted_history = []
    if len(chat_history) > 0:
        for history in chat_history:
            user_content = history["user"]
            assistant_content = history["assistant"]
            if family == "gemini":
                formatted_history.extend([
                    {"role": "user", "parts": [user_content]},
                    {"role": "model", "parts": [assistant_content]}
                ])

            else:
                formatted_history.extend([
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content}
                ])
    return formatted_history

# openai llm handler
def handle_openai(context):
    """Handle requests for OpenAI models."""
    if not context["supports_image"] and context.get("image_urls"):
        return "Images are not supported by selected model."
    try:
        openai.api_key = get_api_key("openai", context)

        messages = format_chat_history(context["chat_history"], "openai") + [
            {"role": "system", "content": context["SYSTEM_PROMPT"]},
            {"role": "assistant", "content": context["phase_instructions"]},
            {"role": "user", "content": context["user_prompt"]}
        ]

        if context["supports_image"] and context["image_urls"]:
            messages.insert(2, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": url}} for url in
                                                            context["image_urls"]]})

        response = openai.chat.completions.create(
            model=context["model"],
            messages=messages,
            temperature=context["temperature"],
            max_tokens=context["max_tokens"],
            top_p=context["top_p"],
            frequency_penalty=context["frequency_penalty"],
            presence_penalty=context["presence_penalty"]
        )
        input_price = int(response.usage.prompt_tokens) * context["price_input_token_1M"] / 1000000
        output_price = int(response.usage.completion_tokens) * context["price_output_token_1M"] / 1000000
        total_price = input_price + output_price
        context['TOTAL_PRICE'] += total_price
        return response.choices[0].message.content
    except Exception as e:
        return f"Unexpected error while handling OpenAI request: {e}"

# claude llm handler
def handle_claude(context):
    """Handle requests for Claude models."""
    if not context["supports_image"] and context.get("image_urls"):
        return "Images are not supported by selected model."
    try:
        client = anthropic.Anthropic(api_key=get_api_key("claude", context))

        messages = format_chat_history(context["chat_history"], "claude") + [
            {"role": "user", "content": [{"type": "text", "text": context["user_prompt"]}]},
            {"role": "assistant", "content": [{"type": "text", "text": context["phase_instructions"]}]}
        ]

        if context["supports_image"] and context["image_urls"]:
            for image_url in context["image_urls"]:
                # Extract base64 data from the image URL
                base64_data = image_url.split(",")[1]
                mime_type = re.search(r"data:(.*?);base64,", image_url).group(1) if re.search(r"data:(.*?);base64,",
                                                                                              image_url) else None
                # Add image to the messages
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": base64_data
                        }
                    }]
                })
        response = client.messages.create(
            model=context["model"],
            max_tokens=context["max_tokens"],
            temperature=context["temperature"],
            system=f"{context['SYSTEM_PROMPT']}",
            messages=messages
        )
        input_price = int(response.usage.input_tokens) * context["price_input_token_1M"] / 1000000
        output_price = int(response.usage.output_tokens) * context["price_output_token_1M"] / 1000000
        total_price = input_price + output_price
        context['TOTAL_PRICE'] += total_price
        return '\n'.join([block.text for block in response.content if block.type == 'text'])
    except Exception as e:
        return f"Unexpected error while handling Claude request: {e}"

# gemini llm handler
def handle_gemini(context):
    """Handle requests for Gemini models."""
    if not context["supports_image"] and context.get("image_urls"):
        return "Images are not supported by selected model."
    try:
        genai.configure(api_key=get_api_key("google", context))

        messages = format_chat_history(context["chat_history"], "gemini") + [
            {"role": "user", "parts": [context["user_prompt"]]},
            {"role": "model", "parts": [context["phase_instructions"]]}
        ]

        if context["supports_image"] and context["image_urls"]:
            for image_url in context["image_urls"]:
                # Add image to the messages
                messages.append({
                    "role": "user",
                    "parts": [image_url]
                })

        chat_session = genai.GenerativeModel(
            model_name=context["model"],
            generation_config= {"temperature": context["temperature"],"top_p": context["top_p"],"max_output_tokens": context["max_tokens"],"response_mime_type":"text/plain"},
            system_instruction=f"{context['SYSTEM_PROMPT']}"
        ).start_chat(history=messages)
        response = chat_session.send_message(context["user_prompt"])
        return response.text
    except Exception as e:
        return f"Unexpected error while handling Gemini request: {e}"

# perplexity handler
def handle_perplexity(context):
    """Handle requests for Perplexity models."""
    if not context["supports_image"] and context.get("image_urls"):
        return "Images are not supported by selected model."
    api_key = get_api_key("perplexity", context)
    url = "https://api.perplexity.ai/chat/completions"

    # Prepare messages
    messages = [
                   {"role": "system", "content": context["SYSTEM_PROMPT"] + context["phase_instructions"]}
               ] + format_chat_history(context["chat_history"], "perplexity") + [
                   {"role": "user", "content": context["user_prompt"]}
               ]

    # Add image URLs if supported
    if context["supports_image"] and context["image_urls"]:
        for image_url in context["image_urls"]:
            messages.append({
                "role": "user",
                "content": {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
            })

    # Prepare payload
    payload = {
        "model": context["model"],
        "messages": messages
    }

    # Prepare headers
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    # Make the API request
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        response_json = response.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            return "Unexpected response format from Perplexity API."

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred while handling Perplexity request: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Error occurred while making the Perplexity request: {req_err}"


def rag_handler(context):
    """
    RAG Handler that processes the document, retrieves relevant information,
    and generates a response using the OpenAI language model.

    Args:
    - context: A dictionary containing the file path, user prompt, and LLM configuration.

    Returns:
    - Generated response and cost.
    """
    # Step 1: Extract necessary information from the context
    file_path = context.get("file_path", None)
    user_prompt = context.get("user_prompt", "")

    if not file_path:
        raise ValueError("File path is required for RAG-based generation.")
    if not user_prompt:
        raise ValueError("User prompt is required.")

    # Step 2: Check and store metadata and embeddings if not already present
    rag_pipeline.check_and_store_metadata_and_embeddings(file_path)

    # Step 4: Retrieve relevant documents based on the user's query and generate a response
    try:
        # Call the retrieval and response generation pipeline
        rag_response, cost = rag_pipeline.retrieve_and_generate_response(
            question= user_prompt,
            template_text= str(context["phase_instructions"])+" User answer is "+ user_prompt
        )
        print(rag_response,cost)
        # Step 5: Update the context with the cost (if applicable)
        context["TOTAL_PRICE"] = context.get("TOTAL_PRICE", 0) + (cost if cost else 0)
        return rag_response
    except Exception as e:
        return f"Error during RAG processing: {e}"


# Mapping of model families to handler functions
HANDLERS = {
    "openai": handle_openai,
    "claude": handle_claude,
    "gemini": handle_gemini,
    "perplexity": handle_perplexity,
    "rag":rag_handler
}


# --- Quiz Export Functions ---
def format_quiz_for_download(quiz_content: str, format_type: str = "plain_text") -> str:
    """
    Format quiz content for download.
    
    Args:
        quiz_content: The raw quiz content from the LLM
        format_type: Either "plain_text" or "olx"
    
    Returns:
        Formatted quiz content as string
    """
    if format_type.lower() == "olx":
        return quiz_content  # OLX format should already be formatted by the LLM
    else:  # plain_text
        return quiz_content  # Plain text should already be formatted by the LLM


def generate_download_filename(output_format: str = "txt") -> str:
    """Generate a filename for the quiz download.

    The `output_format` may be values like 'plain_text', 'txt', 'olx', or 'xml'.
    We normalize accepted values so that both 'olx' and 'xml' produce an .xml filename,
    and everything else produces a .txt filename.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fmt = (output_format or "").lower()
    if fmt in ("olx", "xml") or "olx" in fmt:
        return f"quiz_{timestamp}.xml"
    return f"quiz_{timestamp}.txt"
