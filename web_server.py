# -*- coding: utf-8 -*-
"""
Web界面 - 实时PDF转有声读物工具
支持上传、转换、实时进度显示和在线试听
"""
import os
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import gradio as gr
from audiobook_maker import AudiobookMaker
from audio_generator import AudioGenerator
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'generated_audio'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# 全局变量存储处理状态
processing_status = {
    'is_processing': False,
    'current_file': None,
    'progress': 0,
    'total_chunks': 0,
    'completed_chunks': 0,
    'generated_files': [],
    'start_time': None,
    'voice_preset': 'v2/en_speaker_6'
}

class RealtimeAudiobookMaker:
    """实时有声读物制作器 - 每5分钟生成一个音频文件"""
    
    def __init__(self, voice_preset="v2/en_speaker_6", use_small_model=True):
        self.voice_preset = voice_preset
        self.use_small_model = use_small_model
        self.text_processor = TextProcessor(max_chars=200)
        self.audio_generator = None  # 延迟初始化
        self.is_processing = False
        
    def _init_audio_generator(self):
        """延迟初始化音频生成器"""
        if self.audio_generator is None:
            print("正在初始化音频生成器...")
            self.audio_generator = AudioGenerator(voice_preset=self.voice_preset, 
                                                 use_small_model=self.use_small_model)
            print("✓ 音频生成器初始化完成")
        
    def start_processing(self, pdf_path, output_dir):
        """开始处理PDF文件"""
        self.is_processing = True
        
        try:
            # 更新状态
            processing_status['is_processing'] = True
            processing_status['current_file'] = os.path.basename(pdf_path)
            processing_status['start_time'] = datetime.now().isoformat()
            processing_status['generated_files'] = []
            
            # 提取PDF文本
            print("正在提取PDF文本...")
            extractor = PDFExtractor(pdf_path)
            text = extractor.extract_text()
            
            # 分割文本
            print("正在分割文本...")
            chunks = self.text_processor.split_into_chunks(text)
            
            processing_status['total_chunks'] = len(chunks)
            processing_status['completed_chunks'] = 0
            
            print(f"文本已分割成 {len(chunks)} 个片段")
            
            # 每5分钟生成一个音频文件（约150个片段）
            chunks_per_file = 150  # 约5分钟的音频
            total_files = (len(chunks) + chunks_per_file - 1) // chunks_per_file
            
            for file_idx in range(total_files):
                if not self.is_processing:
                    break
                    
                start_idx = file_idx * chunks_per_file
                end_idx = min(start_idx + chunks_per_file, len(chunks))
                file_chunks = chunks[start_idx:end_idx]
                
                print(f"正在生成第 {file_idx + 1}/{total_files} 个音频文件...")
                
                # 生成音频文件
                output_filename = f"audiobook_part_{file_idx + 1:03d}.wav"
                output_path = os.path.join(output_dir, output_filename)
                
                # 生成音频片段
                temp_dir = f"temp_chunks_{file_idx}"
                os.makedirs(temp_dir, exist_ok=True)
                
                audio_files = []
                for i, chunk in enumerate(file_chunks):
                    if not self.is_processing:
                        break
                        
                    audio_array = self.audio_generator.generate_single_audio(chunk)
                    chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}.wav")
                    
                    from scipy.io import wavfile
                    wavfile.write(chunk_path, self.audio_generator.sample_rate, audio_array)
                    audio_files.append(chunk_path)
                    
                    # 更新进度
                    processing_status['completed_chunks'] += 1
                    processing_status['progress'] = (processing_status['completed_chunks'] / 
                                                   processing_status['total_chunks'] * 100)
                
                if audio_files and self.is_processing:
                    # 合并音频文件
                    merged_audio = self.audio_generator.merge_audio_files(audio_files, output_path)
                    
                    # 添加到生成文件列表
                    file_info = {
                        'filename': output_filename,
                        'path': output_path,
                        'size': os.path.getsize(output_path),
                        'created_time': datetime.now().isoformat(),
                        'part_number': file_idx + 1,
                        'total_parts': total_files
                    }
                    processing_status['generated_files'].append(file_info)
                    
                    print(f"✓ 第 {file_idx + 1} 个音频文件已生成: {output_filename}")
                
                # 清理临时文件
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            
            print("✓ 所有音频文件生成完成！")
            
        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
        finally:
            self.is_processing = False
            processing_status['is_processing'] = False

# 创建实时制作器实例
realtime_maker = RealtimeAudiobookMaker()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传PDF文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    return jsonify({'error': '请上传PDF文件'}), 400

@app.route('/start_conversion', methods=['POST'])
def start_conversion():
    """开始转换"""
    data = request.get_json()
    filepath = data.get('filepath')
    voice_preset = data.get('voice_preset', 'v2/en_speaker_6')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 400
    
    if processing_status['is_processing']:
        return jsonify({'error': '正在处理中，请等待完成'}), 400
    
    # 更新语音预设
    processing_status['voice_preset'] = voice_preset
    realtime_maker.voice_preset = voice_preset
    
    # 在后台线程中开始处理
    thread = threading.Thread(
        target=realtime_maker.start_processing,
        args=(filepath, app.config['AUDIO_FOLDER'])
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '开始转换'})

@app.route('/status')
def get_status():
    """获取处理状态"""
    return jsonify(processing_status)

@app.route('/audio/<filename>')
def get_audio(filename):
    """获取音频文件"""
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

@app.route('/stop_conversion', methods=['POST'])
def stop_conversion():
    """停止转换"""
    realtime_maker.is_processing = False
    processing_status['is_processing'] = False
    return jsonify({'success': True, 'message': '已停止转换'})

@app.route('/clear_files', methods=['POST'])
def clear_files():
    """清理生成的文件"""
    try:
        # 清理音频文件
        for file_info in processing_status['generated_files']:
            file_path = file_info['path']
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 重置状态
        processing_status['generated_files'] = []
        processing_status['progress'] = 0
        processing_status['completed_chunks'] = 0
        processing_status['total_chunks'] = 0
        
        return jsonify({'success': True, 'message': '文件已清理'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("启动Web服务器...")
    print("访问地址: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
