# view_model.py
from flask import Flask, render_template_string, request
import os
import requests

app = Flask(__name__)

HTML_FORM = '''
<html>
<head>
    <title>3D Roof with Solar Panels</title>
</head>
<body>
    <h2>Generate Roof + Solar Panels</h2>
    <form id="inputForm" method="post" enctype="multipart/form-data">
        Roof Length (m): <input type="number" name="roof_length" step="0.1" required><br>
        Roof Width (m): <input type="number" name="roof_width" step="0.1" required><br>
        Number of Panels: <input type="number" name="num_panels" required><br>
        Tilt Angle (deg): <input type="number" name="tilt_angle" step="0.1" required><br>
        <input type="submit" value="Generate 3D Model">
    </form>
    {% if show_viewer %}
        <h3>3D Model:</h3>
        {{ fig|safe }}
    {% endif %}
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
                    aspectmode='data'
                ),
                title='3D Roof with Solar Panels'
            )
            fig_html = fig.to_html(full_html=False)
        else:
            fig_html = "<p style='color:red;'>Failed to generate model.</p>"

    return render_template_string(HTML_FORM, show_viewer=show_viewer, fig=fig_html)

if __name__ == '__main__':
    print("🚀 Flask server running at: http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)
