import os
import tempfile
import streamlit as st
import yt_dlp

st.set_page_config(page_title="Descargador de Videos", page_icon="🎬", layout="centered")

st.title("🎬 Descargador de Videos de YouTube")
st.write("Pega el enlace de un video para procesarlo y descargarlo directamente desde tu navegador.")

url = st.text_input("Enlace del video de YouTube:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Procesar Video", type="primary"):
    if not url:
        st.warning("Por favor, introduce un enlace válido.")
    else:
        with st.spinner("Procesando y preparando el archivo... Esto puede tardar unos momentos."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 'format': 'worst/best' o 'b' obliga a tomar un solo archivo que contenga video y audio sin requerir procesamiento ni formatos específicos
                ydl_opts = {
                    'format': 'worst/b/best', 
                    'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'logtostderr': False,
                    'geo_bypass': True,
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
