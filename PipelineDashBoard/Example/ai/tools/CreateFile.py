from langchain.tools import tool
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@tool
def create_file(file_content) -> bool:
    """
        Tool to create file
        Args:
           file_content(str): the file content
        
        Returns:
          Boolean: create file success or failed
    """
    try:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(file_content)
        print("HTML 文件已创建：index.html")
        return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
