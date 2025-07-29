import os

def ContextWriter(data,path):
    with open(path, "w") as file:
        content = file.write(data)
        print ("上下文写入完成")
