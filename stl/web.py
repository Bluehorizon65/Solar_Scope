# view_model.py
from flask import Flask, render_template_string, request
import os
import requests

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>On karo Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 50%, #1e88e5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.8;
            color: #b0bec5;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 2rem;
            align-items: start;
        }
        
        .form-card {
            background: rgba(30, 30, 46, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .form-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: #e0e0e0;
            display: flex;
            align-items: center;
        }
        
        .form-title::before {
            content: "⚡";
            margin-right: 0.5rem;
            font-size: 1.8rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #b0bec5;
            font-size: 0.95rem;
        }
        
        .form-group input {
            width: 100%;
            padding: 1rem;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.05);
            color: #e0e0e0;
        }
        
        .form-group input::placeholder {
            color: #666;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #64b5f6;
            background: rgba(255,255,255,0.08);
            box-shadow: 0 0 0 3px rgba(100, 181, 246, 0.2);
        }
        
        .submit-btn {
            width: 100%;
            padding: 1.2rem;
            background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 50%, #1e88e5 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 20px rgba(30, 136, 229, 0.3);
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 25px rgba(30, 136, 229, 0.4);
        }
        
        .submit-btn:active {
            transform: translateY(0);
        }
        
        .viewer-card {
            background: rgba(30, 30, 46, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            min-height: 800px;
            display: flex;
            flex-direction: column;
        }
        
        .viewer-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: #e0e0e0;
            display: flex;
            align-items: center;
        }
        
        .viewer-title::before {
            content: "🏠";
            margin-right: 0.5rem;
            font-size: 1.8rem;
        }
        
        .placeholder {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            color: #666;
            border: 2px dashed rgba(255,255,255,0.2);
            border-radius: 12px;
            background: rgba(255,255,255,0.02);
        }
        
        .placeholder-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        .placeholder-text {
            font-size: 1.1rem;
            text-align: center;
            line-height: 1.5;
            color: #888;
        }
        
        .model-viewer {
            flex: 1;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            background: rgba(255,255,255,0.02);
            min-height: 700px;
        }
        
        .error-message {
            background: rgba(244, 67, 54, 0.1);
            border: 1px solid rgba(244, 67, 54, 0.3);
            color: #f44336;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 500;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #64b5f6;
            font-weight: 500;
        }
        
        .loading::after {
            content: "...";
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0%, 33% { content: "."; }
            34%, 66% { content: ".."; }
            67%, 100% { content: "..."; }
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 1rem;
            }
            
            .viewer-card {
                min-height: 600px;
            }
            
            .model-viewer {
                min-height: 500px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Generate Karlo</h1>
            <p>Abe Generate kar</p>
        </div>
        
        <div class="main-content">
            <div class="form-card">
                <h2 class="form-title">Values Enter Karo</h2>
                <form id="inputForm" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="roof_length">Roof Length (meters)</label>
                        <input type="number" id="roof_length" name="roof_length" step="0.1" required placeholder="e.g. 10.5">
                    </div>
                    
                    <div class="form-group">
                        <label for="roof_width">Roof Width (meters)</label>
                        <input type="number" id="roof_width" name="roof_width" step="0.1" required placeholder="e.g. 8.0">
                    </div>
                    
                    <div class="form-group">
                        <label for="num_panels">Number of Solar Panels</label>
                        <input type="number" id="num_panels" name="num_panels" required placeholder="e.g. 20">
                    </div>
                    
                    <div class="form-group">
                        <label for="tilt_angle">Panel Tilt Angle (degrees)</label>
                        <input type="number" id="tilt_angle" name="tilt_angle" step="0.1" required placeholder="e.g. 30">
                    </div>
                    
                    <button type="submit" class="submit-btn">Smash the Genrate Button</button>
                    <div class="loading" id="loading">Generating your model</div>
                </form>
            </div>
            
            <div class="viewer-card">
                <h2 class="viewer-title">Ye Raha 3D Model</h2>
                {% if show_viewer %}
                    <div class="model-viewer">
                        {{ fig|safe }}
                    </div>
                {% elif fig and 'color:red' in fig %}
                    <div class="error-message">
                        {{ fig|safe }}
                    </div>
                {% else %}
                    <div class="placeholder">
                        <div class="placeholder-icon">🏗️</div>
                        <div class="placeholder-text">
                            Configure your solar roof parameters<br>
                            and click "Generate 3D Model" to see<br>
                            your custom design visualization
                        </div>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('inputForm').addEventListener('submit', function() {
            document.querySelector('.submit-btn').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    show_viewer = False
    fig_html = ""
    if request.method == 'POST':
        roof_length = request.form['roof_length']
        roof_width = request.form['roof_width']
        num_panels = request.form['num_panels']
        tilt_angle = request.form['tilt_angle']

      
        api_url = "http://127.0.0.1:8000/generate-stl/"
        params = {
            "roof_length": roof_length,
            "roof_width": roof_width,
            "num_panels": num_panels,
            "tilt_angle": tilt_angle
        }
        r = requests.post(api_url, params=params)
        if r.status_code == 200:
            with open("downloaded_model.glb", "wb") as f:
                f.write(r.content)
            show_viewer = True

            import trimesh
            import plotly.graph_objects as go
            mesh = trimesh.load_mesh("downloaded_model.glb")
            vertices = mesh.vertices
            faces = mesh.faces
            if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
                vertex_colors = mesh.visual.vertex_colors
                colors = [f'rgb({c[0]},{c[1]},{c[2]})' for c in vertex_colors]
            else:
                colors = 'orange'
            fig = go.Figure(
                data=[
                    go.Mesh3d(
                        x=vertices[:, 0],
                        y=vertices[:, 1],
                        z=vertices[:, 2],
                        i=faces[:, 0],
                        j=faces[:, 1],
                        k=faces[:, 2],
                        vertexcolor=colors,
                        opacity=1.0
                    )
                ]
            )
            fig.update_layout(
                scene=dict(
                    xaxis_title='Length (X)',
                    yaxis_title='Width (Y)',
                    zaxis_title='Height (Z)',
                    aspectmode='data',
                    bgcolor='rgba(30,30,46,1)',
                    xaxis=dict(backgroundcolor='rgba(30,30,46,1)', gridcolor='rgba(255,255,255,0.1)', showbackground=True),
                    yaxis=dict(backgroundcolor='rgba(30,30,46,1)', gridcolor='rgba(255,255,255,0.1)', showbackground=True),
                    zaxis=dict(backgroundcolor='rgba(30,30,46,1)', gridcolor='rgba(255,255,255,0.1)', showbackground=True)
                ),
                title={
                    'text': 'Bathameez Dil bathameez Dil <br>Ye Model Hai Tera',
                    'font': {'color': '#e0e0e0'}
                },
                paper_bgcolor='rgba(30,30,46,1)',
                plot_bgcolor='rgba(30,30,46,1)',
                font=dict(color='#e0e0e0'),
                height=700,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            fig_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        else:
            fig_html = "<p style='color:#f44336;'>Failed to generate model.</p>"

    return render_template_string(HTML_FORM, show_viewer=show_viewer, fig=fig_html)

if __name__ == '__main__':
    print("🚀 Flask server running at: http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)