import copy
import re
import base64
import mimetypes
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain
from core_logic.handlers import HANDLERS, fetch_vimeo_transcript
from core_logic.llm_config import LLM_CONFIG
from core_logic.handlers import format_quiz_for_download, generate_download_filename

# Folder where config files are stored
CONFIG_FOLDER = "config_files"

# Apply master page configuration
def apply_page_config():
    PAGE_CONFIG = config.get('PAGE_CONFIG', {})
    st.set_page_config(
        page_title=PAGE_CONFIG.get("page_title", "AI MicroApps"),
        page_icon=PAGE_CONFIG.get("page_icon", "🤖"),
        layout=PAGE_CONFIG.get("layout", "wide"),
        initial_sidebar_state=PAGE_CONFIG.get("initial_sidebar_state", "collapsed")
    )

# Optionally hide the sidebar
def hide_sidebar():
    SIDEBAR_HIDDEN = config.get('SIDEBAR_HIDDEN', True)
    if SIDEBAR_HIDDEN:
        hide_sidebar_style = """
            <style>
                [data-testid="stSidebar"] {display: none;}
                [data-testid="stSidebarCollapsedControl"] {display: none;}
            </style>
        """
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# Function to merge configuration dictionaries
def merge_configurations(defaults, overrides):
    """
    Merges two dictionaries, with 'overrides' taking precedence over 'defaults'.
    """
    merged = copy.deepcopy(defaults)
    for key, override_values in overrides.items():
        if key in merged:
            merged[key].update(override_values)
        else:
            merged[key] = override_values
    return merged

# Function to evaluate conditional logic
def evaluate_conditions(user_input, condition):
    """
    Evaluates whether the 'user_input' meets the specified 'condition'.
    Supports logical operators like $and, $or, $not, and comparison operators.
    """
    if "$and" in condition:
        return all(evaluate_conditions(user_input, sub_condition) for sub_condition in condition["$and"])
    elif "$or" in condition:
        return any(evaluate_conditions(user_input, sub_condition) for sub_condition in condition["$or"])
    elif "$not" in condition:
        return not evaluate_conditions(user_input, condition["$not"])

    for key, value in condition.items():
        if isinstance(value, dict):
            operator, condition_value = next(iter(value.items()))
            user_value = user_input.get(key)

            if operator == "$gt" and not user_value > condition_value:
                return False
            elif operator == "$lt" and not user_value < condition_value:
                return False
            elif operator == "$gte" and not user_value >= condition_value:
                return False
            elif operator == "$lte" and not user_value <= condition_value:
                return False
            elif operator == "$eq" and not user_value == condition_value:
                return False
            elif operator == "$ne" and not user_value != condition_value:
                return False
            elif operator == "$in" and user_value not in condition_value:
                return False
            elif operator == "$nin" and user_value in condition_value:
                return False
        else:
            if isinstance(value, list):
                if user_input.get(key) not in value:
                    return False
            else:
                if user_input.get(key) != value:
                    return False
    return True

