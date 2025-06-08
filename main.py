from tkinter import messagebox, filedialog
from yt_dlp import YoutubeDL
import tkinter as tk
from tkinter import ttk
import re
import shutil

is_dark = False
save_path = ""

def toggle_theme():
    global is_dark

    is_dark = not is_dark

    bg = "#2e2e2e" if is_dark else "#ffffff"
    fg = "#ffffff" if is_dark else "#000000"
    btn_bg = "#444444" if is_dark else "#f0f0f0"

    root.configure(bg=bg)
    heading1.configure(bg=bg, fg=fg)
    label1.configure(bg=bg, fg=fg)
    url_entry.configure(bg=bg, fg=fg, insertbackground=fg)
    folder_label.configure(bg=bg, fg=fg)
    progress_bar.configure(style="dark.Horizontal.TProgressbar" if is_dark else "light.Horizontal.TProgressbar")
    audio_only_cb.configure(bg=bg, fg=fg, activebackground=bg, activeforeground=fg, selectcolor=bg)



    for widget in [download_btn, clear_btn, exit_btn, folder_btn]:
        widget.configure(bg=btn_bg, fg=fg, activebackground="#666" if is_dark else "#ddd", activeforeground=fg)


def choose_folder():
    global save_path
    folder_selected = filedialog.askdirectory()

    if folder_selected:
        save_path = folder_selected
        display_path = (save_path[:50] + '...') if len(save_path) > 53 else save_path
        folder_label.config(text=f"Save to {display_path}")

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = float(d.get('_percent_str', '0').strip().replace('%', ''))
        progress_bar["value"] = percent
        
        label1.config(text=f"Downloading.. {int(percent)}%")
        root.update_idletasks()

    elif d['status'] == 'finished':
        label1.config(text="📦 Merging audio & video...")
        root.update_idletasks()
         
def is_valid_url(url):
    return re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+', url)


def download_video():

    video_url = url_entry.get()

    if not video_url:
        messagebox.showwarning("Warning", "Enter a video URL first!!")
        return
    
    if not save_path:
        messagebox.showwarning("Warning", "Choose a folder to save the video!")
        return        

    if not is_valid_url(video_url):
        messagebox.showerror("Invalid URL", "Please enter a valid YouTube URL.")
        return

    if audio_only_var.get():
        # Download Audio Only
        if not shutil.which("ffmpeg"):
            messagebox.showerror("Missing Dependency", "FFmpeg is required for audio downloads.\nInstall it using:\nsudo apt install ffmpeg")
            return        

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': False,
            'no_color': True,
            'progress_hooks': [progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'final_ext': 'mp3',
        }
    else:

        ydl_opts = {
            'format': 'bv*+ba/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': False,
            'no_color': True,
            'progress_hooks': [progress_hook]

        }

    download_btn.config(state="disabled")
    clear_btn.config(state="disabled")
    folder_btn.config(state="disabled")

    try:
        label1.config(text="Starting Download...")
        progress_bar["value"] = 0
        root.update_idletasks()

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if audio_only_var.get():
            label1.config(text="✅ Audio Completed!")
            messagebox.showinfo("Success", "Audio downloaded successfully!")
            clear_entry()
        
        else:

            label1.config(text="✅ Video Completed!")
            messagebox.showinfo("Success", "Video downloaded successfully!")
            clear_entry()

    except Exception as e:
        messagebox.showerror("Error", f"[Error]: {e}")
        print(e)
    
    finally:
        download_btn.config(state="normal")
        clear_btn.config(state="normal")
        folder_btn.config(state="normal")


def clear_entry():
    url_entry.delete(0, tk.END)
    label1.config(text="Ready for next download")
    progress_bar["value"] = 0
    url_entry.focus()
    audio_only_var.set(False)

root = tk.Tk()
root.title("--- YouTube Video/Audio Downloader ---")
root.geometry('640x480')
root.resizable(True, True)

# Add after setting geometry
window_width = 640
window_height = 480
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f'{window_width}x{window_height}+{x}+{y}')

style = ttk.Style()
style.theme_use('default')
style.configure("light.Horizontal.TProgressbar", troughcolor="#eee", background="#4caf50")
style.configure("dark.Horizontal.TProgressbar", troughcolor="#444", background="#4caf50")


menubar = tk.Menu(root)
options_menu = tk.Menu(menubar, tearoff=0)
options_menu.add_command(label="Toggle Theme", command=toggle_theme)
menubar.add_cascade(label="Options", menu=options_menu)
root.config(menu=menubar)


heading1 = tk.Label(root, text="Enter YouTube Video URL :", font=("Arial", 12))
heading1.pack(pady=10)

url_entry = tk.Entry(root, width=50, font=("Arial", 12))
url_entry.pack(pady=5)


progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(pady=5)

label1 = tk.Label(root, text="Ready to download!", font=("Arial", 12))
label1.pack(pady=10)

folder_label = tk.Label(root, text="No folder selected", font=("Arial", 10), wraplength=600, justify="center")
folder_label.pack()

audio_only_var = tk.BooleanVar(value=False)
audio_only_cb = tk.Checkbutton(root, text="Audio Only", variable=audio_only_var, font=("Arial", 12), bg=root["bg"], fg=folder_label["fg"], activebackground=root["bg"], activeforeground=folder_label["fg"])
audio_only_cb.pack(pady=5)


folder_btn = tk.Button(root, text="Choose Folder", command=choose_folder, font=("Arial", 12), width=20, height=2)
folder_btn.pack(pady=5)

download_btn = tk.Button(root, text="Download", command=download_video, font=("Arial", 12), width=20, height=2)
download_btn.pack(pady=5)

clear_btn = tk.Button(root, text="Clear", command=clear_entry, font=("Arial", 12), width=20, height=2)
clear_btn.pack(pady=5)

exit_btn = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12), width=20, height=2)
exit_btn.pack(pady=5)

root.bind('<Return>', lambda event: download_video())

if __name__ == '__main__':
    toggle_theme()    
    root.mainloop()