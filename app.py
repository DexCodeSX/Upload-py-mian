from flask import Flask, request, render_template, jsonify, send_from_directory
            from werkzeug.utils import secure_filename
            import os
            import uuid
            import magic
            import hashlib
            from datetime import datetime
            
            app = Flask(__name__)
            UPLOAD_FOLDER = 'uploads'
            ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max upload size
            
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
            def get_file_hash(file_path):
                hash_md5 = hashlib.md5()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
            
            @app.route('/')
            def index():
                return render_template('index.html')
            
            @app.route('/upload', methods=['POST'])
            def upload_file():
                if 'file' not in request.files:
                    return jsonify({'error': 'No file part'}), 400
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
            
                    # Get file metadata
                    file_size = os.path.getsize(filepath)
                    file_type = magic.from_file(filepath, mime=True)
                    file_hash = get_file_hash(filepath)
                    upload_time = datetime.now().isoformat()
            
                    return jsonify({
                        'success': True,
                        'filename': unique_filename,
                        'original_filename': filename,
                        'file_size': file_size,
                        'file_type': file_type,
                        'file_hash': file_hash,
                        'upload_time': upload_time
                    }), 200
                return jsonify({'error': 'File type not allowed'}), 400
            
            @app.route('/uploads/<filename>')
            def uploaded_file(filename):
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
            
            @app.route('/files', methods=['GET'])
            def list_files():
                files = []
                for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file_size = os.path.getsize(file_path)
                    file_type = magic.from_file(file_path, mime=True)
                    files.append({
                        'filename': filename,
                        'size': file_size,
                        'type': file_type
                    })
                return jsonify(files)
            
            @app.route('/delete/<filename>', methods=['DELETE'])
            def delete_file(filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return jsonify({'success': True, 'message': 'File deleted successfully'}), 200
                return jsonify({'error': 'File not found'}), 404
            
            @app.errorhandler(413)
            def request_entity_too_large(error):
                return jsonify({'error': 'File too large'}), 413
            
            if __name__ == '__main__':
                app.run(debug=True)