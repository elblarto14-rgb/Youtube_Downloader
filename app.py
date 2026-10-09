import os
import tempfile
import streamlit as st
import yt_dlp

st.set_page_config(page_title="Descargador de Videos", page_icon="🎬", layout="centered")

st.title("🎬 Descargador de Videos de YouTube")
st.write("Pega el enlace de un video o Short para procesarlo y descargarlo directamente.")

url = st.text_input("Enlace del video o Short de YouTube:", placeholder="https://www.youtube.com/shorts/...")

if st.button("Procesar Video", type="primary"):
    if not url:
        st.warning("Por favor, introduce un enlace válido.")
    else:
        with st.spinner("Procesando video... Esto puede tardar unos segundos."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                ydl_opts = {
                    'format': 'b/best',  # Formato directo unificado para evitar bloqueos 403 en servidores
                    'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                    # Cambio a clientes móviles para evadir el bloqueo de IP de centro de datos
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['mweb', 'ios'],
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/605.1.15',
                    }
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        video_title = info.get('title', 'video')
                        ext = info.get('ext', 'mp4')

                    with open(filename, "rb") as file:
                        video_bytes = file.read()

                    st.success(f"¡Video procesado con éxito: **{video_title}**!")
                    
                    st.download_button(
                        label=f"⬇️ Descargar archivo ({ext.upper()})",
                        data=video_bytes,
                        file_name=f"{video_title}.{ext}",
                        mime=f"video/{ext}"
                    )
                except Exception as e:
                    st.error("Ocurrió un error al procesar el video.")
                    st.exception(e)
