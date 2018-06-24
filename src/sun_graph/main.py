import plotly.plotly as py
import plotly.graph_objs as go

def main():
    py.plotly.tools.set_credentials_file(username='raccoonmaster', api_key='kZLKyYhOX6Mp4FwvcDCm')
    z1 = [
        [1,2,3],
        [1, 2, 3]

    ]

    x1 = [1,2,3,4]
    y1 = [1,2,3,4]


    data = [
        go.Surface(z=z1),
    ]

    py.iplot(data)


if __name__ == "__main__":
    main()