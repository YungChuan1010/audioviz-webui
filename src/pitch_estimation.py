import librosa
from librosa import display
from librosa import feature

import numpy as np
from matplotlib import pyplot as plt
import scipy

from numpy import typing as npt
import typing


def plot_mel_spectrogram(
        y: npt.ArrayLike, 
        sr:int, 
        shift_array: npt.ArrayLike,
        with_pitch : bool = True,
    ):

    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_dB = librosa.power_to_db(S, ref=np.max)

    if with_pitch :
        
        f0, voiced_flag, voiced_probs = librosa.pyin(y,
                                                     fmin=librosa.note_to_hz('C2'),
                                                     fmax=librosa.note_to_hz('C7'))
        times = librosa.times_like(f0, sr)
        
        fig, ax = plt.subplots(figsize=(12,6))
        img = librosa.display.specshow(S_dB, x_axis='time',
                                       y_axis='mel', sr=sr, 
                                       fmax=8000, ax=ax)
        ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
        ax.set_xticks(shift_array - shift_array[0],
                      shift_array)
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.legend(loc='upper right')
        ax.set(title='Mel-frequency spectrogram')


    else :
        fig, ax = plt.subplots(figsize=(12,6))
        img = librosa.display.specshow(S_dB, x_axis='time',
                                       y_axis='mel', sr=sr, 
                                       fmax=8000, ax=ax)
        ax.set_xticks(shift_array - shift_array[0],
                      shift_array)
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.set(title='Mel-frequency spectrogram')
    
    return fig, ax


def plot_constant_q_transform(y: npt.ArrayLike, sr:int,
                              shift_array: npt.ArrayLike
    ) :

    C = np.abs(librosa.cqt(y, sr=sr))
    fig, ax = plt.subplots(figsize=(12,6))
    img = librosa.display.specshow(librosa.amplitude_to_db(C, ref=np.max),
                                   sr=sr, x_axis='time', y_axis='cqt_note', ax=ax)
    ax.set_xticks(shift_array - shift_array[0],
                      shift_array)
    ax.set_title('Constant-Q power spectrum')
    fig.colorbar(img, ax=ax, format="%+2.0f dB")

    return fig, ax


def pitch_class_type_one_vis(y: npt.ArrayLike, sr: int) -> None :

    S = np.abs(librosa.stft(y))
    chroma = librosa.feature.chroma_stft(S=S, sr=sr)

    count_pitch = np.empty(np.shape(chroma)) # To count pitch
    notes = np.array(librosa.key_to_notes('C:maj'))
    
    # Set the threshold to determine the exact pitch
    count_pitch[chroma < 0.5] = 0
    count_pitch[chroma > 0.5] = 1

    # To compute the probability
    occurProbs = np.empty(np.shape(count_pitch)[0])
    
    for i in range(np.shape(count_pitch)[0]) :
        total = np.sum(count_pitch)
        occurProbs[i] = np.sum(count_pitch[i]) / total

    result = np.vstack((notes, np.round(occurProbs, 4))).T

    ticks = range(12)
    fig, ax = plt.subplots()
    plt.title("Pitch Class")
    plt.bar(ticks,occurProbs * 100, align='center')
    plt.xticks(ticks, notes)
    plt.xlabel("Note")
    plt.ylabel("Number of occurrences %")

    return fig, ax, result
    
    
def pitch_class_histogram_chroma(y: npt.ArrayLike, sr: int, higher_resolution: bool, save_to_csv: bool = False) -> None :

    S = np.abs(librosa.stft(y))
    notes = np.array(librosa.key_to_notes('C:maj')) # For x-axis legend

    if not higher_resolution :

        chroma = librosa.feature.chroma_stft(S=S, sr=sr)
        valid_pitch = np.empty(np.shape(chroma)) # To count pitch
        valid_pitch[chroma < 0.7] = 0
        valid_pitch[chroma >= 0.7] = 1
        total = np.sum(valid_pitch)

        # To compute the probability
        # WARNING: (12,) means pure 1-D array
        occurProbs = np.empty((12,))
        for i in range(0, 12) :
            occurProbs[i] = np.sum(valid_pitch[i]) / total

        ticks = range(12)
        colors = ['lightcoral', 'goldenrod', 'lightseagreen', 'indigo', 'lightcoral', 
                 'goldenrod', 'lightseagreen', 'indigo', 'lightcoral', 'goldenrod', 
                 'lightseagreen', 'indigo']
        xLegend = notes

        fig, ax = plt.subplots()
        ax.bar(ticks,occurProbs * 100, align='center', color=colors)
        ax.set_xticks(ticks)
        ax.set_xticklabels(xLegend)
        ax.set_title("Pitch Class Histogram")
        ax.set_xlabel("Note")
        ax.set_ylabel("Occurrences %")
    
    if higher_resolution :

        chroma = librosa.feature.chroma_stft(S=S, sr=sr, n_chroma=120)
        valid_pitch = np.empty(np.shape(chroma)) # To count pitch
        valid_pitch[chroma < 0.7] = 0
        valid_pitch[chroma >= 0.7] = 1
        total = np.sum(valid_pitch)

        occurProbs = np.empty((120,))
        for i in range(0, 120) :
            occurProbs[i] = np.sum(valid_pitch[i]) / total
        
        ticks = range(120)
        fig, ax = plt.subplots()
        xLegend = list()
        for i in range(120) :
            if i % 10 == 0 :
                xLegend.append(notes[i // 10])
            else :
                xLegend.append('')

        colors = list()
        
        for i in range(120) :
            if i % 40 >=0 and i % 40 < 10 : colors.append('lightcoral')
            elif i % 40 >= 10 and i % 40 < 20 : colors.append('goldenrod')
            elif i % 40 >= 10 and i % 40 < 30 : colors.append('lightseagreen')
            elif i % 40 >= 10 and i % 40 < 40 : colors.append('indigo')

        fig, ax = plt.subplots()
        ax.bar(ticks,occurProbs * 100, align='center', color = colors)
        ax.set_xticks(ticks)
        ax.set_xticklabels(xLegend)
        ax.set_title("Pitch Class Histogram")
        ax.set_xlabel("Note")
        ax.set_ylabel("Occurrence %")

    result = np.vstack((xLegend, np.round(occurProbs, 4))).T
    if save_to_csv :
        with open('pitch_class.csv', 'w') as out :
            for row in result :
                print(*row, sep=',', file=out) 
                
    return fig, ax, result