# Function to build input fields based on configuration
def build_field(phase_name, fields,user_input):
    """
    Builds the input fields for a given phase based on the 'fields' configuration.
    Checks for 'showIf' conditions before displaying fields.
    """
    function_map = {
        "text_input": st.text_input,
        "text_area": st.text_area,
        "warning": st.warning,
        "button": st.button,
        "radio": st.radio,
        "markdown": st.markdown,
        "selectbox": st.selectbox,
        "checkbox": st.checkbox,
        "slider": st.slider,
        "number_input": st.number_input,
        "image": st.image,
        "file_uploader": st.file_uploader
    }

    for field_key, field in fields.items():
        # Check showIf conditions
        if 'showIf' in field:
            condition = field['showIf']
            if not evaluate_conditions(user_input, condition):
                continue
        field_type = field.get("type", "")
        field_label = field.get("label", "")
        field_body = field.get("body", "")
        field_value = field.get("value", "")
        field_index = field.get("index", None)
        field_max_chars = field.get("max_chars", None)
        field_help = field.get("help", "")
        field_on_click = field.get("on_click", None)
        field_options = field.get("options", [])
        field_horizontal = field.get("horizontal", False)
        field_min_value = field.get("min_value", None)
        field_max_value = field.get("max_value", None)
        field_step = field.get("step", None)
        field_height = field.get("height", None)
        field_unsafe_html = field.get("unsafe_allow_html", False)
        field_placeholder = field.get("placeholder", "")
        field_image = field.get("image", "")
        field_caption = field.get("caption", "")
        field_allowed_files = field.get("allowed_files", None)
        field_multiple_files = field.get("multiple_files", False)
        field_label_visibility = field.get("label_visibility", None)

        kwargs = {}
        if field_label:
            kwargs['label'] = field_label
        if field_body:
            kwargs['body'] = field_body
        if field_value:
            kwargs['value'] = field_value
        if field_index:
            kwargs['index'] = field_index
        if field_options:
            kwargs['options'] = field_options
        if field_max_chars:
            kwargs['max_chars'] = field_max_chars
        if field_help:
            kwargs['help'] = field_help
        if field_on_click:
            kwargs['on_click'] = field_on_click
        if field_horizontal:
            kwargs['horizontal'] = field_horizontal
        if field_min_value:
            kwargs['min_value'] = field_min_value
        if field_max_value:
            kwargs['max_value'] = field_max_value
        if field_step:
            kwargs['step'] = field_step
        if field_height:
            kwargs['height'] = field_height
        if field_unsafe_html:
            kwargs['unsafe_allow_html'] = field_unsafe_html
        if field_placeholder:
            kwargs['placeholder'] = field_placeholder
        if field_image:
            kwargs['image'] = field_image
        if field_caption:
            kwargs['caption'] = field_caption
        if field_allowed_files:
            kwargs['type'] = field_allowed_files
        if field_multiple_files:
            kwargs['accept_multiple_files'] = field_multiple_files
        if field_label_visibility:
            kwargs['label_visibility'] = field_label_visibility

        key = f"{phase_name}_phase_status"

        # If the user has already answered this question:
        if key in st.session_state and st.session_state[key]:
            # Write their answer
            if f"{phase_name}_user_input_{field_key}" in st.session_state:
                if field_type != "selectbox":
                    kwargs['value'] = st.session_state[f"{phase_name}_user_input_{field_key}"]
                kwargs['disabled'] = True

        my_input_function = function_map[field_type]

        with stylable_container(
                key=f"large_label_{phase_name}_{field_key}",
                css_styles="""
                    label p {
                        font-weight: bold;
                        font-size: 16px;
                    }

                    div[role="radiogroup"] label p{
                        font-weight: unset !important;
                        font-size: unset !important;
                    }
                    """,
        ):
            user_input[field_key] = my_input_function(**kwargs)

# Function to execute LLM completions
def execute_llm_completions(SYSTEM_PROMPT, selected_llm, phase_instructions, user_prompt, image_urls=None):
    """
    Executes LLM completions using the selected model.
    """
    if selected_llm not in LLM_CONFIG:
        raise ValueError(f"Selected model '{selected_llm}' not found in configuration.")

    base_model_config = LLM_CONFIG[selected_llm]
    chat_history = st.session_state["chat_history"]

    # Merge base config with any user overrides from the sidebar
    user_llm_config = st.session_state.get("llm_config", {})
    model_config = {**base_model_config, **user_llm_config}
    family = model_config["family"]

    api_keys = {
        "openai": st.session_state.get("openai_api_key")
    }

    context = {
        "SYSTEM_PROMPT": SYSTEM_PROMPT,
        "phase_instructions": phase_instructions,
        "user_prompt": user_prompt,
        "supports_image": model_config["supports_image"],
        "image_urls": image_urls,
        "model": model_config["model"],
        "max_tokens": model_config["max_tokens"],
        "temperature": model_config["temperature"],
        "top_p": model_config["top_p"],
        "frequency_penalty": model_config["frequency_penalty"],
        "presence_penalty": model_config["presence_penalty"],
        "price_input_token_1M": model_config["price_input_token_1M"],
        "price_output_token_1M": model_config["price_output_token_1M"],
        "TOTAL_PRICE": 0,
        "chat_history": chat_history,
        "api_keys": {k: v for k, v in api_keys.items() if v},
    }

    handler = HANDLERS.get(family)
    if handler:
        try:
            result = handler(context)
        except Exception as e:
            raise RuntimeError(f"Error in handling the LLM request: {e}")
    else:
        raise NotImplementedError(f"No handler implemented for model family '{family}'")
    return result

