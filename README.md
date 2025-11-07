
# Processamento Gráfico - GB

**Alunos:** Enzo Porto, Patrick Strassburger e Vicenzo Valmorbida

## Requisitos

- Python 3.12.2
- [ffmpeg](https://ffmpeg.org/) instalado no sistema (necessário para conversão de vídeos)
- Instalar dependências do projeto:
	```bash
	pip install -r requirements.txt
	```
	Ou manualmente:
	```bash
	pip install streamlit streamlit-webrtc aiortc av opencv-python pillow
	```

## Como rodar

```bash
streamlit run main.py
```

## Funcionalidades

- **Aba Foto:**
	- Captura foto da webcam
	- Aplica filtros OpenCV (blur, bordas, canais, sepia, etc.)
	- Permite salvar a imagem filtrada

- **Aba Upload:**
	- Upload de imagem
	- Aplica filtros nas imagens
	- Permite salvar imagem filtrada

- **Aba Vídeo:**
	- Grava vídeo da webcam
	- Aplica filtros em tempo real
	- Salva vídeo original e/ou filtrado
	- Converte automaticamente para mp4/H.264 (compatível com QuickTime)

## Observações

- O vídeo gravado é convertido automaticamente para mp4/H.264 após gravação, garantindo compatibilidade com QuickTime Player.
- O ffmpeg precisa estar instalado e disponível no PATH do sistema.

## TODO

- Operações Matemáticas: Implementar pelo menos 3 operações aritméticas com duas imagens (ex: adição, subtração ponderada, blending) (Verificar com a professora).
- Parte dos Stickers: Implementar funcionalidade de stickers sobre imagens (as 5 fotos a serem usadas estão commitadas).
- Talvez verificar a parte da conversão de vídeos pq eu (enzo) estou usando MACOS.
- Montar slides
---
Projeto para disciplina de Processamento Gráfico.