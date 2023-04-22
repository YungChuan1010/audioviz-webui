import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import librosa
import pandas as pd
from src.st_helper import convert_df, get_shift, update_sessions, warning_region
from src.basic_info import plot_waveform, signal_RMS_analysis, plot_spectrogram
from src.chord_recognition import (
    plot_chord_recognition,
    plot_binary_template_chord_recognition,
    chord_table,
    compute_chromagram,
    chord_recognition_template,
    plot_chord,
    plot_user_chord
)
from src.beat_track import (
    onsets_detection,
    plot_bpm,
    onset_click_plot,
)

warning_region("This page is still under development, there may be errors or incomplete parts.")

#%% 除錯訊息
if st.session_state.debug:
    st.write(st.session_state)

#%% 上傳檔案區塊
with st.expander("上傳檔案(Upload Files)"):
    file = st.file_uploader("Upload your music library", type=["mp3", "wav", "ogg"])

    if file is not None:
        st.audio(file, format="audio/ogg")
        st.subheader("File information")
        st.write(f"File name: `{file.name}`", )
        st.session_state["file_name"] = file.name
        st.write(f"File type: `{file.type}`")
        st.write(f"File size: `{file.size}`")

        # 載入音檔
        y, sr = librosa.load(file, sr=22050)
        st.write(f"Sample rate: `{sr}`")
        duration = float(np.round(len(y)/sr-0.005, 2)) # 時間長度，取小數點後2位，向下取整避免超過音檔長度
        st.write(f"Duration(s): `{duration}`")
        y_all = y
        start_time = 0
        end_time = duration
        
#%% 更新session
update_sessions()
        
#%% 
if file is not None:
    
    # 片段模式 
    # use_segment = st.sidebar.checkbox("使用片段模式", value=st.session_state["use_segment"], key="segment")
    # st.session_state["use_segment"] = use_segment
    use_segment = st.session_state["use_segment"]
    
    if use_segment:
        # 若使用片段模式，則顯示選擇片段的起始時間與結束時間
        if st.session_state.first_run:
            start_time = st.sidebar.number_input("開始時間", value=0.0, min_value=0.0, max_value=duration, step=0.01)
            end_time = st.sidebar.number_input("結束時間", value=duration, min_value=0.0, max_value=duration, step=0.01)
            st.session_state.first_run = False
            st.session_state.start_time = start_time
            st.session_state.end_time = end_time
        else:
            start_time = st.sidebar.number_input("開始時間", value=st.session_state.start_time, min_value=0.0, max_value=duration, step=0.01)
            end_time = st.sidebar.number_input("結束時間", value=st.session_state.end_time, min_value=0.0, max_value=duration, step=0.01)
            st.session_state.start_time = start_time
            st.session_state.end_time = end_time

    else:
        start_time = 0.0
        end_index = duration
    # 根據選擇的聲音片段，取出聲音資料
    start_index = int(start_time*sr)
    end_index = int(end_time*sr)
    if end_index <= start_index:
        st.sidebar.warning("結束時間必須大於開始時間", icon="⚠️")

    y_sub = y_all[start_index:end_index]
    x_sub = np.arange(len(y_sub))/sr
    
    if use_segment: 
        with st.expander("聲音片段(Segment of the audio)"):
            st.write(f"Selected segment: `{start_time}` ~ `{end_time}`, duration: `{end_time-start_time}`")
            st.audio(y_sub, format="audio/ogg", sample_rate=sr)
    
    


#%% 功能分頁
if file is not None:
    
    shift_time, shift_array = get_shift(start_time, end_time) # shift_array為y_sub的時間刻度
    
    
    
    fig = plt.figure(
        figsize=(int(1.8*duration), 25),
    )
    
    ax1 = plt.subplot2grid((9, 1), (4, 0), rowspan=1)
    plot_waveform(x_sub, y_sub, shift_time=shift_time, use_plotly=False, ax=ax1)
    
    ax2 = plt.subplot2grid((9, 1), (2, 0), rowspan=2)
    plot_spectrogram(y_sub, sr, shift_time=shift_time, use_plotly=False, shift_array=shift_array, use_pitch_names=st.session_state["1-basic"]["use_pitch_name"], ax=ax2, show_colorbar=False)
    
    if not st.session_state["4-Chord"]["chord_df"]:
        chroma, _, _, _, duration = compute_chromagram(y_sub, sr)
        _, chord_max = chord_recognition_template(chroma, norm_sim='max')
        sec_per_frame = duration/chroma.shape[1]
        chord_results_df = pd.DataFrame({
            "Frame": np.arange(chroma.shape[1]),
            "Time(s)": np.arange(chroma.shape[1])*sec_per_frame + shift_time,
            "Chord": chord_table(chord_max)
        })
    else:
        chord_results_df = st.session_state["4-Chord"]["chord_df"]
    ax3 = plt.subplot2grid((9, 1), (0, 0), rowspan=2)
    plot_user_chord(chord_results_df, ax=ax3)
    
    ax4 = plt.subplot2grid((9, 1), (5, 0), rowspan=1)
    fig3_1a, ax3_1a, onset_data = onsets_detection(y_sub, sr, shift_array)
    o_env, o_times, onset_frames = onset_data
    if st.session_state["3-Time"]["onset_frames"] == []:
        st.session_state["3-Time"]["onset_frames"] = list(onset_frames)
    onset_click_plot(o_env, o_times, st.session_state["3-Time"]["onset_frames"], len(y_sub), sr, shift_time, ax=ax4)
    
    ax5 = plt.subplot2grid((9, 1), (6, 0), rowspan=1)
    plot_bpm(o_times[st.session_state["3-Time"]["onset_frames"]], shift_time, st.session_state["3-Time"]["onset_ma_window"], False, ax=ax5)
    
    # 增加ax間的間距
    fig.subplots_adjust(hspace=0.8)
    
    st.pyplot(fig)