# Function to apply conditional logic to prompts
def prompt_conditionals(user_input, phase_name=None, phases=None):
    """
    Applies conditional logic to determine the correct prompt based on 'user_input' and 'phase_name'.
    Uses the provided 'phases' to retrieve phase-specific information.
    """
    phase = phases[phase_name]
    if isinstance(phase["user_prompt"], str):
        base_prompt = phase["user_prompt"]
    else:
        additional_prompts = []
        for item in phase["user_prompt"]:
            condition_clause = item["condition"]
            if evaluate_conditions(user_input, condition_clause):
                additional_prompts.append(item["prompt"])
        base_prompt = "\n".join(additional_prompts)
    return base_prompt


# Function to format user prompt with provided inputs
def format_user_prompt(prompt, user_input, phase_name=None, phases=None):
    """
    Formats the 'prompt' using the provided 'user_input' and applies any conditional logic.
    'phases' is required to access phase-specific data.
    """
    try:
        prompt = prompt_conditionals(user_input, phase_name, phases)
        formatted_user_prompt = prompt.format(**{k: user_input.get(k, '') for k in re.findall(r'{(\w+)}', prompt)})
        return formatted_user_prompt
    except Exception as e:
        print(f"Error occurred in format_user_prompt: {e}")
        formatted_user_prompt = prompt.format(**user_input)
        return formatted_user_prompt


# Function to store session state data
def st_store(input, phase_name, phase_key, field_key=""):
    """
    Stores input data in the session state with keys generated from phase and field names.
    """
    if field_key:
        key = f"{phase_name}_{field_key}_{phase_key}"
    else:
        key = f"{phase_name}_{phase_key}"
    st.session_state[key] = input

# Function to build scoring instructions
def build_scoring_instructions(rubric):
    """
    Builds scoring instructions based on the provided rubric for AI scoring.
    """
    scoring_instructions = f"""
        Please score the user's previous response based on the following rubric: \n{rubric}
        \n\nPlease output your response as JSON, using this format: '{{{{ "[criteria 1]": "[score 1]", "[criteria 2]": "[score 2]", "total": "[total score]" }}}}'
        """
    return scoring_instructions

# Function to extract score from AI response
def extract_score(text):
    """
    Extracts the total score from the AI response text.
    """
    pattern = r'"total":\s*"?(\d+)"?'
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    else:
        return 0

# Function to check if the score meets the minimum requirement
def check_score(PHASES,PHASE_NAME):
    """
    Checks if the AI score meets the minimum score requirement for the phase.
    """
    score = st.session_state[f"{PHASE_NAME}_ai_score"]
    try:
        if score >= PHASES[PHASE_NAME]["minimum_score"]:
            st.session_state[f"{PHASE_NAME}_phase_status"] = True
            return True
        else:
            st.session_state[f"{PHASE_NAME}_phase_status"] = False
            return False
    except:
        st.session_state[f"{PHASE_NAME}_phase_status"] = False
        return False

