import setup_tests
import tkinter as tk
from RTE.views.editor_window import EditorFrame

if __name__ == "__main__":
    root = tk.Tk()
    gui = EditorFrame(root)
    gui.pack(side="top", fill="both", expand=True)
    gui.text.insert("end", "one\ntwo\nthree\n")
    gui.text.insert("end", "four\n")
    gui.text.insert("end", "five\n")
    print(gui.text.index("current linestart"))
    root.mainloop()
