import os
import win32api
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def execute():
    def get_hd_name(drive_letter):
        try:
            return win32api.GetVolumeInformation(drive_letter)[0]
        except:
            return os.path.basename(drive_letter)

    def get_hd_name(drive_letter):
        try:
            return win32api.GetVolumeInformation(drive_letter)[0]
        except:
            return os.path.basename(drive_letter)


    def tree(directory, padding='', file_output=None, folder_count=0, file_count=0, progress_bar=None, total_items=None, current_item=[0]):
        try:
            print(padding[:-1] + '+--' + os.path.basename(directory) + '/', file=file_output)
            padding = padding + '   '
            files = []
            directories = []

            for f in os.listdir(directory):
                if os.path.isdir(os.path.join(directory, f)):
                    directories.append(f)
                else:
                    files.append(f)

            for d in directories:
                folder_count += 1
                current_item[0] += 1
                if progress_bar:
                    progress_bar["value"] = (current_item[0] / total_items) * 100
                    root.update_idletasks()
                folder_count, file_count = tree(os.path.join(directory, d), padding, file_output, folder_count, file_count, progress_bar, total_items, current_item)

            for f in files:
                file_count += 1
                current_item[0] += 1
                if progress_bar:
                    progress_bar["value"] = (current_item[0] / total_items) * 100
                    root.update_idletasks()
                print(padding + '|--' + f, file=file_output)
        except PermissionError:
            print(padding + '|--[Permissão Negada]', file=file_output)
        except FileNotFoundError:
            print(padding + '|--[Arquivo Não Encontrado]', file=file_output)

        return folder_count, file_count


    def count_items(directory):
        total_items = 0
        for root, dirs, files in os.walk(directory):
            total_items += len(dirs) + len(files)
        return total_items


    def executar_backup():
        path_to_directory = filedialog.askdirectory(title="Selecione a pasta para fazer o backup")
        if not path_to_directory:
            messagebox.showwarning("Atenção", "Nenhum diretório foi selecionado.")
            return
        
        directory_name = get_hd_name(path_to_directory)
        output_file_path = filedialog.asksaveasfilename(
            initialfile=f'{directory_name}_tree_view.txt',
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Salvar arquivo de backup"
        )
        
        if os.path.exists(path_to_directory):
            total_items = count_items(path_to_directory)
            progress_bar["value"] = 0
            progress_bar["maximum"] = 100
            root.update_idletasks()

            try:
                messagebox.showinfo("Processo", "Iniciando backup...")
                with open(output_file_path, 'w', encoding='utf-8') as file_output:
                    folder_count, file_count = tree(
                        path_to_directory, file_output=file_output, progress_bar=progress_bar, total_items=total_items
                    )
                    file_output.seek(0, 0)
                    file_output.write(f"Resumo do diretório '{directory_name}':\n")
                    file_output.write(f"Total de pastas: {folder_count}\n")
                    file_output.write(f"Total de arquivos: {file_count}\n\n")
                
                progress_bar["value"] = 100
                

                resumo = f"Backup concluído:\nTotal de pastas: {folder_count}\nTotal de arquivos: {file_count}\n\nBackup salvo em {output_file_path}"
                messagebox.showinfo("Backup concluído", resumo)
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro durante o backup: {str(e)}")
        else:
            messagebox.showerror("Erro", "O caminho especificado não foi encontrado.")


    def executar_busca():
        diretorio = filedialog.askdirectory(title="Selecione o diretório para busca")
        if not diretorio:
            messagebox.showwarning("Atenção", "Nenhum diretório foi selecionado.")
            return
        
        palavra = palavra_entry.get()
        if not palavra:
            messagebox.showerror("Erro", "Você deve inserir uma palavra para buscar.")
            return

        try:
            messagebox.showinfo("Processo", "Iniciando busca...")
            resultados = buscar_palavra(diretorio, palavra)
            if resultados:
                messagebox.showinfo("Resultados da Busca", "\n".join(resultados))
            else:
                messagebox.showinfo("Resultados da Busca", f"A palavra '{palavra}' não foi encontrada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro durante a busca: {str(e)}")


    def buscar_palavra(directory, palavra):
        resultados = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if palavra in f.read():
                            resultados.append(f"Palavra encontrada em: {file_path}")
                except Exception as e:
                    resultados.append(f"Erro ao ler {file_path}: {str(e)}")
        return resultados


    root = tk.Tk()
    root.title("BACKUP TREE")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)


    progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=0, column=0, columnspan=2, pady=10)

    
    backup_button = tk.Button(frame, text="Executar Backup", command=executar_backup)
    backup_button.grid(row=1, column=0, pady=5)


    palavra_label = tk.Label(frame, text="Palavra para buscar:")
    palavra_label.grid(row=2, column=0, pady=5)

    palavra_entry = tk.Entry(frame)
    palavra_entry.grid(row=2, column=1, pady=5)


    busca_button = tk.Button(frame, text="Executar Busca", command=executar_busca)
    busca_button.grid(row=3, column=0, columnspan=2, pady=5)


    return root.mainloop()
