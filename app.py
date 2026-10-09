import os
import tempfile
import streamlit as st
import yt_dlp

st.set_page_config(page_title="Descargador de Videos", page_icon="🎬", layout="centered")

st.title("🎬 Descargador de Videos de YouTube")
st.write("Pega el enlace de un video o Short para procesarlo y descargarlo directamente.")

url = st.text_input("Enlace del video o Short de YouTube:", placeholder="https://www.youtube.com/shorts/...")

def descargar_con_fallbacks(url_video, temp_dir):
    # Lista de configuraciones en orden de preferencia. Si una falla por formato o bloqueo 403, pasa a la siguiente.
    estrategias = [
        # Estrategia 1: Mejor calidad uniendo audio + video con FFmpeg (Cliente Android)
        {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        },
        # Estrategia 2: Cliente iOS con cualquier formato de video/audio que exista
        {
            'format': 'best',
            'extractor_args': {'youtube': {'player_client': ['ios', 'mweb']}},
        },
        # Estrategia 3: Sin restricción de formato (yt-dlp decide el único archivo descargable)
        {
            'format': None,
            'extractor_args': {'youtube': {'player_client': ['tv', 'web']}},
        }
    ]

    ultimo_error = None

    for est in estrategias:
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': est['extractor_args'],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            }
        }
        if est['format']:
            ydl_opts['format'] = est['format']

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url_video, download=True)
                filename = ydl.prepare_filename(info)
                
                # Verificar si el archivo se generó correctamente
                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    return info, filename
                
                # Si FFmpeg cambió la extensión del archivo al unirlo (ej. .mp4)
                base_path = os.path.splitext(filename)[0]
                for f in os.listdir(temp_dir):
                    full_p = os.path.join(temp_dir, f)
                    if full_p.startswith(base_path) and os.path.getsize(full_p) > 0:
                        return info, full_p
        except Exception as e:
            ultimo_error = e
            continue  # Si esta estrategia falla, salta a la siguiente inmediatamente

    raise ultimo_error if ultimo_error else Exception("No se pudo obtener el video en ningún formato disponible.")

if st.button("Procesar Video", type="primary"):
    if not url:
        st.warning("Por favor, introduce un enlace válido.")
    else:
        with st.spinner("Procesando video... Evaluando la vía de conexión más estable."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                try:
                    info, filename = descargar_con_fallbacks(url, tmp_dir)
                    video_title = info.get('title', 'video')
                    ext = os.path.splitext(filename)[1].replace('.', '') or 'mp4'

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
                    st.error("No se pudo descargar el video debido a las restricciones de YouTube.")
                    st.exception(e)
