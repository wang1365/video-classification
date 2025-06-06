import pathlib
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox
import os
import time  # 用于模拟耗时操作
from concurrent.futures import ThreadPoolExecutor  # 用于多线程处理

os.environ['PATH'] = os.environ['PATH'] + os.pathsep + "./_internal"

class FileClassifierApp:
    def __init__(self, master):
        self.master = master
        master.title("视频与剧本分类工具")
        master.geometry("1200x700")  # 调整窗口大小以适应左右两部分

        # 左右主框架
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 左侧部分 - 文件选择和列表
        self.left_frame = tk.Frame(self.main_frame, bd=2, relief="groove")  # 添加边框
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # 右侧部分 - 视频分类和结果展示
        self.right_frame = tk.Frame(self.main_frame, bd=2, relief="groove")  # 添加边框
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # --- 左侧功能区 ---
        # 视频文件部分
        self.video_frame = tk.LabelFrame(self.left_frame, text="视频文件", padx=10, pady=10)
        self.video_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.btn_select_video_folder = tk.Button(self.video_frame, text="选择视频文件夹",
                                                 command=self.select_video_folder)
        self.btn_select_video_folder.pack(pady=5)

        self.video_folder_label = tk.Label(self.video_frame, text="当前视频文件夹: 未选择")
        self.video_folder_label.pack(pady=5)

        # 视频文件列表框
        self.video_list_scrollbar = tk.Scrollbar(self.video_frame)
        self.video_list_scrollbar.pack(side="right", fill="y")
        self.video_listbox = tk.Listbox(self.video_frame, width=60, height=10,
                                        yscrollcommand=self.video_list_scrollbar.set)
        self.video_listbox.pack(pady=5, fill="both", expand=True)
        self.video_list_scrollbar.config(command=self.video_listbox.yview)

        # PDF文件部分
        self.pdf_frame = tk.LabelFrame(self.left_frame, text="剧本文件 (PDF)", padx=10, pady=10)
        self.pdf_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.btn_select_pdf_folder = tk.Button(self.pdf_frame, text="选择PDF文件夹", command=self.select_pdf_folder)
        self.btn_select_pdf_folder.pack(pady=5)

        self.pdf_folder_label = tk.Label(self.pdf_frame, text="当前PDF文件夹: 未选择")
        self.pdf_folder_label.pack(pady=5)

        # PDF文件列表框
        self.pdf_list_scrollbar = tk.Scrollbar(self.pdf_frame)
        self.pdf_list_scrollbar.pack(side="right", fill="y")
        self.pdf_listbox = tk.Listbox(self.pdf_frame, width=60, height=10,
                                      yscrollcommand=self.pdf_list_scrollbar.set)
        self.pdf_listbox.pack(pady=5, fill="both", expand=True)
        self.pdf_list_scrollbar.config(command=self.pdf_listbox.yview)

        # --- 右侧功能区 ---
        self.classify_frame = tk.LabelFrame(self.right_frame, text="视频分类操作与结果", padx=10, pady=10)
        self.classify_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.btn_classify_videos = tk.Button(self.classify_frame, text="开始视频分类",
                                             command=self.start_video_classification)
        self.btn_classify_videos.pack(pady=10)

        self.classification_status_label = tk.Label(self.classify_frame, text="状态: 准备就绪")
        self.classification_status_label.pack(pady=5)

        self.classification_result_label = tk.Label(self.classify_frame, text="分类结果:")
        self.classification_result_label.pack(pady=5)

        # 分类结果列表框
        self.result_list_scrollbar = tk.Scrollbar(self.classify_frame)
        self.result_list_scrollbar.pack(side="right", fill="y")
        self.result_listbox = tk.Listbox(self.classify_frame, width=60, height=20,
                                         yscrollcommand=self.result_list_scrollbar.set)
        self.result_listbox.pack(pady=5, fill="both", expand=True)
        self.result_list_scrollbar.config(command=self.result_listbox.yview)

        # 存储当前选择的文件夹路径
        self.video_folder_path = ""
        self.pdf_folder_path = ""

        # 使用线程池来执行耗时操作，避免界面卡死
        self.executor = ThreadPoolExecutor(max_workers=1)

    def select_video_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.video_folder_path = folder_selected
            self.video_folder_label.config(
                text=f"当前视频文件夹: {os.path.basename(self.video_folder_path)}")  # 只显示文件夹名
            self.load_files_to_listbox(self.video_folder_path, self.video_listbox,
                                       ['.mxf'])
        else:
            messagebox.showinfo("提示", "未选择视频文件夹。")

    def select_pdf_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.pdf_folder_path = folder_selected
            self.pdf_folder_label.config(text=f"当前PDF文件夹: {os.path.basename(self.pdf_folder_path)}")  # 只显示文件夹名
            self.load_files_to_listbox(self.pdf_folder_path, self.pdf_listbox, ['.pdf'])
        else:
            messagebox.showinfo("提示", "未选择PDF文件夹。")

    def load_files_to_listbox(self, folder_path, listbox_widget, allowed_extensions):
        listbox_widget.delete(0, tk.END)  # 清空现有列表
        if not os.path.exists(folder_path):
            messagebox.showerror("错误", "指定的文件夹不存在！")
            return

        files = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item)[1].lower()
                if file_ext in allowed_extensions:
                    files.append(item)

        if not files:
            listbox_widget.insert(tk.END, "此文件夹中没有找到匹配的文件。")
        else:
            for file_name in sorted(files):
                listbox_widget.insert(tk.END, file_name)

    def start_video_classification(self):
        if not self.video_folder_path or not os.path.exists(self.video_folder_path):
            messagebox.showwarning("警告", "请先选择有效的视频文件夹！")
            return
        if not self.pdf_folder_path or not os.path.exists(self.pdf_folder_path):
            messagebox.showwarning("警告", "请先选择有效的PDF剧本文件夹！")
            return

        # 清空之前的分类结果
        self.result_listbox.delete(0, tk.END)
        self.classification_status_label.config(text="状态: 正在进行视频分类...")
        self.btn_classify_videos.config(state=tk.DISABLED)  # 分类过程中禁用按钮

        # 在单独的线程中执行分类逻辑
        future = self.executor.submit(self._run_classification_logic)
        future.add_done_callback(self._on_classification_done)

    def _run_classification_logic(self):
        """
        这个函数将包含你的实际视频分类逻辑。
        为了避免界面卡死，它应该在一个单独的线程中运行。
        这里我们用一个模拟来代替。
        """
        print(f"开始分类...\n视频文件夹: {self.video_folder_path}\nPDF文件夹: {self.pdf_folder_path}")

        # 模拟AI分类过程
        classified_results = []
        video_files = [self.video_listbox.get(i) for i in range(self.video_listbox.size()) if
                       "此文件夹中没有找到" not in self.video_listbox.get(i)]
        pdf_files = [self.pdf_listbox.get(i) for i in range(self.pdf_listbox.size()) if
                     "此文件夹中没有找到" not in self.pdf_listbox.get(i)]

        if not video_files:
            return ["没有找到视频文件进行分类。"]
        if not pdf_files:
            return ["没有找到PDF剧本文件进行分类。"]

        # 简单的模拟分类逻辑：假设每个视频都匹配到一个随机的PDF剧本
        # 在实际应用中，这里会调用你的AI/ML模型进行匹配
        from app.main import extract_all_pdfs, main
        pfs = [os.path.join(self.pdf_folder_path, pf) for pf in pdf_files]
        vfs = [os.path.join(self.video_folder_path, vf) for vf in video_files]
        pfs_info = extract_all_pdfs(pfs)

        try:
            result = main(vfs, pfs_info)
        except Exception as e:
            # 捕获任何异常，并格式化堆栈信息
            error_traceback = traceback.format_exc()
            print("子线程捕获到异常:\n", error_traceback)  # 打印到控制台
            # 将异常信息返回，以便在主线程中处理
            return {"error": str(e), "traceback": error_traceback}
        print(result)

        # for i, video_file in enumerate(video_files):
        #     # 模拟耗时操作，例如：视频处理、ASR、文本对比
        #     time.sleep(0.5)
        #     try:
        #         # 随机选择一个PDF作为匹配结果
        #         import random
        #         matched_pdf = random.choice(pdf_files)
        #         classified_results.append(
        #             f"视频: {video_file} -> 匹配剧本: {matched_pdf} (匹配度: {random.randint(70, 99)}%)")
        #     except IndexError:
        #         classified_results.append(f"视频: {video_file} -> 未找到可用剧本匹配")

        return result

    def _on_classification_done(self, future):
        """
        分类逻辑执行完毕后的回调函数，在主线程中更新UI。
        """
        try:
            results = future.result()  # 获取分类结果
            for item in results:
                video, pdf = pathlib.Path(item[0]).name, pathlib.Path(item[1]).name
                result_line = f"视频: {video} -> 匹配剧本: {pdf} "
                self.result_listbox.insert(tk.END, result_line)
            self.classification_status_label.config(text="状态: 分类完成！")
        except Exception as e:
            self.classification_status_label.config(text=f"状态: 分类出错！{e}")
            messagebox.showerror("错误", f"视频分类过程中发生错误: {e}")
        finally:
            self.btn_classify_videos.config(state=tk.NORMAL)  # 重新启用按钮


# 创建Tkinter主窗口
root = tk.Tk()
app = FileClassifierApp(root)

# 运行主循环
root.mainloop()