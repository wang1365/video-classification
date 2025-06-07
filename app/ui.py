import pathlib
import sys
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox
import os
import time  # 用于模拟耗时操作
from concurrent.futures import ThreadPoolExecutor  # 用于多线程处理
from tkinter import ttk

from app.main import extract_text_from_pdf

os.environ['PATH'] = os.environ['PATH'] + os.pathsep + "./_internal"


class FileClassifierApp:
    def __init__(self, master):
        self.master = master
        master.title("Video Classification Tool")
        master.geometry("1400x700")  # 调整窗口大小以适应左右两部分

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
        self.video_frame = tk.LabelFrame(self.left_frame, text="Video", padx=10, pady=10)
        self.video_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.video_frame.grid_rowconfigure(1, weight=1)  # 添加这行
        self.video_frame.grid_columnconfigure(0, weight=1)  # 添加这行

        self.btn_select_video_folder = tk.Button(self.video_frame, text="Select Video Folder",
                                                 command=self.select_video_folder)

        self.btn_select_video_folder.grid(row=0, column=0, pady=5, sticky="w")

        self.video_folder_label = tk.Label(self.video_frame, text="", anchor="w")
        self.video_folder_label.grid(row=0, column=1, pady=5, sticky="w")

        # 将btn_select_video_folder 和 video_folder_label 放置在同一行
        # self.btn_select_video_folder.pack(side="left", padx=5)

        # 视频文件列表框
        self.video_list_scrollbar = tk.Scrollbar(self.video_frame)
        # self.video_list_scrollbar.grid(row=0, column=1, pady=5)
        self.video_listbox = tk.Listbox(self.video_frame, width=60, height=10,
                                        yscrollcommand=self.video_list_scrollbar.set)
        self.video_listbox.grid(row=1, column=0, columnspan=2, pady=5, sticky="nsew")
        self.video_list_scrollbar.grid(row=1, column=2, columnspan=1, sticky="ns")  # 添加这行
        self.video_list_scrollbar.config(command=self.video_listbox.yview)

        # 实现video_listbox的条目双击后打开视频文件
        def open_video(event):
            selected_index = self.video_listbox.curselection()
            if selected_index:
                selected_video = self.video_listbox.get(selected_index)
                video_path = os.path.join(self.video_folder_path, selected_video)
                if os.path.exists(video_path):
                    os.startfile(video_path)
                else:
                    messagebox.showerror("Error", "Video file not found!")
                    traceback.print_exc()

        self.video_listbox.bind("<Double-Button-1>", open_video)

        # PDF文件部分
        self.pdf_frame = tk.LabelFrame(self.left_frame, text="Script Files (PDF)", padx=10, pady=10)
        self.pdf_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.pdf_frame.grid_rowconfigure(1, weight=1)  # 添加这行
        self.pdf_frame.grid_columnconfigure(0, weight=1)  # 添加这行

        self.btn_select_pdf_folder = tk.Button(self.pdf_frame, text="Select Script Folder",
                                               command=self.select_pdf_folder)
        self.btn_select_pdf_folder.grid(row=0, column=0, columnspan=1, pady=5, sticky="w")

        self.pdf_folder_label = tk.Label(self.pdf_frame, text="", anchor="w")
        self.pdf_folder_label.grid(row=0, column=1, columnspan=3, pady=5, sticky="w")

        # PDF文件列表框
        self.pdf_list_scrollbar = tk.Scrollbar(self.pdf_frame)
        # self.pdf_list_scrollbar.pack(side="right", fill="y")
        self.pdf_listbox = tk.Listbox(self.pdf_frame, width=60, height=10,
                                      yscrollcommand=self.pdf_list_scrollbar.set)
        self.pdf_listbox.grid(row=1, column=0, columnspan=3, pady=5, sticky="nsew")
        self.pdf_list_scrollbar.grid(row=1, column=3, columnspan=1, sticky="ns")  # 添加这行
        self.pdf_list_scrollbar.config(command=self.pdf_listbox.yview)

        # 实现pdf_listbox的条目双击后打开pdf文件
        def open_pdf(event):
            selected_index = self.pdf_listbox.curselection()
            if selected_index:
                selected_pdf = self.pdf_listbox.get(selected_index)
                pdf_path = os.path.join(self.pdf_folder_path, selected_pdf)
                if os.path.exists(pdf_path):
                    os.startfile(pdf_path)
                else:
                    messagebox.showerror("Error", "PDF file not found!")

        self.pdf_listbox.bind("<Double-Button-1>", open_pdf)

        # --- 右侧功能区 ---
        self.classify_frame = tk.LabelFrame(self.right_frame, text="Video Classification Result", padx=10, pady=10)
        self.classify_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # 创建按钮和状态标签的容器框架
        self.button_frame = tk.Frame(self.classify_frame)
        self.button_frame.pack(pady=10, anchor='w')

        self.btn_classify_videos = tk.Button(self.button_frame, text="Start >>",
                                             command=self.start_video_classification)
        self.btn_classify_videos.pack(side="left", padx=5)

        self.btn_open_log = tk.Button(self.button_frame, text="Open Log", command=lambda: os.startfile('log.txt'))
        self.btn_open_log.pack(side="left", padx=5)

        self.classification_status_label = tk.Label(self.button_frame, text="Status: Ready")
        self.classification_status_label.pack(side="left", padx=5)

        # 分类结果表格
        self.result_tree = ttk.Treeview(self.classify_frame, columns=('time', 'video', 'script'), show='headings')
        self.result_tree.heading('time', text='Time')  # 完成时间 -> Time
        self.result_tree.heading('video', text='Video File')  # Video文件 -> Video File
        self.result_tree.heading('script', text='Matched Script')  # 匹配Script -> Matched Script

        # 设置列宽
        self.result_tree.column('time', width=180)
        self.result_tree.column('video', width=300)
        self.result_tree.column('script', width=300)

        # 添加双击事件处理
        def on_tree_double_click(event):
            item = self.result_tree.identify('item', event.x, event.y)
            column = self.result_tree.identify('column', event.x, event.y)

            if item:
                values = self.result_tree.item(item, 'values')
                if column == '#2' and values[1]:  # video列
                    video_path = os.path.join(self.video_folder_path, values[1])
                    if os.path.exists(video_path):
                        os.startfile(video_path)
                    else:
                        messagebox.showerror("Error", "Video file not found!")
                elif column == '#3' and values[2]:  # script列
                    script_path = os.path.join(self.pdf_folder_path, values[2])
                    if os.path.exists(script_path):
                        os.startfile(script_path)
                    else:
                        messagebox.showerror("Error", "Script file not found!")

        self.result_tree.bind('<Double-1>', on_tree_double_click)

        # 滚动条
        self.result_scrollbar = ttk.Scrollbar(self.classify_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=self.result_scrollbar.set)

        # 布局
        self.result_tree.pack(side="left", fill="both", expand=True, pady=5)
        self.result_scrollbar.pack(side="right", fill="y")

        self.result_list_scrollbar = tk.Scrollbar(self.classify_frame)
        self.result_list_scrollbar.pack(side="right", fill="y")
        self.result_listbox = tk.Listbox(self.classify_frame, width=60, height=20,
                                         yscrollcommand=self.result_list_scrollbar.set)
        self.result_listbox.pack(pady=5, fill="both", expand=True)
        self.result_list_scrollbar.config(command=self.result_listbox.yview)

        # log text增加滚动条
        self.log_scrollbar = tk.Scrollbar(self.classify_frame)
        self.log_scrollbar.pack(side="right", fill="y")

        # 重定向标准输出到控制台
        class TextRedirector(object):
            def write(self, str):
                # 如果str是换行符，不做任何处理
                if str == '\n':
                    return
                with open('./log.txt', 'a', encoding="utf8") as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + str + '\n')

        sys.stdout = TextRedirector()

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
                text=f"{self.video_folder_path}")  # 只显示文件夹名
            self.load_files_to_listbox(self.video_folder_path, self.video_listbox,
                                       ['.mxf'])
        else:
            messagebox.showinfo("Warning", "No video folder selected.")

    def select_pdf_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.pdf_folder_path = folder_selected
            self.pdf_folder_label.config(text=f"{self.pdf_folder_path}")  # 只显示文件夹名
            self.load_files_to_listbox(self.pdf_folder_path, self.pdf_listbox, ['.pdf'])
        else:
            messagebox.showinfo("Warning", "No script folder selected.")

    def load_files_to_listbox(self, folder_path, listbox_widget, allowed_extensions):
        listbox_widget.delete(0, tk.END)  # 清空现有列表
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Folder not exist！")
            return

        files = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item)[1].lower()
                if file_ext in allowed_extensions:
                    files.append(item)

        if not files:
            listbox_widget.insert(tk.END, "No matched file found in this folder.")
        else:
            for file_name in sorted(files):
                listbox_widget.insert(tk.END, file_name)

    def start_video_classification(self):
        if not self.video_folder_path or not os.path.exists(self.video_folder_path):
            messagebox.showwarning("Warning", "Please select a video folder！")
            return
        if not self.pdf_folder_path or not os.path.exists(self.pdf_folder_path):
            messagebox.showwarning("Warning", "Please select a script folder！")
            return

        # 清空之前的分类结果
        self.result_listbox.delete(0, tk.END)
        self.classification_status_label.config(text="Status: Classifying...")
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

        from app.main import extract_text_from_pdf, main
        pfs = [os.path.join(self.pdf_folder_path, pf) for pf in pdf_files]
        vfs = [os.path.join(self.video_folder_path, vf) for vf in video_files]

        pfs_info = {}
        for pf in pfs:
            pdf_name = os.path.basename(pf)
            self.classification_status_label.config(text=f"Status: Extracting {pdf_name}...")
            try:
                text = extract_text_from_pdf(pf)
                pfs_info[pf] = text

                # 设置对应的PDF Listbox条目为绿色
                for i in range(self.pdf_listbox.size()):
                    if self.pdf_listbox.get(i) == pdf_name:
                        self.pdf_listbox.itemconfig(i, {'fg': 'green'})
                        break
            except Exception as e:
                print(f"Error extracting {pdf_name}: {str(e)}")
                continue

        # 在_run_classification_logic方法中修改结果插入部分
        for vf in vfs:
            try:
                result = main(vf, pfs_info)
                current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                video_name = os.path.basename(vf)
                script_name = os.path.basename(result) if result else "未匹配"
                self.result_tree.insert('', 'end', values=(current_time, video_name, script_name))

                # 找到并设置对应的Listbox条目为绿色
                for i in range(self.video_listbox.size()):
                    if self.video_listbox.get(i) == video_name:
                        self.video_listbox.itemconfig(i, {'fg': 'green'})
                        break

            except Exception as e:
                error_traceback = traceback.format_exc()
                print("子线程捕获到异常:\n", error_traceback)
                return {"error": str(e), "traceback": error_traceback}

        return result

    def _on_classification_done(self, future):
        """
        分类逻辑执行完毕后的回调函数，在主线程中更新UI。
        """
        try:
            results = future.result()  # 获取分类结果
            self.classification_status_label.config(text="Status: Done")  # 修改状态为完成
            # for item in results:
            #     video, pdf = pathlib.Path(item[0]).name, pathlib.Path(item[1]).name
            #     result_line = f"Video: {video} -> Script: {pdf} "
            #     self.result_listbox.insert(tk.END, result_line)
        except Exception as e:
            self.classification_status_label.config(text=f"Status: Error！{e}")
            print("主线程捕获到异常:\n", traceback.format_exc())
            with open("error.log", "a", encoding="utf8") as log_file:
                log_file.write(f"Error occurred at {time.strftime('%Y-%m-%d %H:%M:%S')}:\n")
                log_file.write(traceback.format_exc())
                log_file.write("\n")
            messagebox.showerror("Error", f"WOW: {e}")
        finally:
            self.btn_classify_videos.config(state=tk.NORMAL)


# 创建Tkinter主窗口
root = tk.Tk()
app = FileClassifierApp(root)

# 运行主循环
root.mainloop()