# Function to skip the current phase
def skip_phase(PHASE_NAME, phases, user_input, No_Submit=False):
    """
    Skips the current phase, optionally without submitting data.
    """
    phase_fields = phases[PHASE_NAME]["fields"]  # Access fields from the passed phases argument
    for field_key in phase_fields:
        st_store(user_input[field_key], PHASE_NAME, "user_input", field_key)
    if not No_Submit:
        st.session_state[f"{PHASE_NAME}_ai_response"] = "This phase was skipped."
    st.session_state[f"{PHASE_NAME}_phase_status"] = True
    st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(phases) - 1)


# Function to display a celebration effect
def celebration():
    """
    Displays a celebration effect using falling emojis.
    """
    rain(
        emoji="🥳",
        font_size=54,
        falling_speed=5,
        animation_length=1,
    )

# Function to find image URLs for uploaded app_images
def find_image_urls(user_input,fields):
    """
    Extracts and encodes image URLs from file uploads in the form fields.
    """
    image_urls = []
    for key, value in fields.items():
        if 'image' in value:
            image_urls.append(value['image'])
        if 'file_uploader' in value.values():
            uploaded_files = user_input[key]
            if not isinstance(uploaded_files, list):
                uploaded_files = [uploaded_files]
            for uploaded_file in uploaded_files:
                if uploaded_file:
                    file_content = uploaded_file.read()
                    mime_type, _ = mimetypes.guess_type(uploaded_file.name)
                    if not mime_type:
                        mime_type = 'application/octet-stream'
                    base64_encoded_content = base64.b64encode(file_content).decode('utf-8')
                    image_url = f"data:{mime_type};base64,{base64_encoded_content}"
                    image_urls.append(image_url)
    return image_urls

