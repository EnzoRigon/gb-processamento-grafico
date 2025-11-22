import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from apply_filters import FILTERS, MATH_OPS
import uuid
from pathlib import Path
import av
from aiortc.contrib.media import MediaRecorder
from util import delete_folder_files

# Título principal do app
st.title("Demo de Filtros em Foto e Vídeo com OpenCV")

# Cria as abas principais do app
tab1, tab2, tab3 = st.tabs(["Foto", "Vídeo", "Operações Matemáticas"])

# --- Aba Foto ---
with tab1:
    st.header("Foto")
    from streamlit_image_coordinates import streamlit_image_coordinates

    # Lista de filtros disponíveis
    filters_list = [""] + list(FILTERS.keys())

    # Inicializa índice do filtro na sessão
    if "filtro_index" not in st.session_state:
        st.session_state["filtro_index"] = 0

    # Permite ao usuário escolher entre tirar foto ou fazer upload
    modo_foto = st.radio("Como deseja obter a foto?", ["Tirar Foto", "Upload"], key="modo_foto_tab1")
    img_file = None
    if modo_foto == "Tirar Foto":
        img_file = st.camera_input("Tire uma foto")
    elif modo_foto == "Upload":
        img_file = st.file_uploader("Faça upload de uma foto (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"], key="upload_tab1")

    # Processa a imagem se ela foi fornecida
    if img_file is not None:
        img = Image.open(img_file).convert("RGBA")
        max_dim = 800  # Limite máximo de dimensão da imagem
        # Redimensiona a imagem se for muito grande
        if img.width > max_dim or img.height > max_dim:
            scale = min(max_dim / img.width, max_dim / img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.LANCZOS)
        img_np = np.array(img)

        # Filtros
        if "filtro_key" not in st.session_state:
            st.session_state["filtro_key"] = 0
        # Selectbox para escolher filtro
        filtro = st.selectbox(
            "Escolha um filtro",
            filters_list,
            key="Escolha um filtro",
            index=st.session_state["filtro_index"]
        )
        # Aplica filtro se selecionado
        if filtro:
            st.markdown(f"**Descrição do filtro:** {FILTERS[filtro]['desc']}")
            img_filtrada = FILTERS[filtro]["func"](cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR))
            if len(img_filtrada.shape) == 2:
                img_filtrada = cv2.cvtColor(img_filtrada, cv2.COLOR_GRAY2BGR)
            img_show = Image.fromarray(cv2.cvtColor(img_filtrada, cv2.COLOR_BGR2RGBA))
        else:
            st.markdown("**Nenhum filtro selecionado**")
            img_show = img

        # Stickers
        stickers_dir = Path("images")
        # Lista todos os arquivos de imagem na pasta de stickers
        stickers_files = [f for f in stickers_dir.glob("*") if f.suffix in [".png", ".jpg", ".jpeg"]]
        stickers_names = [f.name for f in stickers_files]
        # Selectbox para escolher sticker
        selected_sticker = st.selectbox("Escolha um sticker para colar", [""] + stickers_names, key="sticker_select", index=0)

        # Sliders para tamanho e opacidade do sticker
        max_sticker_size = min(img_show.width, img_show.height) // 3
        sticker_size = st.slider("Tamanho do sticker (px)", 32, max_sticker_size, max_sticker_size // 2)
        sticker_opacity = st.slider("Opacidade do sticker", 0.0, 1.0, 1.0, step=0.05)

        # Botão para resetar a foto (remove todos os stickers e filtro)
        if st.button("Resetar para foto original", key="reset_stickers"):
            key_idx = st.session_state["filtro_key"]
            # Remove todas as chaves do session_state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Atualiza a chave do filtro para forçar rerun
            st.session_state["filtro_key"] = key_idx+1
            st.rerun()

        # Inicializa lista de stickers e pontos na sessão
        if "stickers_points" not in st.session_state:
            # Cada item: (x, y, sticker_name, size, opacity)
            st.session_state["stickers_points"] = []

        # Função chamada ao clicar na imagem para adicionar sticker
        def add_sticker():
            raw_value = st.session_state["pil"]
            value = raw_value["x"], raw_value["y"]
            # Salva o sticker selecionado, tamanho e opacidade junto com o ponto
            st.session_state["stickers_points"].append((value[0], value[1], selected_sticker, sticker_size, sticker_opacity))

        st.write("Clique na imagem para colar o sticker selecionado. Você pode clicar várias vezes para adicionar múltiplos stickers diferentes.")
        # Componente para capturar clique na imagem
        value = streamlit_image_coordinates(
            img_show,
            key="pil",
            on_click=add_sticker,
            width=img_show.width,
            height=img_show.height
        )

        # Desenha todos os stickers nos pontos salvos
        result_img = img_show.copy()
        for x, y, sticker_name, size, opacity in st.session_state["stickers_points"]:
            if sticker_name != "":
                sticker_path = stickers_dir / sticker_name
                sticker_img = Image.open(sticker_path).convert("RGBA")
                # Redimensiona sticker
                sticker_img = sticker_img.resize((size, size), Image.LANCZOS)
                # Aplica opacidade
                if opacity < 1.0:
                    alpha = sticker_img.split()[-1]
                    alpha = alpha.point(lambda p: int(p * opacity))
                    sticker_img.putalpha(alpha)
                # Cola o sticker na posição clicada
                result_img.paste(sticker_img, (int(x), int(y)), sticker_img)
        # Exibe imagem final com stickers
        st.image(result_img, caption="Foto com stickers")
        # Permite baixar a imagem final
        img_bytes = cv2.imencode('.png', np.array(result_img))[1].tobytes()
        st.download_button("Salvar imagem", img_bytes, file_name="imagem_com_stickers.png", mime="image/png", key="save_foto_sticker")


# --- Aba Vídeo (streamlit-webrtc) ---
with tab2:
    import subprocess

    def convert_to_h264(input_path, output_path):
        """
        Converte vídeo para formato H.264 usando ffmpeg.
        """
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
    filter_options = [""] + list(FILTERS.keys())
    selected_filter = st.selectbox("Escolha um filtro para o vídeo", filter_options, key="webrtc_filtro_vid")
    st.markdown(f"**Descrição do filtro:** {FILTERS[selected_filter]['desc']}" if selected_filter else "")

    RECORD_DIR = Path("./records")
    RECORD_DIR.mkdir(exist_ok=True)

    # Gera prefixo único para os arquivos de vídeo
    if "prefix_video" not in st.session_state:
        st.session_state["prefix_video"] = str(uuid.uuid4())
    prefix = st.session_state["prefix_video"]
    in_file = RECORD_DIR / f"{prefix}_input.mp4"
    out_file = RECORD_DIR / f"{prefix}_output.mp4"

    # Funções para gravar vídeo
    def in_recorder_factory():
        return MediaRecorder(str(in_file), format="mp4")

    def out_recorder_factory():
        return MediaRecorder(str(out_file), format="mp4")

    # Função de callback para aplicar filtro em cada frame do vídeo
    def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        if selected_filter and selected_filter in FILTERS:
            img = FILTERS[selected_filter]["func"](img)
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    # Observação importante sobre filtros e gravação
    # SE TROCAR O FILTRO NO MEIO DA GRAVAÇÃO, O VÍDEO FICA COM PROBLEMA. PARA FUNCIONAR O UPLOAD DO VÍDEO, PRIMEIRO APLIQUE O FILTRO E DEPOIS BOTE PARA GRAVAR.

    # Inicializa o componente de gravação de vídeo
    ctx_video = webrtc_streamer(
        key="video",
        mode=WebRtcMode.SENDRECV,
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=video_frame_callback,
        in_recorder_factory=in_recorder_factory,
        out_recorder_factory=out_recorder_factory,
    )

    # Permite baixar apenas o vídeo filtrado gravado
    if out_file.exists():
        h264_output_path = out_file.parent / f"{prefix}_output_h264.mp4"
        if not h264_output_path.exists():
            if convert_to_h264(out_file, h264_output_path):
                st.success("Vídeo filtrado pronto para download!")
            else:
                st.error("Falha ao converter o vídeo filtrado.")
        if h264_output_path.exists():
            with h264_output_path.open("rb") as f:
                st.download_button(
                    "Download do vídeo filtrado", f, "video_filtrado.mp4", key="download_output_h264_video_tab3", mime="video/mp4"
                )
            delete_folder_files(RECORD_DIR)

# --- Aba Operações Matemáticas ---
with tab3:
    st.header("Operações Matemáticas entre Imagens")
    st.write("Selecione duas imagens (upload ou tirar foto) e uma operação para combinar.")

    # Colunas para seleção das imagens
    col1, col2 = st.columns(2)
    with col1:
        tipo_img1 = st.radio("Imagem 1", ["Upload", "Tirar Foto"], key="tipo_img1")
        if tipo_img1 == "Upload":
            img_file1 = st.file_uploader("Upload da Imagem 1", type=["png", "jpg", "jpeg"], key="math_img1_upload")
            if img_file1:
                img1 = Image.open(img_file1)
        else:
            img_file1 = st.camera_input("Tire a Foto 1", key="math_img1_camera")
            if img_file1:
                img1 = Image.open(img_file1)

    with col2:
        tipo_img2 = st.radio("Imagem 2", ["Upload", "Tirar Foto"], key="tipo_img2")
        if tipo_img2 == "Upload":
            img_file2 = st.file_uploader("Upload da Imagem 2", type=["png", "jpg", "jpeg"], key="math_img2_upload")
            if img_file2:
                img2 = Image.open(img_file2)
        else:
            img_file2 = st.camera_input("Tire a Foto 2", key="math_img2_camera")
            if img_file2:
                img2 = Image.open(img_file2)

    # Selectbox para escolher operação matemática
    op_list = list(MATH_OPS.keys())
    op_selected = st.selectbox("Operação", op_list)

    # Executa operação se ambas imagens estão disponíveis
    if 'img1' in locals() and 'img2' in locals():
        img1_np = np.array(img1)
        img2_np = np.array(img2)
        # Ajusta tamanho se necessário
        if img1_np.shape != img2_np.shape:
            st.warning("As imagens precisam ter o mesmo tamanho e canais. Redimensionando a segunda imagem...")
            img2_np = cv2.resize(img2_np, (img1_np.shape[1], img1_np.shape[0]))
        # Executa operação matemática selecionada
        if op_selected == "Blending":
            alpha = st.slider("Peso da Imagem 1 (alpha)", 0.0, 1.0, 0.5, 0.01)
            result = MATH_OPS[op_selected]["func"](img1_np, img2_np, alpha)
        elif op_selected == "Subtração Ponderada":
            alpha = st.slider("Peso da Imagem 1 (alpha)", 0.0, 1.0, 0.7, 0.01)
            beta = st.slider("Peso da Imagem 2 (beta)", 0.0, 1.0, 0.3, 0.01)
            result = MATH_OPS[op_selected]["func"](img1_np, img2_np, alpha, beta)
        else:
            result = MATH_OPS[op_selected]["func"](img1_np, img2_np)
        # Exibe resultado
        st.image(result, caption=f"Resultado: {op_selected}")
        # Permite baixar resultado
        img_bytes = cv2.imencode('.png', result)[1].tobytes()
        st.download_button("Salvar resultado", img_bytes, file_name="resultado.png", mime="image/png", key="save_math_result")