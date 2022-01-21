# written by Jeemin Kim
# Jan 16, 2022
# github.com/mrharrykim

from tkinter import E, HORIZONTAL, N, W, S, StringVar, Tk, messagebox, ttk, Listbox, MULTIPLE, Message
from ropto  import get_namespace, main
from lib.security import decrypt

namespace = get_namespace()

# structure
root = Tk()
root.title("ROPTO")
main_frame = ttk.Frame(root, borderwidth=1, relief="solid")

input_frame = ttk.Frame(main_frame)

address_listbox_frame = ttk.Frame(input_frame)
with open(namespace.file, "r", encoding="UTF-8") as file:
    address_dump = file.read()
    if  len(address_dump) > 0:
        address_list = address_dump.split("\n")
    else:
        address_list = []
address_var = StringVar(value=address_list)
address_listbox = Listbox(address_listbox_frame, listvariable=address_var, selectmode=MULTIPLE)

entry_frame = ttk.Frame(input_frame)

def delete_address():
    global address_list
    selected_indices = address_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("입력 오류", "선택된 주소가 없습니다.")
    new_address_list = [address for i, address in enumerate(address_list) if i not in selected_indices]
    address_list = new_address_list
    address_var.set(address_list)

def handle_address_listbox_event(e):
    delete_address()

address_listbox.bind("<KeyRelease-Delete>", handle_address_listbox_event)
address_listbox.bind("<KeyRelease-BackSpace>", handle_address_listbox_event)
delete_address_button = ttk.Button(entry_frame, text="삭제", command=delete_address)

new_address = StringVar()
new_address_entry = ttk.Entry(entry_frame, textvariable=new_address)

def add_address():
    address = new_address.get()
    if len(address) == 0:
        return
    new_address_entry.delete(0, len(address))
    address_list.append(address)
    address_var.set(address_list)

def handle_new_address_entry_event(e):
    add_address()
new_address_entry.bind("<KeyRelease-Return>", handle_new_address_entry_event)
add_address_button = ttk.Button(entry_frame, text="추가", command=add_address)

seperator1 = ttk.Separator(entry_frame, orient=HORIZONTAL)

set_start_var = StringVar(value="T" if namespace.set_start else False)

def set_set_start():
    namespace.set_start = True if set_start_var.get() == "T" else False

set_start_label = ttk.Label(entry_frame, text="처음 주소를 시작 주소로")
set_start_checkbutton = ttk.Checkbutton(entry_frame, variable=set_start_var, onvalue="T", offvalue="F", command=set_set_start)

no_return_var = StringVar(value="T" if namespace.no_return else False)

def set_no_return():
    namespace.no_return = True if no_return_var.get() == "T" else False

no_return_label = ttk.Label(entry_frame, text="시작 주소로 귀환하지 않음")
no_return_checkbutton = ttk.Checkbutton(entry_frame, variable=no_return_var, onvalue="T", offvalue="F", command=set_no_return)

seperator2 = ttk.Separator(entry_frame, orient=HORIZONTAL)

verbose_var = StringVar(value=namespace.verbose)

def set_verbose():
    namespace.verbose = int(verbose_var.get())

verbose_label = ttk.Label(entry_frame, text="출력 정보량")
verbose_spinbox = ttk.Spinbox(entry_frame, from_=1, to=1, textvariable=verbose_var, command=set_verbose)

output_frame = ttk.Frame(main_frame)
message = StringVar()
output_message = Message(output_frame, textvariable=message, borderwidth=1, relief="solid", padx=5, pady=5)

passwd_var = StringVar()
password_entry = ttk.Entry(entry_frame, textvariable=passwd_var, show="*")

def run_main():
    passwd = passwd_var.get()
    if len(passwd) == 0:
        messagebox.showwarning("입력 오류", "비밀번호를 입력하세요.")
        return
    password_entry.delete(0, len(passwd))
    secret = decrypt(passwd)
    if not secret:
        messagebox.showerror("인증 오류", "비밀번호가 잘못되었습니다.")
        return
    with open(namespace.file, "w", encoding="UTF-8") as file:
        file.write("\n".join(address_list))
    message.set(main(namespace, secret))

def handle_passwd_entry_event(e):
    run_main()

password_entry.bind("<KeyRelease-Return>", handle_passwd_entry_event)
run_button = ttk.Button(entry_frame, text="실행", command=run_main)


# geometry
root.geometry("750x400")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.grid(column=0, row=0, sticky=(N, E, S, W))

main_frame.columnconfigure(0, weight=0)
main_frame.rowconfigure(0, weight=1)
input_frame.grid(column=0, row=0, sticky=(N, E, S, W))
input_frame["padding"] = 5

input_frame.columnconfigure(0, weight=1)
input_frame.rowconfigure(0, weight=1)
address_listbox_frame.grid(column=0, row=0, sticky=(N, E, S, W))
address_listbox_frame["padding"] = 5

address_listbox_frame.columnconfigure(0, weight=1)
address_listbox_frame.rowconfigure(0, weight=1)
address_listbox.grid(column=0, row=0, sticky=(N, E, S, W))

entry_frame.grid(column=0, row=1, sticky=(N, E, S, W))
entry_frame["padding"] = (5, 0, 5, 5)
delete_address_button.grid(column=1, row=0, padx=(5, 0), sticky=E)
delete_address_button["width"] = 5

new_address_entry.grid(column=0, row=1, pady=(5, 0))
add_address_button.grid(column=1, row=1, padx=(5, 0), pady=(5, 0), sticky=E)
add_address_button["width"] = 5

seperator1.grid(column=0, columnspan=2, row=2, pady=5, sticky=(N, E, S, W))

set_start_label.grid(column=0, row=3, sticky=W)
set_start_checkbutton.grid(column=1, row=3)
no_return_label.grid(column=0, row=4, sticky=W)
no_return_checkbutton.grid(column=1, row=4)

seperator2.grid(column=0, columnspan=2, row=5, pady=5, sticky=(N, E, S, W))

verbose_label.grid(column=0, row=6, sticky=W)
verbose_spinbox.grid(column=1, row=6, padx=(5, 0))
verbose_spinbox["width"] = 3

password_entry.grid(column=0, row=7, pady=(5, 0))
run_button.grid(column=1, row=7, padx=(5, 0), pady=(5, 0))
run_button["width"] = 5

main_frame.columnconfigure(1, weight=1)
output_frame.grid(column=1, row=0, sticky=(N, E, S, W))
output_frame["padding"] = (0, 10, 10, 10)

output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(0, weight=1)
output_message.grid(column=0, row=0, sticky=(N, E, S, W))

# debug
# entry_frame["borderwidth"] = 2
# entry_frame["relief"] = "solid"

root.mainloop()