# Main function to run the application
def main(config):
    """
    The main entry point for the Streamlit application. Handles page setup, form generation,
    prompt processing, and interaction with LLM for responses.
    """
    # Dynamically get configurations from globals
    PAGE_CONFIG = config.get('PAGE_CONFIG',{})
    SIDEBAR_HIDDEN = config.get('SIDEBAR_HIDDEN', True)
    DISPLAY_COST = config.get('DISPLAY_COST', False)
    APP_TITLE = config.get('APP_TITLE',"Default Title")
    APP_INTRO = config.get('APP_INTRO', "")
    APP_HOW_IT_WORKS = config.get('APP_HOW_IT_WORKS',"")
    SHARED_ASSET = config.get('SHARED_ASSET', None)
    HTML_BUTTON = config.get('HTML_BUTTON', None)
    PHASES = config.get('PHASES', {"phase1":{"name":"default phase"}})
    COMPLETION_MESSAGE = config.get('COMPLETION_MESSAGE', 'Process completed successfully.')
    COMPLETION_CELEBRATION = config.get('COMPLETION_CELEBRATION', False)
    LLM_CONFIGURATIONS = LLM_CONFIG
    PREFERRED_LLM = config.get('PREFERRED_LLM', 'openai')
    SYSTEM_PROMPT = config.get('SYSTEM_PROMPT', '')

    # Apply the page configuration
    if PAGE_CONFIG:
        st.set_page_config(
            page_title=PAGE_CONFIG.get("page_title", "AI MicroApps"),
            page_icon=PAGE_CONFIG.get("page_icon", "🤖"),
            layout=PAGE_CONFIG.get("layout", "wide"),
            initial_sidebar_state=PAGE_CONFIG.get("initial_sidebar_state", "collapsed")
        )

    # Optionally hide the sidebar
    if SIDEBAR_HIDDEN:
        hide_sidebar_style = """
                <style>
                    [data-testid="stSidebar"] {display: none;}
                    [data-testid="stSidebarCollapsedControl"] {display: none;}
                </style>
            """
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)

    # Select template from the sidebar
    selected_template = APP_TITLE

    if "template" not in st.session_state or st.session_state.template != selected_template:
        st.session_state.template = selected_template
        st.query_params["template"] = selected_template
        # Clear all session state variables
        keys_to_keep = ['template']  # Add any other keys you want to preserve
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        st.session_state['additional_prompt'] = ""
        st.session_state['chat_history'] = []
        st.session_state['CURRENT_PHASE'] = 0
        st.session_state['TOTAL_PRICE'] = 0

        st.rerun()

    user_input = {}

    image_urls = []
    if 'TOTAL_PRICE' not in st.session_state:
        st.session_state['TOTAL_PRICE'] = 0

    # Handle sidebar: API keys, model selection, and basic generation settings
    with st.sidebar:
        st.subheader("API keys")

        openai_key = st.text_input("OpenAI API key", type="password", key="openai_api_key")

        vimeo_token = st.text_input("Vimeo API Token (optional)", type="password", key="vimeo_api_token", 
                                     help="Used to download Vimeo transcripts for videos. Get one from https://developer.vimeo.com/apps")

        st.caption("Keys are stored only in this session and not persisted on the server.")

        st.markdown("---")

        llm_options = list(LLM_CONFIGURATIONS.keys())
        llm_index = llm_options.index(PREFERRED_LLM) if PREFERRED_LLM in llm_options else 0

        selected_llm = st.selectbox(
            "Language model",
            options=LLM_CONFIGURATIONS.keys(),
            index=llm_index,
            key="selected_llm",
        )

        initial_config = LLM_CONFIGURATIONS[selected_llm]

        # Basic controls that are actually useful to tweak
        with st.expander("Generation settings", expanded=False):
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(initial_config.get("temperature", 1.0)),
                step=0.01,
            )
            max_tokens = st.slider(
                "Max output tokens",
                min_value=50,
                max_value=4000,
                value=int(initial_config.get("max_tokens", 1000)),
                step=50,
            )
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=float(initial_config.get("top_p", 1.0)),
                step=0.1,
            )

        # Store the overrides in session state so the LLM call can use them
        st.session_state["llm_config"] = {
            "model": initial_config["model"],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            # keep penalties from default config (no need to expose sliders)
            "frequency_penalty": initial_config.get("frequency_penalty", 0.0),
            "presence_penalty": initial_config.get("presence_penalty", 0.0),
            # prices stay internal; no UI
            "price_input_token_1M": initial_config.get("price_input_token_1M", 0.0),
            "price_output_token_1M": initial_config.get("price_output_token_1M", 0.0),
        }

        st.markdown("---")

        # Display chat history in the sidebar
        st.subheader("Chat History")
        for history in st.session_state["chat_history"]:
            st.markdown(f"**User:** {history['user']}")
            if "app_images" in history:
                for image in history["app_images"]:
                    st.image(image)
            st.markdown(f"**AI:** {history['assistant']}")
            st.markdown("---")

    # Require an API key for the selected provider
    family_to_service = {
        "openai": "openai",
        "claude": "claude",
        "gemini": "google",       # using GOOGLE_API_KEY for Gemini
        "perplexity": "perplexity",
        "rag": "openai",          # RAG pipeline uses OpenAI under the hood
    }

    selected_family = LLM_CONFIGURATIONS[selected_llm]["family"]
    service_name = family_to_service.get(selected_family)

    if service_name:
        required_key = st.session_state.get(f"{service_name}_api_key")
        if not required_key:
            st.warning(
                f"Please enter a valid {service_name.capitalize()} API key in the sidebar "
                f"to use this app with **{selected_llm}**."
            )
            st.stop()

    # Main content rendering
    if 'CURRENT_PHASE' not in st.session_state:
        st.session_state['CURRENT_PHASE'] = 0

    st.title(APP_TITLE)
    st.markdown(APP_INTRO)

    # Optionally show "How it Works" section
    if APP_HOW_IT_WORKS:
        with st.expander("Learn how this works", expanded=False):
            st.markdown(APP_HOW_IT_WORKS)

    '''
    # Optional asset download
    if SHARED_ASSET:
        with open(SHARED_ASSET["path"], "rb") as asset_file:
            st.download_button(label=SHARED_ASSET["button_text"],
                               data=asset_file,
                               file_name=SHARED_ASSET["name"],
                               mime="application/octet-stream")
    
    if HTML_BUTTON:
        st.link_button(label=HTML_BUTTON["button_text"], url=HTML_BUTTON["url"])
    '''

    # Phase rendering and logic
    i = 0
    while i <= st.session_state['CURRENT_PHASE']:
        submit_button = False
        skip_button = False
        final_phase_name = list(PHASES.keys())[-1]
        final_key = f"{final_phase_name}_ai_response"

        PHASE_NAME = list(PHASES.keys())[i]
        PHASE_DICT = PHASES[PHASE_NAME]
        fields = PHASE_DICT["fields"]

        st.write(f"#### Phase {i + 1}: {PHASE_DICT['name']}")

        build_field(PHASE_NAME, fields,user_input)

        key = f"{PHASE_NAME}_phase_status"
        user_prompt_template = PHASE_DICT.get("user_prompt", "")
        if PHASE_DICT.get("show_prompt", False):
            with st.expander("View/edit full prompt"):
                formatted_user_prompt = st.text_area(
                    label="Prompt",
                    height=100,
                    max_chars=50000,
                    value=format_user_prompt(user_prompt_template, user_input, PHASE_NAME,PHASES),
                    disabled=PHASE_DICT.get("read_only_prompt", False)
                )
        else:
            formatted_user_prompt = format_user_prompt(user_prompt_template, user_input, PHASE_NAME,PHASES)

        if PHASE_DICT.get("no_submission", False):
            if key not in st.session_state:
                st.session_state[key] = True
                st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES) - 1)
                st.session_state[f"{PHASE_NAME}_phase_completed"] = True
                st.rerun()

        if key not in st.session_state:
            st.session_state[key] = False

        if not st.session_state.get(f"{PHASE_NAME}_phase_completed", False):
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    submit_button = st.button(label=PHASE_DICT.get("button_label", "Submit"), type="primary",
                                              key=f"submit {i}")
                with col2:
                    if PHASE_DICT.get("allow_skip", False):
                        skip_button = st.button(label="Skip Question", key=f"skip {i}")

        key = f"{PHASE_NAME}_ai_response"
        if key in st.session_state and st.session_state[key]:
            st.info(st.session_state[key], icon="🤖")
            # Add download buttons for the quiz
            ai_response_content = st.session_state[key]
            col1, col2 = st.columns(2)
            with col1:
                # Download as plain text
                plain_text_content = format_quiz_for_download(ai_response_content, "plain_text")
                plain_filename = generate_download_filename("txt")
                st.download_button(
                    label="📄 Download as Text",
                    data=plain_text_content,
                    file_name=plain_filename,
                    mime="text/plain",
                    key=f"download_text_{PHASE_NAME}"
                )
            with col2:
                # Download as OLX
                olx_content = format_quiz_for_download(ai_response_content, "olx")
                olx_filename = generate_download_filename("xml")
                st.download_button(
                    label="⚙️ Download as OLX",
                    data=olx_content,
                    file_name=olx_filename,
                    mime="application/xml",
                    key=f"download_olx_{PHASE_NAME}"
                )

        key = f"{PHASE_NAME}_ai_score_debug"
        if key in st.session_state and st.session_state[key]:
            st.info(st.session_state[key], icon="🤖")

        key = f"{PHASE_NAME}_ai_response_revision_1"
        if key in st.session_state and st.session_state[key]:
            z = 1
            while z <= PHASE_DICT.get("max_revisions", 10):
                key = f"{PHASE_NAME}_ai_response_revision_{z}"
                if key in st.session_state and st.session_state[key]:
                    st.info(st.session_state[key], icon="🤖")
                    # Add download buttons for revised responses
                    revision_content = st.session_state[key]
                    col1, col2 = st.columns(2)
                    with col1:
                        plain_text_content = format_quiz_for_download(revision_content, "plain_text")
                        plain_filename = generate_download_filename("txt").replace(".txt", f"_rev{z}.txt")
                        st.download_button(
                            label="📄 Download as Text",
                            data=plain_text_content,
                            file_name=plain_filename,
                            mime="text/plain",
                            key=f"download_text_{PHASE_NAME}_rev{z}"
                        )
                    with col2:
                        olx_content = format_quiz_for_download(revision_content, "olx")
                        olx_filename = generate_download_filename("xml").replace(".xml", f"_rev{z}.xml")
                        st.download_button(
                            label="⚙️ Download as OLX",
                            data=olx_content,
                            file_name=olx_filename,
                            mime="application/xml",
                            key=f"download_olx_{PHASE_NAME}_rev{z}"
                        )
                z += 1

        if submit_button:
            # If the user provided a Vimeo URL, attempt to fetch and clean the transcript
            vimeo_url = (user_input.get("vimeo_url") or "").strip()
            if vimeo_url:
                try:
                    vimeo_token = st.session_state.get("vimeo_api_token", "").strip() or None
                    with st.spinner("Fetching Vimeo transcript..."):
                        transcript = fetch_vimeo_transcript(vimeo_url, vimeo_token=vimeo_token)
                    if transcript:
                        # populate the topic_content with the cleaned transcript
                        user_input["topic_content"] = transcript
                        st.success(f"✅ Successfully fetched transcript ({len(transcript)} characters)")
                        # Re-format the user prompt now that we have the transcript
                        formatted_user_prompt = format_user_prompt(user_prompt_template, user_input, PHASE_NAME, PHASES)
                    else:
                        st.warning("⚠️ Could not find captions/transcript for the provided Vimeo URL. Check if the video has captions enabled.")
                except Exception as e:
                    st.error(f"❌ Error fetching Vimeo transcript: {e}")

            for field_key, field in fields.items():
                st_store(user_input.get(field_key, ""), PHASE_NAME, "user_input", field_key)

            phase_instructions = PHASE_DICT.get("phase_instructions", "")

            image_urls = find_image_urls(user_input,PHASE_DICT.get('fields', {}))

            if PHASE_DICT.get("ai_response", True):
                if PHASE_DICT.get("scored_phase", False):
                    if "rubric" in PHASE_DICT:
                        scoring_instructions = build_scoring_instructions(PHASE_DICT["rubric"])
                        ai_feedback = execute_llm_completions(SYSTEM_PROMPT,selected_llm, phase_instructions, formatted_user_prompt,
                                                              image_urls)
                        st.info(body=ai_feedback, icon="🤖")
                        ai_score = execute_llm_completions(SYSTEM_PROMPT,selected_llm, scoring_instructions, ai_feedback)
                        st.info(ai_score, icon="🤖")
                        st_store(ai_feedback, PHASE_NAME, "ai_response")
                        st_store(ai_score, PHASE_NAME, "ai_score_debug")
                        score = extract_score(ai_score)
                        st_store(score, PHASE_NAME, "ai_score")
                        chat_history_entry = {
                            "user": formatted_user_prompt,
                            "assistant": ai_feedback
                        }
                        if image_urls:
                            chat_history_entry["app_images"] = image_urls

                        st.session_state['chat_history'].append(chat_history_entry)
                        st.session_state["ai_score"] = ai_score
                        st.session_state['score'] = score
                        if check_score(PHASES,PHASE_NAME):
                            st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1,
                                                                    len(PHASES) - 1)
                            st.session_state[f"{PHASE_NAME}_phase_completed"] = True
                            st.rerun()
                        else:
                            st.warning("You haven't passed. Please try again.")
                    else:
                        st.error('You need to include a rubric for a scored phase', icon="🚨")
                else:
                    ai_feedback = execute_llm_completions(SYSTEM_PROMPT,selected_llm, phase_instructions, formatted_user_prompt,
                                                          image_urls)
                    st_store(ai_feedback, PHASE_NAME, "ai_response")
                    chat_history_entry = {
                        "user": formatted_user_prompt,
                        "assistant": ai_feedback
                    }
                    if image_urls:
                        chat_history_entry["app_images"] = image_urls

                    st.session_state['chat_history'].append(chat_history_entry)
                    st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES) - 1)
                    st.session_state[f"{PHASE_NAME}_phase_completed"] = True
                    st.rerun()
            else:
                res_box = st.info(body="", icon="🤖")
                result = ""
                hard_coded_message = PHASE_DICT.get('custom_response', None)
                hard_coded_message = format_user_prompt(hard_coded_message, user_input, PHASE_NAME,PHASES)
                for char in hard_coded_message:
                    result += char
                    res_box.info(body=result, icon="🤖")
                st.session_state[f"{PHASE_NAME}_ai_response"] = hard_coded_message
                chat_history_entry = {
                    "user": formatted_user_prompt,
                    "assistant": hard_coded_message
                }
                if image_urls:
                    chat_history_entry["app_images"] = image_urls

                st.session_state['chat_history'].append(chat_history_entry)
                st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES) - 1)
                st.session_state[f"{PHASE_NAME}_phase_completed"] = True
                st.rerun()

        if PHASE_DICT.get("allow_revisions", False):
            if f"{PHASE_NAME}_ai_response" in st.session_state:
                is_latest_completed_phase = i == st.session_state['CURRENT_PHASE'] or (
                        i == st.session_state['CURRENT_PHASE'] - 1 and not st.session_state.get(
                    f"{list(PHASES.keys())[i + 1]}_phase_completed", False))

                is_last_phase = (PHASE_NAME == final_phase_name)
                is_not_skipped = not st.session_state.get(f"{PHASE_NAME}_skipped", False)

                if (is_latest_completed_phase or is_last_phase) and is_not_skipped:
                    with st.expander("Revise this response?"):
                        max_revisions = PHASE_DICT.get("max_revisions", 10)
                        if f"{PHASE_NAME}_revision_count" not in st.session_state:
                            st_store(0, PHASE_NAME, "revision_count")
                        if st.session_state[f"{PHASE_NAME}_revision_count"] < max_revisions:
                            st.session_state['additional_prompt'] = st.text_input("Enter additional prompt", value="",
                                                                                  key=PHASE_NAME)
                            if st.button("Revise", key=f"revise_{i}"):
                                st.session_state[f"{PHASE_NAME}_revision_count"] += 1

                                phase_instructions = PHASE_DICT.get("phase_instructions", "")
                                user_prompt_template = PHASE_DICT.get("user_prompt", "")
                                formatted_user_prompt = format_user_prompt(user_prompt_template, user_input, PHASE_NAME,PHASES)

                                formatted_user_prompt += st.session_state['additional_prompt']

                                ai_feedback = execute_llm_completions(SYSTEM_PROMPT,selected_llm, phase_instructions,
                                                                      formatted_user_prompt)

                                st_store(ai_feedback, PHASE_NAME, "ai_response_revision_" + str(
                                    st.session_state[f"{PHASE_NAME}_revision_count"]))
                                chat_history_entry = {
                                    "user": formatted_user_prompt,
                                    "assistant": ai_feedback
                                }
                                if image_urls:
                                    chat_history_entry["app_images"] = image_urls
                                st.session_state['chat_history'].append(chat_history_entry)
                                st.rerun()
                        else:
                            st.warning("Revision limits exceeded")

        if skip_button:
            skip_phase(PHASE_NAME,PHASES,user_input)
            st.session_state[f"{PHASE_NAME}_phase_completed"] = True
            st.session_state[f"{PHASE_NAME}_skipped"] = True
            st.rerun()

        if final_key in st.session_state and i == st.session_state['CURRENT_PHASE']:
            st.success(COMPLETION_MESSAGE)
            if COMPLETION_CELEBRATION:
                celebration()

        i = min(i + 1, len(PHASES))
