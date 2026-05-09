import os 
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import platform
import subprocess
from apex.config.settings import config
from apex.rag.rag import search_code, _bm25 as rag_bm25
import apex.rag.rag as rag
OS = platform.system()

DANGEROUS_WINDOW = [
    "del /f",           
    "del /s",           
    "del /q",           
    "rmdir /s",         
    "format",         
    "rd /s",            
    "shutdown",         
    "shutdown /r",     
    "taskkill /f",      
    "reg delete",       
    "cipher /w",        
    "bcdedit",          
    "diskpart",        
    "sfc /scannow",     
    "netsh",           
    "drop table",       
    "truncate",
]
 
DANGEROUS_LINUX = [
    "rm -rf",
    "rm -rf/",
    "rm -rf*",
    "dd ",              
    "mkfs",             
    "fdisk",          
    "shutdown",         
    "reboot",           
    "kill -9",          
    "killall",          
    ":(){:|:&};:",      
    "chmod 777 /",      
    "chown -r",         
    "mv /* /dev/null", 
    "> /dev/sda",       
    "shred",            
    "drop table",       
    "truncate",      
]
 
DANGEROUS_MAC = [
    "rm -rf",           
    "rm -rf /",         
    "rm -rf *",         
    "dd ",           
    "diskutil",        
    "shutdown",        
    "reboot",           
    "kill -9",          
    "killall",         
    ":(){:|:&};:",      
    "chmod 777 /",      
    "chown -r",         
    "mv /* /dev/null",  
    "csrutil disable",  
    "nvram",            
    "shred",           
    "drop table",       
    "truncate",      
]
 
DANGEROUS_UNIVERSAL = [
    "drop table",
    "drop database",
    "truncate",
    "delete from",
]

def dangerous_cmd() -> list :
    if OS == "windows":
        return DANGEROUS_WINDOW + DANGEROUS_UNIVERSAL
    elif OS == "Linux":
        return DANGEROUS_LINUX + DANGEROUS_UNIVERSAL
    elif OS == "Darwin":
        return DANGEROUS_MAC + DANGEROUS_UNIVERSAL
    else :
        return DANGEROUS_WINDOW + DANGEROUS_LINUX + DANGEROUS_MAC + DANGEROUS_UNIVERSAL
    
def is_dangerous(commands : str) :
    command_lower = commands.lower()
    return any(danger in command_lower for danger in dangerous_cmd())

def read_file(path : str) -> str:
    try : 
        with open(path, "r" , encoding = "utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error : {e}"
    
def list_dir(path : str) -> str:
    try:
        item = os.listdir(path)
        return "\n".join(item)
    except Exception as e:
        return f"Error : {e}"
    
def delete_file(path : str) -> str:
    print(f"> APEX want to delete file : {path}")
    confirm = input("> Allow (yes / no) : ").strip().lower()
    if confirm != 'yes':
        return "Delete block by user !"
    
    try : 
        os.remove(path)
        return f"File deleted successfully : {path}"
    except Exception as e:
        return f"Error : {e}"
    
def fix_code(path : str, error_message : str) -> str:
    """
    Read a file and return a prompt-ready string for the LLM to fix it.
    The LLM will call write_file with the correct code.
    """

    try:
        with open(path , 'r') as f:
            code = f.read()
        return f"""
                FILE : 
                {path}

                Error_Message:
                {error_message}

                CODE : 
                {code}

                Fix the code above based on the error. Return the complete corrected file content.
                """
    except Exception as e:
        return f"Erro : {e}"
    
def write_file(path : str , content = "") -> str:
    if os.path.exists(path):
        if config.get("auto_mode") == True:
            pass
        else:
            print("> Do you want to over write file : ")
            confirm = input("> Allow (yes / no) : ").strip().lower()
            if confirm != 'yes':
                return f"> User denied to over write the file : {path}"
        
    try :
        with open(path , "w" , encoding = "utf-8") as f:
            f.write(content)
        return f"File written successfully : {path}"
    except Exception as e:
        return f"Error : {e}" 

def run_cmd(commands):
    """
    Runs terminal commands with safety checks.
    Args:
        commands: Command string to execute
    Returns:
        Output of command or error message
    """ 
    if is_dangerous(commands):
        print("⚠️ Warning - This command is dangerous")
        if config.get("auto_mode") == True:
            pass
        else :
            print(f"> {commands}")
            confirm = input("> Allow (yes / no) : ").strip().lower()
            if confirm != 'yes':
                return "> Command blocked for safety !"
        
    elif config.get("auto_run_commands") == False:
        if config.get("auto_mode") == True:
            pass
        else : 
            print(f"> APEX want to run : {commands}")
            confirm = input("> Allow (yes / no) : ")
            if confirm != 'yes' :
                return "> User denied the command !"
        
    try : 
        result = subprocess.run(
            commands,
            shell = True,
            capture_output = True,
            text = True,
            timeout = 10,
            stdin = subprocess.DEVNULL
        )

        if result.stdout:
            return result.stdout
            
        if result.stderr:
            return result.stderr
            
        return f"Run command successfully : {commands}"
        
    except subprocess.TimeoutExpired:
        return f"> Command timed out after 30 seconds..."
    except Exception as e:
        
        return f"Error : {e}"
        
def find_relevant_code(query : str, path : str = None):
    if rag._bm25 is None:
        return "NO_RAG"
    return search_code(None , query)

REGISTRY = {
    "run_cmd"            : run_cmd,
    "write_file"         : write_file,
    "read_file"          : read_file,
    "list_dir"           : list_dir,
    "delete_file"        : delete_file,
    "fix_code"           : fix_code,
    "find_relevant_code" : find_relevant_code,
}