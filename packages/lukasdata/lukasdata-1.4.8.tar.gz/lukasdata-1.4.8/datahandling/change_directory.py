import os
import getpass

username = getpass.getuser()

def chdir_bachelor():
      os.chdir(f"C:/Users/{username}/Desktop/bachelor")

def chdir_data():
      os.chdir(f"C:/Users/{username}/Desktop/bachelor/data")

def chdir_id():
      os.chdir(f"C:/Users/{username}/Desktop/bachelor/data/id")

def chdir_sql():
      if username == "lukas":
            os.chdir("E:\sql")
      if username=="Lukas":
            os.chdir("C:\sql")
      
def chdir_sql_requests():
    os.chdir(f"C:/Users/{username}/Desktop/bachelor/data/sql_data")   

def chdir_pdf():
      os.chdir(f"C:/Users/{username}/Desktop/bachelor/pdf") 

def chdir_auth():
      os.chdir(f"C:/Users/{username}/Desktop/bachelor/auth")    

def chdir_txt():
      os.chdir(f"C:/Users/{username}/Desktop/bachelor/txt")    

def chdir_fig():
      os.chdir(f"C:/Users/{username}/Desktop/bachelor/data/figures")          

def switch_dir(type):
      if type =="pdf":
            chdir_pdf()
      if type == "json":
            chdir_data()