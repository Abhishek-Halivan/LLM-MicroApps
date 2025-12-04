"""
Custom CSS styles for the Streamlit MCQ Generator app.
This module provides the styling for the web interface.
"""


def get_custom_styles():
    """
    Returns the custom CSS styling for the application.
    
    Returns:
        str: CSS styling wrapped in <style> tags for use with st.markdown
    """
    return """
    <style>
        /* Palette & variables (concise and accessible) */
        :root{
            --primary: #0b63ff; /* vivid blue */
            --accent: #ff6b6b;  /* coral accent */
            --muted: #6b7280;   /* secondary text */
            --bg: #ffffff;
            --surface: #f8fafc; /* cards */
            --card-border: #e6eefc;
            --code-bg: #0f1724; /* dark code bg */
            --text: #0f1724;    /* main text */
            --radius: 10px;
            --shadow-sm: 0 6px 18px rgba(11,99,255,0.08);
            --shadow-md: 0 12px 28px rgba(11,99,255,0.08);
        }

        /* Base layout and typography */
        html,body{
            height:100%;
            background: linear-gradient(180deg, #f5f5f0 0%, #efefea 100%);
            color:var(--text);
            font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
            -webkit-font-smoothing:antialiased;
            -moz-osx-font-smoothing:grayscale;
            line-height:1.5;
            font-size:18px;
        }

        /* Main container padding */
        .main{ padding:28px; }

        /* Headings - clear hierarchy */
        h1{ font-size:32px; margin:0 0 12px 0; color:var(--primary); font-weight:700; }
        h2{ font-size:26px; margin:20px 0 10px 0; color:#0b4fd9; font-weight:700; }
        h3{ font-size:22px; margin:14px 0 8px 0; color:var(--text); font-weight:600; }

        /* Labels & form text (readable, consistent) */
        label{ display:block; font-size:16px; color:var(--muted); font-weight:600; margin-bottom:8px; }

        /* Inputs & textareas */
        input[type="text"], input[type="password"], textarea, select{
            width:100%;
            background: #fff;
            border:1px solid var(--card-border);
            border-radius:8px;
            padding:10px 12px;
            font-size:16px;
            color:var(--text);
            transition:box-shadow .12s ease, border-color .12s ease;
        }
        textarea{ min-height:140px; }
        input:focus, textarea:focus, select:focus{
            outline:none;
            border-color:var(--primary);
            box-shadow:0 6px 18px rgba(11,99,255,0.08);
        }

        /* Buttons - high contrast, prominent */
        button, [role="button"]{
            display:inline-flex; align-items:center; justify-content:center;
            gap:8px;
            padding:10px 16px;
            border-radius:10px;
            border:none;
            cursor:pointer;
            font-weight:700;
            font-size:16px;
            color:#fff;
            background:linear-gradient(90deg,var(--primary),#1450d7);
            box-shadow:var(--shadow-sm);
            transition:transform .14s ease, box-shadow .14s ease, opacity .14s ease;
        }
        button:hover,[role="button"]:hover{ transform:translateY(-3px); box-shadow:var(--shadow-md); }
        button:active,[role="button"]:active{ transform:translateY(0); }
        button:focus{ outline:3px solid rgba(11,99,255,0.14); }

        /* Emphasize primary submit with accent option class (optional) */
        .btn-accent{ background: linear-gradient(90deg,var(--accent),#ff4e4e); }

        /* Alerts */
        [data-testid="stAlert"], .stInfo{ padding:12px; border-radius:10px; background:var(--surface); border-left:4px solid var(--primary); color:var(--text); }
        [data-testid="stAlert"][kind="success"]{ border-left-color: #16a34a; background:#f6fbf6; }

        /* Sidebar - light, airy */
        [data-testid="stSidebar"]{ background: linear-gradient(180deg,#f6fbff,#f0f9ff); border-right:1px solid var(--card-border); padding:18px; }
        [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2{ color:var(--primary); }

        /* Expander & cards */
        [data-testid="stExpander"], .stCard{ background:var(--surface); border:1px solid var(--card-border); border-radius:10px; padding:12px; }

        /* Code & pre blocks - readable and distinct */
        code{ background:#eef2ff; color:#0b3a8b; padding:0.15rem 0.4rem; border-radius:6px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace; font-size:15px; }
        pre{ background:var(--code-bg); color:#e6eefc; padding:12px; border-radius:10px; overflow:auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace; font-size:15px; }

        /* HR decorative */
        hr{ height:2px; border:none; background:linear-gradient(to right, transparent, rgba(11,99,255,0.18), transparent); margin:18px 0; }

        /* Small text */
        small, .stCaption{ color:var(--muted); font-size:15px; }

        /* Download button spacing */
        [data-testid="stDownloadButton"]{ margin:8px 0; }

        /* Select icon polish */
        select{ appearance:none; background-image:none; padding-right:14px; }

        /* Checkbox and radio */
        input[type="checkbox"], input[type="radio"]{ width:18px; height:18px; accent-color:var(--primary); }

        /* Responsive tweaks */
        @media (max-width:768px){
            .main{ padding:14px; }
            h1{ font-size:20px; }
        }
    </style>
    """
