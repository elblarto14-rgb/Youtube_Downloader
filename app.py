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
        with st.spinner("Procesando y uniendo audio/video... Esto puede tardar unos segundos."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Opciones avanzadas que combinan video+audio con ffmpeg o buscan el mejor formato simple disponible
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                    # Evitar restricciones de servidor agregando encabezados de navegador común
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-us,en;q=0.5',
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
