import os

import numpy
import whisper
from docx import Document
from moviepy import VideoFileClip
from pydub import AudioSegment
import pdfplumber


def extract_audio_from_mxf(video_path, output_audio_path="temp_audio.wav"):
    """从MXF视频中提取音频并保存为WAV格式"""
    try:
        # 加载视频文件
        video = VideoFileClip(video_path)
        # 提取音频
        audio = video.audio
        # 保存为WAV格式（Whisper模型支持多种格式，但WAV更可靠）
        audio.write_audiofile(output_audio_path, codec="pcm_s16le")
        print(f"音频已提取并保存至: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"提取音频时出错: {e}")
        return None


def audio_to_text(audio_path, model_size="base"):
    """使用Whisper模型将音频转换为文本"""
    try:
        # 加载Whisper模型
        model = whisper.load_model(model_size)
        # 转录音频
        result = model.transcribe(audio_path)
        # 返回转录的文本
        return result["text"]
    except Exception as e:
        print(f"音频转文本时出错: {e}")
        return None

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_pdf(pdf_path):
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return '\n'.join(full_text)


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(text_list):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(text_list)
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]) # 比较第一个文本与其他文本

# text_video = "这是电影的第一场戏，主人公登场了。"
# text_script_1 = "剧本描述：这是电影的第一场戏，主人公闪亮登场。"
# text_script_2 = "本场戏没有对话，只有环境描述。"
# text_script_3 = "这是一个全新的剧本，与之前无关。"
#
# texts_to_compare = [text_video, text_script_1, text_script_2, text_script_3]
# similarities = calculate_cosine_similarity(texts_to_compare)
#
# print(f"Cosine similarity (video vs script 1): {similarities[0][0]}") # 与第一个剧本的相似度
# print(f"Cosine similarity (video vs script 2): {similarities[0][1]}") # 与第二个剧本的相似度
# print(f"Cosine similarity (video vs script 3): {similarities[0][2]}") # 与第三个剧本的相似度

def extract_all_pdfs(pdfs):
    result = {}
    for pdf in pdfs:
        print(f"pdf: {pdf}")
        text = extract_text_from_pdf(pdf)
        print(f"text: {text}")
        result[pdf] = text
    return result


def main(videos, pdf_info, model_size="base"):
    """主函数：从MXF视频中提取音频并转换为文本"""
    main_result = []
    for video_path in videos:
    # 提取音频
        audio_path = extract_audio_from_mxf(video_path)
        if not audio_path:
            print("无法提取音频，程序终止")
            return

        # 音频转文本
        transcription = audio_to_text(audio_path, model_size)
        if not transcription:
            print("无法进行音频转文本，程序终止")
            # 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return

        # 清理临时文件
        if os.path.exists(audio_path):
            os.remove(audio_path)


        # 打印转录的文本
        texts = [transcription]
        texts.extend(pdf_info.values())
        print('==> 开始对比相似性...', texts)
        result: numpy.ndarray = calculate_cosine_similarity(texts)

        print(f"result: {result[0][0]}, {result[0][1]}, {result[0][2]}")
        # 找出最大的相似度
        max_similarity = max(result[0][1:])
        max_index = list(result[0][1:]).index(max_similarity) + 1  # 加上1是因为我们从第二个文本开始比较

        # 打印最大相似度的脚本
        print(f"最大相似度: {max_similarity}, 对应的脚本: {list(pdf_info.keys())[max_index]}")
        main_result.append([video_path, list(pdf_info.keys())[max_index]])
    return main_result

if __name__ == "__main__":
    # 使用示例
    video_file = r"C:\Users\86180\Downloads\A004C001_250530DW.MXF"  # 替换为你的MXF文件路径
    output_file = "transcription.txt"
    model_size = "base"  # 可选: tiny, base, small, medium, large

    main(video_file, output_file, model_size)