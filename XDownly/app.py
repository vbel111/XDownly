from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import os
import tempfile
import threading
import time
from urllib.parse import urlparse
import re
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Response
import requests

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Add environment configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')

app.config.from_object(Config)

# Create downloads directory
DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Adult sites configuration - expanded list
ADULT_SITES = [
    'pornhub.com', 'xvideos.com', 'xhamster.com', 'redtube.com',
    'youporn.com', 'tube8.com', 'spankbang.com', 'xnxx.com',
    'beeg.com', 'tnaflix.com', 'drtuber.com', 'nuvid.com',
    'vporn.com', 'txxx.com', 'hdzog.com', 'upornia.com',
    'eporner.com', 'gotporn.com', 'analdin.com', 'sunporno.com',
    'fapality.com', 'sexvid.xxx', 'porn.com', 'thumbzilla.com',
    'ixxx.com', 'ok.xxx', 'porntrex.com', 'hqporner.com',
    'porndig.com', 'pornone.com', 'freeones.com', 'pornhd.com',
    'empflix.com', 'moviefap.com', 'slutload.com', 'extremetube.com',
    'keezmovies.com', 'mofosex.com', 'pornerbros.com', 'fux.com',
    'pornoxo.com', 'alphaporno.com', 'anysex.com', 'befuck.com',
    'bravotube.net', 'definebabe.com', 'drporn.com', 'fapdu.com',
    'flyflv.com', 'freeporn.com', 'gotgayporn.com', 'hdporn.net',
    'hdpornz.com', 'hotmovs.com', 'iceporn.com', 'jizzbunker.com',
    'katestube.com', 'largeporntube.com', 'madthumbs.com', 'megatube.xxx',
    'milffox.com', 'nuvid.com', 'orgasm.com', 'perfectgirls.net',
    'pervclips.com', 'pinkrod.com', 'porn300.com', 'porn555.com',
    'pornbanana.com', 'pornburst.xxx', 'porndoe.com', 'porngo.com',
    'pornhat.com', 'pornheed.com', 'pornhits.com', 'pornhub.com',
    'pornid.xxx', 'pornktube.com', 'pornl.com', 'pornmaki.com',
    'pornmd.com', 'pornmega.com', 'pornpics.com', 'pornq.com',
    'pornrabbit.com', 'pornsocket.com', 'pornstar.com', 'pornstep.com',
    'porntop.com', 'porntube.com', 'porntubevidz.com', 'pornvibe.org',
    'pornwhite.com', 'pornxs.com', 'pornyeah.com', 'porrzab.com',
    'proporn.com', 'pussyspace.com', 'redporn.xxx', 'sexu.com',
    'sexvid.xxx', 'shameless.com', 'sluttyred.com', 'spankwire.com',
    'stileproject.com', 'sunporno.com', 'thenewporn.com', 'tjoob.com',
    'tubegalore.com', 'tubepornclassic.com', 'tubewolf.com', 'updatetube.com',
    'vjav.com', 'watchmygf.com', 'wankoz.com', 'xbabe.com',
    'xcafe.com', 'xfantazy.com', 'xmoviesforyou.com', 'xozilla.com',
    'xtube.com', 'xxxbunker.com', 'xxxdan.com', 'youjizz.com',
    'yuvutu.com', 'zbporn.com', 'zedporn.com', 'ztod.com'
]

def get_site_category(url):
    """Determine if URL is from adult site"""
    domain = urlparse(url).netloc.lower()
    domain = domain.replace('www.', '')
    
    for site in ADULT_SITES:
        if site in domain:
            return 'adult'
    
    return 'unknown'

def clean_filename(filename):
    """Clean filename for safe saving"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Check if it's an adult site
        category = get_site_category(url)
        if category != 'adult':
            return jsonify({'error': 'Only adult content sites are supported. Please use a URL from supported adult platforms.'}), 400
        
        # Configure yt-dlp options
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get available formats
            formats = []
            if 'formats' in info:
                for f in info['formats']:
                    if f.get('vcodec') != 'none':  # Video formats only
                        formats.append({
                            'format_id': f.get('format_id'),
                            'ext': f.get('ext'),
                            'quality': f.get('height', 'Unknown'),
                            'filesize': f.get('filesize'),
                            'format_note': f.get('format_note', '')
                        })
            
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'formats': formats[:10],  # Limit to first 10 formats
                'category': category
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        format_id = data.get('format_id', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Verify it's an adult site
        category = get_site_category(url)
        if category != 'adult':
            return jsonify({'error': 'Only adult content sites are supported.'}), 400
        
        # Create unique filename
        timestamp = str(int(time.time()))
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(DOWNLOAD_DIR, f'{timestamp}_%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Find the downloaded file
            expected_filename = ydl.prepare_filename(info)
            
            if os.path.exists(expected_filename):
                return jsonify({
                    'success': True,
                    'filename': os.path.basename(expected_filename),
                    'title': info.get('title', 'Unknown')
                })
            else:
                return jsonify({'error': 'Download failed'}), 500
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-file/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-preview', methods=['POST'])
def get_video_preview():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Verify it's an adult site
        category = get_site_category(url)
        if category != 'adult':
            return jsonify({'error': 'Only adult content sites are supported.'}), 400
        
        # Configure yt-dlp options for preview
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': 'worst[height<=480]/worst',  # Get low quality for preview
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get preview URL (usually the lowest quality stream)
            preview_url = None
            if 'formats' in info:
                # Find a suitable preview format
                for f in info['formats']:
                    if (f.get('vcodec') != 'none' and 
                        f.get('height') and f.get('height') <= 480 and
                        f.get('url')):
                        preview_url = f.get('url')
                        break
                
                # Fallback to any video format if no low quality found
                if not preview_url:
                    for f in info['formats']:
                        if f.get('vcodec') != 'none' and f.get('url'):
                            preview_url = f.get('url')
                            break
            
            # If no direct URL, try to get the best available
            if not preview_url and info.get('url'):
                preview_url = info.get('url')
            
            return jsonify({
                'preview_url': preview_url,
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'description': info.get('description', '')[:500] if info.get('description') else ''
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream', methods=['POST'])
def stream_video():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        format_id = data.get('format_id', 'best')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Verify it's an adult site
        category = get_site_category(url)
        if category != 'adult':
            return jsonify({'error': 'Only adult content sites are supported.'}), 400

        # Get direct video URL using yt_dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': format_id,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = None
            if 'formats' in info:
                for f in info['formats']:
                    if f.get('format_id') == format_id and f.get('url'):
                        video_url = f['url']
                        break
            if not video_url and info.get('url'):
                video_url = info['url']

        if not video_url:
            return jsonify({'error': 'Could not get video URL'}), 500

        # Stream the video to the client
        def generate():
            with requests.get(video_url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

        return Response(generate(), mimetype='video/mp4')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cleanup old files periodically
def cleanup_old_files():
    """Remove files older than 1 hour"""
    while True:
        try:
            current_time = time.time()
            for filename in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > 3600:  # 1 hour
                        os.remove(file_path)
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        time.sleep(300)  # Check every 5 minutes

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'], 
        host=app.config['HOST'], 
        port=app.config['PORT']
    )
