import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import io
import base64
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

def interactive_graphic():
    # Define the data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Get the slider value from the request object
    freq = float(request.args.get('freq', 1.0))

    # Create the plot
    fig, ax = plt.subplots()
    line, = ax.plot(x, np.sin(freq * x))

    # Add interactivity
    def update(val):
        print('update called')
        # Get the slider value
        freq = s_freq.val
        
        # Update the plot
        line.set_ydata(np.sin(freq * x))
        fig.canvas.draw_idle()

    # Create a slider
    ax_freq = plt.axes([0.1, 0.1, 0.8, 0.05])
    s_freq = Slider(ax_freq, 'Frequency', 0.1, 10.0, valinit=freq)
    s_freq.on_changed(update)


    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(x, y)

    # Convert the plot to an image
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    
    # Generate the HTML code for the plot
    html = f'<img id="plot" src="send_file(buffer, mimetype=''image/png'')" />'
    print(f'freq = {freq}')

    # Render the template with the HTML code for the plot
    return render_template('interactive-graphic.html', html=html)

def plot_im(freq):
    # Define the data
    x = np.linspace(0, 10, 100)
    y = np.sin(freq * x)

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(x, y)

    # Convert the plot to an image
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    # Return the image as a response
    return send_file(buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
