import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tempfile
import os

from apply_filters import filters

st.title("Demo de Filtros em Foto e Vídeo com OpenCV")

tab1, tab2 = st.tabs(["Foto", "Upload"])

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
            img_filtrada = filters[filtro](img_np)
            if len(img_filtrada.shape) == 2:
                img_filtrada = cv2.cvtColor(img_filtrada, cv2.COLOR_GRAY2BGR)
            st.image(cv2.cvtColor(img_filtrada, cv2.COLOR_BGR2RGB), caption=f"Foto com filtro: {filtro}")
            # Botão para salvar a imagem filtrada
            img_bytes = cv2.imencode('.png', img_filtrada)[1].tobytes()
            st.download_button("Salvar imagem filtrada", img_bytes, file_name="imagem_filtrada.png", mime="image/png")
        else:
            st.image(img, caption="Foto original")
            # Botão para salvar a imagem original
            img_bytes = cv2.imencode('.png', img_np)[1].tobytes()
            st.download_button("Salvar imagem original", img_bytes, file_name="imagem_original.png", mime="image/png")

# --- Aba Upload (Foto ou Vídeo) ---
with tab2:
    st.header("Upload de Foto ou Vídeo")
    upload_file = st.file_uploader("Faça upload de uma foto (.png, .jpg, .jpeg) ou vídeo (.mp4, .avi, .mov)", type=["png", "jpg", "jpeg", "mp4", "avi", "mov"])
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
                img_filtrada = filters[filtro_upload](img_np)
                if len(img_filtrada.shape) == 2:
                    img_filtrada = cv2.cvtColor(img_filtrada, cv2.COLOR_GRAY2BGR)
                st.image(cv2.cvtColor(img_filtrada, cv2.COLOR_BGR2RGB), caption=f"Imagem com filtro: {filtro_upload}")
                img_bytes = cv2.imencode('.png', img_filtrada)[1].tobytes()
                st.download_button("Salvar imagem filtrada", img_bytes, file_name="imagem_filtrada.png", mime="image/png")
            else:
                st.image(img, caption="Imagem original")
                img_bytes = cv2.imencode('.png', img_np)[1].tobytes()
                st.download_button("Salvar imagem original", img_bytes, file_name="imagem_original.png", mime="image/png")
        elif file_type.startswith("video"):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(upload_file.read())
            temp_video_path = tfile.name
            st.video(temp_video_path)

            filters_list_upload = [""] + list(filters.keys())
            filtro_upload = st.selectbox("Escolha um filtro para o vídeo", filters_list_upload, key="upload_filtro_vid")
            if filtro_upload != "":
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
                    frame_filt = filters[filtro_upload](frame)
                    if len(frame_filt.shape) == 2:
                        frame_filt = cv2.cvtColor(frame_filt, cv2.COLOR_GRAY2BGR)
                    out.write(frame_filt)
                cap.release()
                out.release()
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button("Salvar vídeo filtrado", f, file_name="video_filtrado.mp4", mime="video/mp4")
                os.remove(out_path)
            else:
                st.info("Selecione um filtro para aplicar ao vídeo.")
            os.remove(temp_video_path)
        else:
            st.error("Tipo de arquivo não suportado.")