from datetime import datetime

now = datetime.now().strftime("%Y%m%d%H%M")
filename = f"hello_{now}.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write("안녕하세요")

