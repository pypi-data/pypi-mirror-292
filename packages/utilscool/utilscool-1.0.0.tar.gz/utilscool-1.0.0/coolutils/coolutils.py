import requests
import json
import matplotlib.pyplot as plt
import multiprocessing as mp
import sqlite3
from time import sleep
from datetime import datetime
import functools

MARKERS = ['o', 's', '^', 'D', 'v', 'x', 'P', 'h', '+', '*'] #in order of best looking ones, in my opinion anyways ;)

#Send notification to phone via ntfy.sh | Delay can be either 30m,9am formats | Action: [(label, url),(label,url)]
def notify(route, msg = "",title="<>", private = False,priority = 3, action = None, delay=None, markdown_enabled = True):
    cache = "yes"
    if private:
        cache = "no"
    data = {
        "topic": route,
        "message": msg,
        "title": title,
        "priority": priority,
        "markdown":markdown_enabled,
    }

    if delay is not None:
        data["delay"] = delay
    if action is not None:
        #[{ "action": "view", "label": "Google", "url": "https://www.google.com/" }]
        data["actions"] = [{ "action": "view", "label": label, "url": f"https://{url}"} for label,url in action]
    requests.post(f"https://ntfy.sh/",
    data=json.dumps(data),
    headers={"Cache": cache })
    return True

ntfy = notify

oprint = print
RED = 91
GREEN = 92
YELLOW = 93
BLUE = 94
MAGENTA = 95
CYAN = 96
color_codes = {}
START_OF_LINE = "\033[F\r\033[K"

def print(text, end = "\n", color = None,move_cursor = "", delay_per_char = 0, delay_per_word = 0, delay_per_line = 0):
    color_codes = {None:"\033[0m", 91: '\033[91m', 92: '\033[92m', 93: '\033[93m', 94: '\033[94m', 95: '\033[95m', 96: '\033[96m'}
    oprint(move_cursor,end = color_codes[color])
    if delay_per_char == delay_per_word == delay_per_line == 0:
        oprint(text, end = end)
    else:
        lines = text.split("\n")
        words = [line.split(" ") for line in lines]
        for line in lines:
            for word in line:
                word = word + " "
                if delay_per_char > 0:
                    for char in word:
                        oprint(char,end = "")
                        sleep(delay_per_char)
                else:
                    oprint(word,end = "")
                if delay_per_word > 0:
                    sleep(delay_per_word)
            oprint("",end = "\n")
            if delay_per_line > 0:
                sleep(delay_per_line)
    oprint(color_codes[None],end = "")

#print("Hello",color=RED, move_cursor = START_OF_LINE)


#x_vals is None -> 0 to len; x_vals is float/int -> Starts from there; x_vals is tuple w/ two vals -> starts from there with steps of second val; x_vals is list, uses it as x_vals
def plot(y_vals,x_vals=None, labels = None,show = True,plt_title = 'Plot of X and Y Values',x_labels = 'X Values',y_labels = 'Y Values'):
    multiple = type(y_vals[0]) == list #if y_vals contains nested loop, multiple = True
    
    if multiple:
        markers = MARKERS[:max(1,min(10,round(len(y_vals)/2)))] #take 1 marker for every 2 new data sets. Max: 10, min 1
        if type(x_vals) != list:
            x_vals = [x_vals for _ in range(0,len(y_vals))]
        for i,x_val in enumerate(x_vals):
            y_val = y_vals[i]
            if x_val is None:
                x_val = [i for i in range(0,len(y_val))]
            elif type(x_val) == float or type(x_val) == int:
                x_val = [i+x_val for i in range(0,len(y_val))]
            elif type(x_val) == tuple and len(x_val) == 2:
                x_val = [(i*x_val[1])+x_val[0] for i in range(0,len(y_val))]
            elif type(x_val) == tuple:
                print("Warning: Avoid using tuple as x_vals. Use list instead")
            elif type(x_val) == list:
                pass
            else:
                print("x_val is incompatabile type")
                raise TypeError
            if type(y_val) != list:
                print("y_val is not a list")
                raise TypeError
            if labels is None:
                plt.plot(x_val, y_val, marker=markers[i%len(markers)],label = f'{i}')
            elif labels[i] is None:
                plt.plot(x_val, y_val, marker=markers[i%len(markers)],label = f'{i}')
            else:
                plt.plot(x_val, y_val, marker=markers[i%len(markers)],label = labels[i])
            plt.legend()
    else:
        if x_vals is None:
            x_vals = [i for i in range(0,len(y_vals))]
        elif type(x_vals) == float or type(x_vals) == int:
            x_vals = [i+x_vals for i in range(0,len(y_vals))]
        elif type(x_vals) == tuple and len(x_vals) == 2:
            x_vals = [(i*x_vals[1])+x_vals[0] for i in range(0,len(y_vals))]
        elif type(x_vals) == tuple:
            print("Warning: Avoid using tuple as x_vals. Use list instead")
        elif type(x_vals) == list:
            pass
        else:
            print("x_vals is incompatabile type")
            raise TypeError
        if type(y_vals) != list:
            print("y_vals is not a list")
            raise TypeError

        plt.plot(x_vals, y_vals, marker='o')
    
    plt.xlabel(x_labels)
    plt.ylabel(y_labels)
    plt.title(plt_title)
    plt.grid(True)
    if show:
        plt.show()

