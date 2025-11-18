# Processamento Gráfico - GB

**Alunos:** Enzo Porto, Patrick Strassburger e Vicenzo Valmorbida

## Sobre o Projeto

Este projeto é um aplicativo Streamlit para edição de fotos e vídeos usando filtros do OpenCV, stickers personalizados e operações matemáticas entre imagens.

## Requisitos

- Python 3.12.2
- [ffmpeg](https://ffmpeg.org/) instalado no sistema (necessário para conversão de vídeos)
- Instalar dependências do projeto:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## Como rodar

```bash
streamlit run main.py
```

## Funcionalidades

### Aba Foto
- Tire uma foto com a webcam ou faça upload de uma imagem.
- Aplique filtros do OpenCV (ex: blur, grayscale, sepia, bordas, canais, etc).
- Cole stickers personalizados na imagem, escolhendo posição com o mouse, tamanho e opacidade.
- Adicione múltiplos stickers diferentes na mesma foto.
- Baixe a imagem final editada.
- Botão para resetar a imagem e filtros.

### Aba Vídeo
- Grave vídeo da webcam com filtro aplicado em tempo real.
- Baixe o vídeo original e o vídeo filtrado (convertido para H.264).
- Observação: para conseguir salvar o vídeo, primeiro escolha o filtro desejado. Se trocar o filtro durante a gravação, a câmera é reiniciada e o vídeo pode ser cortado.

### Aba Operações Matemáticas
- Combine duas imagens usando operações matemáticas (soma, subtração, blending, etc).
- Ajuste pesos para blending/subtração ponderada.
- Baixe o resultado da operação.

## Estrutura do Projeto

- `main.py` — Código principal do app Streamlit.
- `apply_filters.py` — Implementação dos filtros e operações matemáticas.
- `util.py` — Funções utilitárias (ex: deletar arquivos temporários).
- `images/` — Pasta com stickers para colar nas fotos.
- `records/` — Pasta onde os vídeos gravados são salvos.
- `requirements.txt` — Dependências do projeto.

## Observações

- Para usar a webcam, permita acesso ao navegador.
- Os stickers devem estar na pasta `images/`.
- Os vídeos são salvos e convertidos automaticamente para H.264 (foi desenvolvido em MacOS, não sei como isso se comportara em Windows e Linux).
---