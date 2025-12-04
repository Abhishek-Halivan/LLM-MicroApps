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
        /* Modern Color Palette */
        :root{
            --primary: #0f7fd9;      /* Deep professional blue */
            --primary-light: #5aabf0; /* Light accent blue */
            --accent: #ff6b6b;       /* Vibrant coral */
            --success: #10b981;      /* Emerald */
            --warning: #f59e0b;      /* Amber */
            --danger: #ef4444;       /* Red */
            --text-primary: #1a202c; /* Deep charcoal */
            --text-secondary: #718096; /* Muted gray */
            --bg-primary: #f5f5f0;   /* Warm bone gray */
            --bg-secondary: #efefea; /* Lighter bone gray */
            --card-bg: #ffffff;      /* Pure white for cards */
            --card-border: #e2e8f0;  /* Subtle border */
            --code-bg: #0f1724;      /* Dark code background */
            --radius: 12px;
            --radius-lg: 16px;
            --shadow-xs: 0 2px 6px rgba(15,127,217,0.05);
            --shadow-sm: 0 4px 12px rgba(15,127,217,0.1);
            --shadow-md: 0 8px 20px rgba(15,127,217,0.12);
            --shadow-lg: 0 12px 32px rgba(15,127,217,0.14);
            --transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Base layout & typography */
        html,body{
            height:100%;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color:var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            -webkit-font-smoothing:antialiased;
            -moz-osx-font-smoothing:grayscale;
            line-height:1.6;
            font-size:18px;
            letter-spacing: -0.3px;
        }

        /* Main container */
        .main{
            padding:32px 28px;
            max-width:1200px;
            margin:0 auto;
        }

        /* Heading styles with refined hierarchy */
        h1{
            font-size:36px;
            font-weight:800;
            color:var(--primary);
            margin:0 0 16px 0;
            letter-spacing: -1px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        h2{
            font-size:28px;
            font-weight:700;
            color:var(--primary);
            margin:24px 0 12px 0;
            letter-spacing: -0.5px;
        }

        h3{
            font-size:24px;
            font-weight:700;
            color:var(--text-primary);
            margin:16px 0 10px 0;
        }

        h4, h5, h6{
            font-size:18px;
            font-weight:600;
            color:var(--text-primary);
            margin:12px 0 8px 0;
        }

        p{
            font-size:16px;
            line-height:1.8;
            color:var(--text-secondary);
            margin:12px 0;
        }

        /* Labels with improved contrast */
        label{
            display:block;
            font-size:16px;
            color:var(--text-primary);
            font-weight:700;
            margin-bottom:10px;
            letter-spacing: -0.3px;
        }

        /* Form elements - refined */
        input[type="text"], input[type="password"], textarea, select{
            width:100%;
            background:#fff;
            border:2px solid var(--card-border);
            border-radius:var(--radius);
            padding:14px 16px;
            font-size:16px;
            color:var(--text-primary);
            transition:var(--transition);
            font-family:inherit;
        }

        textarea{
            min-height:160px;
            resize:vertical;
        }

        input[type="text"]::placeholder, textarea::placeholder{
            color:#bbb;
        }

        input:focus, textarea:focus, select:focus{
            outline:none;
            border-color:var(--primary);
            box-shadow:0 0 0 4px rgba(15,127,217,0.1);
            background:#fafbff;
        }

        /* Buttons - elevated & interactive */
        button, [role="button"]{
            display:inline-flex;
            align-items:center;
            justify-content:center;
            gap:10px;
            padding:14px 24px;
            border-radius:var(--radius);
            border:none;
            cursor:pointer;
            font-weight:700;
            font-size:16px;
            color:#fff;
            background:linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            box-shadow:var(--shadow-md);
            transition:var(--transition);
            letter-spacing: -0.3px;
        }

        button:hover, [role="button"]:hover{
            transform:translateY(-4px);
            box-shadow:var(--shadow-lg);
            background:linear-gradient(135deg, #0d6bc8 0%, #4a9de8 100%);
        }

        button:active, [role="button"]:active{
            transform:translateY(-2px);
            box-shadow:var(--shadow-sm);
        }

        button:focus{ outline:3px solid rgba(15,127,217,0.25); outline-offset:2px; }

        /* Alert messages - enhanced */
        [data-testid="stAlert"], .stInfo{
            padding:16px 18px;
            border-radius:var(--radius);
            border-left:5px solid var(--primary);
            background:linear-gradient(135deg, rgba(15,127,217,0.05) 0%, rgba(15,127,217,0.02) 100%);
            color:var(--text-primary);
            box-shadow:var(--shadow-xs);
            margin:12px 0;
        }

        [data-testid="stAlert"][kind="success"]{
            border-left-color:var(--success);
            background:linear-gradient(135deg, rgba(16,185,129,0.05) 0%, rgba(16,185,129,0.02) 100%);
        }

        [data-testid="stAlert"][kind="warning"]{
            border-left-color:var(--warning);
            background:linear-gradient(135deg, rgba(245,158,11,0.05) 0%, rgba(245,158,11,0.02) 100%);
        }

        [data-testid="stAlert"][kind="error"]{
            border-left-color:var(--danger);
            background:linear-gradient(135deg, rgba(239,68,68,0.05) 0%, rgba(239,68,68,0.02) 100%);
        }

        /* Sidebar - sophisticated */
        [data-testid="stSidebar"]{
            background:linear-gradient(180deg, rgba(15,127,217,0.02) 0%, rgba(15,127,217,0.01) 100%);
            border-right:1px solid var(--card-border);
            padding:24px 18px;
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
            color:var(--primary);
            font-weight:700;
        }

        [data-testid="stSidebar"] label{
            color:var(--text-primary);
            font-weight:600;
        }

        /* Expanders & cards */
        [data-testid="stExpander"]{
            background:var(--card-bg);
            border:1px solid var(--card-border);
            border-radius:var(--radius-lg);
            box-shadow:var(--shadow-xs);
            transition:var(--transition);
        }

        [data-testid="stExpander"]:hover{
            box-shadow:var(--shadow-sm);
            border-color:#d1d5db;
        }

        [data-testid="stExpander"] > div:first-child{
            background:linear-gradient(135deg, #fafbff 0%, #f5f7ff 100%);
            border-radius:var(--radius);
        }

        /* Code & pre blocks - syntax-ready */
        code{
            background:#f0f3ff;
            color:#0d47a1;
            padding:0.2rem 0.5rem;
            border-radius:6px;
            font-family: 'Fira Code', 'Monaco', 'Menlo', ui-monospace, monospace;
            font-size:15px;
            font-weight:500;
        }

        pre{
            background:var(--code-bg);
            color:#e6eefc;
            padding:16px;
            border-radius:var(--radius-lg);
            overflow:auto;
            font-family: 'Fira Code', 'Monaco', 'Menlo', ui-monospace, monospace;
            font-size:14px;
            border:1px solid rgba(15,127,217,0.1);
            box-shadow:var(--shadow-md);
        }

        pre::-webkit-scrollbar{
            height:8px;
        }

        pre::-webkit-scrollbar-track{
            background:#1a2332;
        }

        pre::-webkit-scrollbar-thumb{
            background:#0f63d9;
            border-radius:4px;
        }

        /* Decorative divider */
        hr{
            height:2px;
            border:none;
            background:linear-gradient(to right, transparent, rgba(15,127,217,0.2), transparent);
            margin:24px 0;
        }

        /* Caption & small text */
        small, .stCaption{
            color:var(--text-secondary);
            font-size:15px;
            font-weight:500;
        }

        /* Download buttons */
        [data-testid="stDownloadButton"]{
            margin:12px 0;
        }

        /* Select dropdowns */
        select{
            appearance:none;
            background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%230f7fd9' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat:no-repeat;
            background-position:right 12px center;
            background-size:12px;
            padding-right:36px;
        }

        /* Checkboxes & radios - polished */
        input[type="checkbox"], input[type="radio"]{
            width:20px;
            height:20px;
            cursor:pointer;
            accent-color:var(--primary);
            margin-right:8px;
        }

        /* Responsive design */
        @media (max-width:768px){
            .main{
                padding:16px 12px;
            }
            h1{
                font-size:28px;
            }
            h2{
                font-size:24px;
            }
            button, [role="button"]{
                padding:12px 20px;
                font-size:15px;
            }
        }

        /* Print styles */
        @media print{
            body{
                background:#fff;
            }
            [data-testid="stSidebar"]{
                display:none;
            }
        }
    </style>
    """