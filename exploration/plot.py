import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CandlePlot:
    def __init__(self, df, plot_candles=True) -> None:
        self.df_plot = df.copy()
        self.plot_candles = plot_candles
        self.create_candle_fig()
    
    def add_timestr(self):
        self.df_plot['sTime'] = [dt.datetime.strftime(x, "%Y-%m-%d %H:%M") for x in self.df_plot.time]

    def create_candle_fig(self):
        self.add_timestr()
        self.fig = make_subplots(specs=[[{"secondary_y": True}]])
        if self.plot_candles:
            self.fig.add_trace(go.Candlestick(
                x = self.df_plot.sTime,
                open= self.df_plot.mid_o,
                low= self.df_plot.mid_l,
                high= self.df_plot.mid_h,
                close= self.df_plot.mid_c,
            ))

        self.fig.update_layout(xaxis=dict(type="category"), yaxis=dict(autorange = True, fixedrange= False))
        self.fig.update_xaxes(
            nticks=5
        )  

    def add_traces(self, line_traces, is_secondary=False):
        for line_trace in line_traces:
            self.fig.add_trace(go.Scatter(
            x=self.df_plot.sTime,
            y=self.df_plot[line_trace],
            line=dict(width=2),
            line_shape="spline",
            name=line_trace
        ), secondary_y=is_secondary)

    def show_plot(self, line_traces=[], secondary_traces=[]):
        self.add_traces(line_traces)
        self.add_traces(secondary_traces, is_secondary=True)
        self.fig.show()