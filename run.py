# run.py
import threading
import game
from UI import root  # 确保 UI.py 有 root = tk.Tk()

def start_game():
    # 调用 game.py 的主循环
    game.main_loop()

if __name__ == "__main__":
    # 1) 新开一个线程运行 Pygame
    t = threading.Thread(target=start_game, daemon=True)
    t.start()

    # 2) 主线程运行 Tkinter
    root.mainloop()