#Basic boilerplate for multiprocessing pool
class Multiprocess():
    def __init__(self):
        pass
    #args -> list of tuples | add_id -> provides id as first argument (useful if they are writing to seperate files)
    def pool(func, args, add_id = False):
        if add_id:
            for i,x in enumerate(args):
                args[i] = tuple([i] + list(x))
        pool = mp.Pool()
        results = pool.starmap(func, args)
        pool.close()
        pool.join()
        return results

    def run(funcs,args = None):
        processes = []
        for i,func in enumerate(funcs):
            processes.append(mp.Process(target=func,args=(args[i],)))
            processes[-1].start()
        for p in processes:
            p.join()

"""
def myfunc(i,a,b):
    print(f"{i}. {a}+{b}={a+b}")

Multiprocess.pool(myfunc,[(1,2,3),(4,5,6)])
"""
timer_start = None
def start_timer():
    global timer_start
    timer_start = datetime.now()

def get_timer():
    global timer_start
    if timer_start is None:
        return None
    return datetime.now() - timer_start

def retry(retries = 3, delay = 5, exponential_delay = False):
    """
    Retry decorator that retries a function a number of times before raising an exception.
    @retry(3,5)
    def myfunc():
        pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {i} failed: {e} | Args: {args} | Kwargs: {kwargs}")
                    print(f"Sleeping for {delay * (2**(i-1) if exponential_delay else 1)} seconds")
                    sleep(delay * (2**(i-1) if exponential_delay else 1))
            raise Exception(f"Failed after {retries} attempts")
        return wrapper
    return decorator


#Database class for sqlite3

class DatabaseCell():
    def __init__(self,row,col,fn,filename):
        self.row = row
        self.fn = fn
        self.filename = filename
        self.col = col

    def __getattr__(self,attr):
        filename = self.filename
        connection = sqlite3.connect(filename)
        crsr = connection.cursor()
        crsr.execute(f'SELECT {self.col} FROM {self.fn} WHERE id = ?', (self.row,))
        result = crsr.fetchone()
        connection.close()
        if result is not None:
            return result[0]
        else:
            return None

    def __setattr__(self,attr,value):
        filename = self.filename
        connection = sqlite3.connect(filename)
        crsr = connection.cursor()
        crsr.execute(f'UPDATE {self.fn} SET {self.col} = ? WHERE id = ?', (value, self.row))

class DatabaseRow():
    def __init__(self,row,fn,filename):
        self.row = row
        self.fn = fn
        self.filename = filename

    def __getitem__(self,col):
        return DatabaseCell(self.row,col,self.fn,self.filename)

    def __getattr__(self,attr):
        filename = self.filename
        connection = sqlite3.connect(filename)
        crsr = connection.cursor()
        crsr.execute(f'SELECT * FROM {self.fn} WHERE id = ?', (attr,))
        result = crsr.fetchone()
        connection.close()
        return result if result else []

    def __setattr__(self,attr,value):
        connection = sqlite3.connect(self.filename)
        crsr = connection.cursor()
        crsr.execute(f'UPDATE {self.fn} SET {", ".join([f"{self.col} = ?" for self.col in value])} WHERE id = ?', (*value, self.row))

    
class Database():
    #database name (str), columns (list of tuples) -> (name,[python/sqlite] datatype) | int,float,str supported
    def __init__(self,fn:str,columns:tuple,force_write = False):
        filename = "databases/" + fn + ".db"
        self.fn = fn
        self.filename = filename
        try:
            with open(filename) as f:
                pass
            if not force_write:
                return False
        except FileNotFoundError:
            pass
        with open(filename,"w+") as f:
            pass
        connection = sqlite3.connect(filename)
        crsr = connection.cursor()
        command = ""
        for name,dt in columns:
            if dt == int:
                datatype = "INTEGER"
            elif dt == float:
                datatype = "REAL"
            elif dt == str:
                datatype = "TEXT"
            else:
                datatype = dt
            command += f"{name} {datatype},"

        crsr.execute(f"CREATE TABLE {fn} ({command[:-1]})")
        connection.commit()
        connection.close()
        return True

    def __len__(self):
        fn = self.fn
        filename = self.filename
        connection = sqlite3.connect(filename)
        crsr = connection.cursor()
        crsr.execute(f"SELECT COUNT(*) FROM {fn}")
        return crsr.fetchall()[0][0]

    def append(self,values:tuple):
        fn = self.fn
        filename = self.filename
        connection = sqlite3.connect(filename)
        crsr = connection.cursor()
        crsr.execute(f'INSERT INTO {fn} VALUES {values};')
        connection.commit()

    def __getitem__(self,index):
        return DatabaseRow(index,self.fn,self.filename)

    def save(self,values:list):
        for value in values:
            self.append(value)

    #item (leave empty for all, else int)
    def get(self,num_results = None, offset = None):
        fn = self.fn
        filename = self.filename
        connection = sqlite3.connect(filename)
        crsr = connection.cursor()
        if num_results == None:
            crsr.execute(f"SELECT * FROM {fn}")
        else:
            crsr.execute(f"SELECT * FROM {fn} LIMIT {num_results} OFFSET {offset}")
        return crsr.fetchall()

    def __str__(self):
        return str(self.get())