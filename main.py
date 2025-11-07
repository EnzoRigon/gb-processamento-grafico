import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tempfile
import os
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from apply_filters import filters
import uuid
from pathlib import Path
import av
from aiortc.contrib.media import MediaRecorder
from util import delete_folder_files

st.title("Demo de Filtros em Foto e Vídeo com OpenCV")

tab1, tab2, tab3 = st.tabs(["Foto", "Upload", "Vídeo"])

# --- Aba Foto ---
with tab1:
    st.header("Foto")
    img_file = st.camera_input("Tire uma foto")
    if img_file is not None:
        img = Image.open(img_file)
        img_np = np.array(img)
        if img_np.shape[2] == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
        else:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        filters_list = [""] + list(filters.keys())
        filtro = st.selectbox("Escolha um filtro", filters_list)
        if filtro != "":
            st.markdown(f"**Descrição do filtro:** {filters[filtro]['desc']}")
            img_filtrada = filters[filtro]["func"](img_np)
            if len(img_filtrada.shape) == 2:
                img_filtrada = cv2.cvtColor(img_filtrada, cv2.COLOR_GRAY2BGR)
            st.image(cv2.cvtColor(img_filtrada, cv2.COLOR_BGR2RGB), caption=f"Foto com filtro: {filtro}")
            img_bytes = cv2.imencode('.png', img_filtrada)[1].tobytes()
            st.download_button("Salvar imagem filtrada", img_bytes, file_name="imagem_filtrada.png", mime="image/png", key="save_foto_filtrada")
        else:
            st.image(img, caption="Foto original")
            img_bytes = cv2.imencode('.png', img_np)[1].tobytes()
            st.download_button("Salvar imagem original", img_bytes, file_name="imagem_original.png", mime="image/png", key="save_foto_original")

# --- Aba Upload (Foto) ---
with tab2:
    st.header("Upload de Foto")
    upload_file = st.file_uploader("Faça upload de uma foto (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
    if upload_file is not None:
        file_type = upload_file.type
        if file_type.startswith("image"):
            img = Image.open(upload_file)
            img_np = np.array(img)
            if img_np.shape[2] == 4:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
            else:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            filters_list_upload = [""] + list(filters.keys())
            filtro_upload = st.selectbox("Escolha um filtro para a imagem", filters_list_upload, key="upload_filtro_img")
            if filtro_upload != "":
                st.markdown(f"**Descrição do filtro:** {filters[filtro_upload]['desc']}")
                img_filtrada = filters[filtro_upload]["func"](img_np)
                if len(img_filtrada.shape) == 2:
                    img_filtrada = cv2.cvtColor(img_filtrada, cv2.COLOR_GRAY2BGR)
                st.image(cv2.cvtColor(img_filtrada, cv2.COLOR_BGR2RGB), caption=f"Imagem com filtro: {filtro_upload}")
                img_bytes = cv2.imencode('.png', img_filtrada)[1].tobytes()
                st.download_button("Salvar imagem filtrada", img_bytes, file_name="imagem_filtrada.png", mime="image/png", key="save_upload_filtrada")
            else:
                st.image(img, caption="Imagem original")
                img_bytes = cv2.imencode('.png', img_np)[1].tobytes()
                st.download_button("Salvar imagem original", img_bytes, file_name="imagem_original.png", mime="image/png", key="save_upload_original")
        elif file_type.startswith("video"):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(upload_file.read())
            temp_video_path = tfile.name
            st.video(temp_video_path)

            filters_list_upload = [""] + list(filters.keys())
            filtro_upload = st.selectbox("Escolha um filtro para o vídeo", filters_list_upload, key="upload_filtro_vid")
            if filtro_upload != "":
                st.markdown(f"**Descrição do filtro:** {filters[filtro_upload]['desc']}")
                st.write("Processando vídeo, aguarde...")
                cap = cv2.VideoCapture(temp_video_path)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out_path = temp_video_path + "_filtered.mp4"
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_filt = filters[filtro_upload]["func"](frame)
                    if len(frame_filt.shape) == 2:
                        frame_filt = cv2.cvtColor(frame_filt, cv2.COLOR_GRAY2BGR)
                    out.write(frame_filt)
                cap.release()
                out.release()
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button("Salvar vídeo filtrado", f, file_name="video_filtrado.mp4", mime="video/mp4", key="save_upload_video_filtrado")
                os.remove(out_path)
            else:
                st.info("Selecione um filtro para aplicar ao vídeo.")
            os.remove(temp_video_path)
        else:
            st.error("Tipo de arquivo não suportado.")


# --- Aba Vídeo (streamlit-webrtc) ---
with tab3:
    import subprocess
    def convert_to_h264(input_path, output_path):
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path), "-c:v", "libx264", "-c:a", "aac", str(output_path)
        ]
        try:
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            st.error(f"Erro ao converter vídeo: {e}")
            return False
    st.header("Gravar vídeo da webcam (filtros em tempo real)")
    st.write("Grave um vídeo, aplique filtro em tempo real e salve o vídeo original e filtrado.")
    filter_options = [""] + list(filters.keys())
    selected_filter = st.selectbox("Escolha um filtro para o vídeo", filter_options, key="webrtc_filtro_vid")
    st.markdown(f"**Descrição do filtro:** {filters[selected_filter]['desc']}" if selected_filter else "")

    RECORD_DIR = Path("./records")
    RECORD_DIR.mkdir(exist_ok=True)

    if "prefix_video" not in st.session_state:
        st.session_state["prefix_video"] = str(uuid.uuid4())
    prefix = st.session_state["prefix_video"]
    in_file = RECORD_DIR / f"{prefix}_input.mp4"
    out_file = RECORD_DIR / f"{prefix}_output.mp4"

    def in_recorder_factory():
        return MediaRecorder(str(in_file), format="mp4")

    def out_recorder_factory():
        return MediaRecorder(str(out_file), format="mp4")

    def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        if selected_filter and selected_filter in filters:
            img = filters[selected_filter]["func"](img)
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    ctx_video = webrtc_streamer(
        key="video",
        mode=WebRtcMode.SENDRECV,
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=video_frame_callback,
        in_recorder_factory=in_recorder_factory,
        out_recorder_factory=out_recorder_factory,
    )
    if in_file.exists():
        h264_input_path = in_file.parent / f"{prefix}_input.mp4"
        if not h264_input_path.exists():
            if convert_to_h264(in_file, h264_input_path):
                st.success("Vídeo pronto para download!")
            else:
                st.error("Falha ao converter o vídeo.")
        if h264_input_path.exists():
            with h264_input_path.open("rb") as f:
                st.download_button(
                    "Download do vídeo", f, "input.mp4", key="download_input_h264_video_tab3", mime="video/mp4"
                )
            delete_folder_files(RECORD_DIR)

    if out_file.exists():
        h264_output_path = out_file.parent / f"{prefix}_output_h264.mp4"
        if not h264_output_path.exists():
            if convert_to_h264(out_file, h264_output_path):
                st.success("Vídeo pronto para download!")
            else:
                st.error("Falha ao converter o vídeo.")
        if h264_output_path.exists():
            with h264_output_path.open("rb") as f:
                st.download_button(
                    "Download do vídeo", f, "output.mp4", key="download_output_h264_video_tab3", mime="video/mp4"
                )
                delete_folder_files(RECORD_DIR)