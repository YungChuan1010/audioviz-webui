import librosa
from librosa import display
from librosa import feature

import numpy as np
from matplotlib import pyplot as plt
import scipy

from numpy import typing as npt
import typing

import plotly.graph_objects as go
import streamlit as st 

def plot_waveform(
    x: npt.ArrayLike, 
    y: npt.ArrayLike, 
    shift_time: float = 0.0, 
    use_plotly=False
) -> typing.Tuple[plt.Figure, plt.Axes]:
    """
    Plots a waveform graph.

    Parameters
    ----------
    x : array-like
        The x-coordinates of the waveform data.
    y : array-like
        The y-coordinates of the waveform data.
    shift_time : float, optional
        A time shift to apply to the waveform, in seconds (default 0.0).
    use_plotly : bool, optional
        Whether to use Plotly to plot the waveform (default False).

    Returns
    -------
    fig : matplotlib.figure.Figure or plotly.graph_objs._figure.Figure
        The generated figure object.
    ax : matplotlib.axes.Axes or None
        The generated axes object. If `use_plotly` is True, this value will be None.
    """
    if use_plotly:
        fig = go.Figure(data=go.Scatter(x=x + shift_time, y=y))
        ax = None
        fig.update_layout(
            title="Waveform",
            xaxis_title="Time(s)",
            yaxis_title="Amplitude",
        )
    else:
        fig, ax = plt.subplots()
        ax.plot(x + shift_time, y)
        ax.set_xlabel("Time(s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Waveform")
        
    return fig, ax


def plot_spectrogram(
    y: npt.ArrayLike, 
    sr: int, 
    shift_time: float = 0.0, 
    shift_array: npt.ArrayLike = np.array([], dtype=np.float32),
    use_plotly=False
) -> typing.Tuple[plt.Figure, plt.Axes]:
    """
    Plots a Spectrogram graph.

    Parameters
    ----------
    y : array-like
        The waveform data.
    sr : int
        The sample rate of the waveform data.
    shift_time : float, optional
        A time shift to apply to the spectrogram, in seconds (default 0.0).
    use_plotly : bool, optional
        Whether to use Plotly to plot the spectrogram (default False).

    Returns
    -------
    fig : matplotlib.figure.Figure or plotly.graph_objs._figure.Figure
        The generated figure object.
    ax : matplotlib.axes.Axes or None
        The generated axes object. If `use_plotly` is True, this value will be None.
    """
    if use_plotly:
        fig = go.Figure()
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=2048)
        fig.add_trace(
            go.Heatmap(
                z=librosa.amplitude_to_db(
                    np.abs(librosa.stft(y)), ref=np.max
                ),
                x=np.arange(len(y)) / sr + shift_time,
                y=frequencies,
                colorscale="Viridis",
            )
        )
        ax = None
        fig.update_layout(
            title="Spectrogram",
            xaxis_title="Time(s)",
            yaxis_title="Frequency(Hz)",
            yaxis=dict(range=[0, 10000]),
        )
    else:
        fig, ax = plt.subplots()
        D = librosa.amplitude_to_db(
            np.abs(librosa.stft(y)), ref=np.max
        )
        img = librosa.display.specshow(
            D, x_axis="time", y_axis="log", sr=sr, ax=ax
        )
        fig.colorbar(img, ax=ax, format="%+2.0f dB")
        ax.set_title("Spectrogram")
        ax.set_xlabel("Time(s)")
        ax.set_ylabel("Frequency(Hz)")
        if shift_array.size > 0:
            ax.set_xticks(shift_array - shift_array[0],
                         shift_array)
            ax.autoscale()
    return fig, ax

def signal_RMS_analysis(
    y: npt.ArrayLike, 
    shift_time: float = 0.0,
    use_plotly=False
) -> typing.Tuple[plt.Figure, plt.Axes, npt.ArrayLike, npt.ArrayLike]:
    """
    Computes the Root Mean Square (RMS) of a given audio signal and plots the result.

    Parameters
    ----------
    y : npt.ArrayLike
        The audio signal as a 1-dimensional NumPy array or array-like object.
    shift_time : float, optional
        Time shift in seconds to apply to the plot (default 0.0).
    use_plotly : bool, optional
        Whether to use Plotly for plotting (True) or Matplotlib (False) (default False).

    Returns
    -------
    Tuple[plt.Figure, Union[plt.Axes, None], npt.ArrayLike, npt.ArrayLike]
        A tuple containing:
            - fig : plt.Figure or go.Figure
                The plot figure object (either a Matplotlib or Plotly figure object).
            - ax : plt.Axes or None
                The plot axes object (only for Matplotlib) or None if `use_plotly` is True.
            - times : npt.ArrayLike
                A 1-dimensional NumPy array of the times (in seconds) at which the RMS was computed.
            - rms : npt.ArrayLike
                A 1-dimensional NumPy array containing the RMS values for each window.

    Raises
    ------
    TypeError
        If the input signal is not a 1-dimensional NumPy array or array-like object.

    Examples
    --------
    # Compute the RMS and plot the result using Matplotlib
    y, sr = librosa.load('audio_file.wav')
    fig, ax, times, rms = signal_RMS_analysis(y, use_plotly=False)
    plt.show()
    """
    rms = librosa.feature.rms(y = y)
    times = librosa.times_like(rms) + shift_time
    
    if use_plotly:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=rms[0]))
        ax = None
    else:
        fig, ax = plt.subplots()
        ax.plot(times, rms[0])
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('RMS')


    return fig, ax, times, rms