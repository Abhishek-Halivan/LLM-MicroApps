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
        /* Root variables and base styles */
        :root {
            --primary-color: #2563eb;
            --secondary-color: #f97316;
            --success-color: #16a34a;
            --danger-color: #dc2626;
            --text-dark: #1f2937;
            --text-light: #f9fafb;
            --bg-light: #ffffff;
            --bg-lighter: #f9fafb;
            --bg-card: #f3f4f6;
            --border-radius: 8px;
            --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        /* Overall body and main content */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text-dark);
            background-color: var(--bg-lighter);
            line-height: 1.6;
        }

        /* Main container */
        .main {
            background-color: var(--bg-lighter);
            padding: 2rem;
        }

        /* Headers and titles */
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color);
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }

        h1 {
            font-size: 2.5rem;
            border-bottom: 3px solid var(--secondary-color);
            padding-bottom: 0.5rem;
        }

        h2 {
            font-size: 2rem;
            margin-top: 2rem;
        }

        h3, h4 {
            font-size: 1.3rem;
        }

        /* Labels and form text */
        label {
            color: var(--text-dark);
            font-weight: 500;
            font-size: 1rem;
            display: block;
            margin-bottom: 0.5rem;
        }

        /* Text areas and inputs */
        textarea, input[type="text"], input[type="password"], select {
            background-color: white;
            border: 2px solid #ddd;
            border-radius: var(--border-radius);
            padding: 0.75rem;
            font-size: 1rem;
            color: var(--text-dark);
            font-family: inherit;
        }

        textarea:focus, input:focus, select:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 8px rgba(31, 119, 180, 0.2);
        }

        /* Buttons */
        button, [role="button"] {
            background-color: var(--primary-color);
            color: white;
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.18s ease;
            box-shadow: var(--shadow);
            text-shadow: 0 1px 1px rgba(0,0,0,0.18);
        }

        button:hover, [role="button"]:hover {
            background-color: #1d4ed8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        button:active, [role="button"]:active {
            transform: translateY(0);
        }

        /* Primary button style (Submit) */
        [kind="primary"] {
            background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
        }

        [kind="primary"]:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
        }

        /* Info boxes */
        .stInfo, [data-testid="stAlert"] {
            background-color: #eff6ff;
            border-left: 4px solid var(--primary-color);
            border-radius: var(--border-radius);
            padding: 1rem;
            margin: 1rem 0;
            color: var(--text-dark);
        }

        /* Success boxes */
        .stSuccess, [data-testid="stAlert"][kind="success"] {
            background-color: #f0fdf4;
            border-left: 4px solid var(--success-color);
            color: #166534;
        }

        /* Warning boxes */
        .stWarning, [data-testid="stAlert"][kind="warning"] {
            background-color: #fefce8;
            border-left: 4px solid var(--secondary-color);
            color: #92400e;
        }

        /* Error boxes */
        .stError, [data-testid="stAlert"][kind="error"] {
            background-color: #fef2f2;
            border-left: 4px solid var(--danger-color);
            color: #991b1b;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f0f9ff;
            padding: 1.5rem 1rem;
            border-right: 1px solid #e0e7ff;
        }

        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--primary-color);
            margin-top: 1rem;
        }

        [data-testid="stSidebar"] label {
            color: var(--text-dark);
        }

        /* Expanders */
        [data-testid="stExpander"] {
            border: 1px solid #e5e7eb;
            border-radius: var(--border-radius);
            background-color: var(--bg-light);
        }

        [data-testid="stExpander"] > div:first-child {
            background-color: var(--bg-card);
            border-radius: var(--border-radius);
        }

        /* Columns and containers */
        .stColumns {
            gap: 1rem;
        }

        /* Text styling for better readability */
        p {
            font-size: 1rem;
            line-height: 1.8;
            color: var(--text-dark);
            margin-bottom: 1rem;
        }

        /* Code blocks */
        code {
            background-color: var(--bg-card);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            color: #d946ef;
            font-family: 'Courier New', monospace;
        }

        pre {
            background-color: #1f2937;
            color: #f3f4f6;
            padding: 1rem;
            border-radius: var(--border-radius);
            overflow-x: auto;
            font-size: 0.9rem;
        }

        /* Divider/Markdown HR */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, var(--primary-color), transparent);
            margin: 2rem 0;
        }

        /* Caption and small text */
        .stCaption, small {
            color: #666;
            font-size: 0.9rem;
        }

        /* Download buttons */
        [data-testid="stDownloadButton"] {
            margin: 0.5rem 0;
        }

        /* Selectbox and radio styling */
        select {
            appearance: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 0.75rem center;
            background-size: 1.5rem;
            padding-right: 2.5rem;
        }

        /* Checkbox and Radio styling */
        input[type="checkbox"], input[type="radio"] {
            width: 1.2rem;
            height: 1.2rem;
            cursor: pointer;
            accent-color: var(--primary-color);
        }

        /* Responsive design */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8rem;
            }
            h2 {
                font-size: 1.5rem;
            }
            .main {
                padding: 1rem;
            }
        }
    </style>
    """
