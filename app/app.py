import folium, io, sys, json, pickle, os

import plotly.express as px
import plotly

from folium.plugins import Draw
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

# help functions
import branca.colormap as cm

import matplotlib.pyplot as plt
from matplotlib import colors as colors
from helpers import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("DUW - Hittestressmonitoring APP"))
        self.setMinimumSize(1600, 1200)
        self.UI()
        self.Map()

    def UI(self):
        btn = QPushButton("Maak grafiek", self)
        btn.clicked.connect(self.onClick)
        btn.setFixedSize(120, 50)

        text = QLabel(
            "<B>DUW - Hittestressmonitor APP</B><BR>1. Teken een gebied in op de kaart [door op de vijfhoek te klikken of het vierkant]<BR>2. Klik op jouw ingetekende gebied [hierdoor sla je jouw ingetekende gebied op]<BR>3. Klik op OK<BR>4. Klik op Maak grafiek<BR>Bron; Landsat7 & 8"
        )

        self.view = QWebEngineView()
        self.view.setContentsMargins(20, 20, 20, 20)

        # central container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        lay = QHBoxLayout(central_widget)

        # menu container
        button_container = QWidget()
        vlay = QVBoxLayout(button_container)
        vlay.setSpacing(20)
        vlay.addStretch()
        vlay.addWidget(text)
        vlay.addWidget(btn)

        vlay.addStretch()
        lay.addWidget(button_container)
        lay.addWidget(self.view, stretch=1)

    def Map(self):
        array = getclasarray()
        colormap = getcolormap()
        bounds = getbounds()
        coordinate = [
            (bounds.bottom + bounds.top) / 2,
            (bounds.left + bounds.right) / 2,
        ]

        m = folium.Map(location=coordinate, zoom_start=13, tiles="CartoDB positron")

        folium.raster_layers.ImageOverlay(
            image=array,
            opacity=0.4,
            bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
            colormap=lambda value: mapvalue2color(value, colormap),
        ).add_to(m)
        m.add_child(colormap)

        # add draw component
        draw = Draw(
            draw_options={
                "polyline": False,
                "rectangle": True,
                "polygon": True,
                "circle": False,
                "marker": False,
                "circlemarker": False,
            },
            edit_options={"edit": False},
        )
        m.add_child(draw)

        # save map data to data object
        data = io.BytesIO()
        m.save(data, close_file=False)

        # set map to central widget, add listener to return drawn poly
        page = WebEnginePage(self.view)
        self.view.setPage(page)
        self.view.setHtml(data.getvalue().decode())

    def onClick(self):
        # click on button opens second window
        self.SW = SecondWindow()
        self.SW.resize(800, 600)
        self.SW.show()


class WebEnginePage(QWebEnginePage):
    # reads drawn shapes and saves them
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        coords_dict = json.loads(msg)
        coords = coords_dict["geometry"]["coordinates"][
            0
        ]  # extract the coordinates from the message
        with open(os.path.join("..", "data", "temp.pickle"), "wb") as outfile:
            pickle.dump(coords, outfile)


class SecondWindow(QMainWindow):
    # if second window opens make the graph
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.view = QWebEngineView()
        self.show_graph()
        self.setCentralWidget(self.view)

    def show_graph(self):
        df = plotframe()
        fig = px.scatter(
            df,
            color_discrete_sequence=["black"],
            trendline="ols",
            trendline_color_override="grey",
        ).update_traces(
            marker=dict(size=8),
        )
        fig.update_yaxes(range=[-5, 5], dtick=1).update_layout(
            title="oppervlaktetemperatuur over tijd voor laatst opgeslagen gebied",
            xaxis_title="datum",
            yaxis_title="std van gemiddelde",
            shapes=shapes(),
        )

        # set html to view
        self.view.setHtml(fig.to_html(include_plotlyjs="cdn"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MW = MainWindow()
    MW.resize(1200, 800)
    MW.show()
    sys.exit(app.exec_())
