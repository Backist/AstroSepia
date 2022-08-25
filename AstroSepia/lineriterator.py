from pathlib import Path
import os
import mmap
import pathlib


def get_file_lines(file) -> list[int]:
    with open(file, "r+") as myfile:
        mm = mmap.mmap(myfile.fileno(), 0)
        total_lines = 0

        while mm.readline():
            total_lines += 1
    return total_lines

def get_files_dir(path: os.PathLike | pathlib.Path) -> list[str]:
    """Detorna una lista con el nombre de todos los archivos del directorio. Si se encuentra un subdirectorio, se retorna una lista con todos los archivos"""
    main_path = os.scandir(path)
    for files in main_path:
        if files.is_file():
            return [files.name]
        elif files.is_dir():
            sub_dir = os.listdir(path.joinpath(f"{files}"))
            return get_files_dir(sub_dir)
    


all_files = os.scandir("C:\\Users\\Usuario\\Desktop\\Programacion\\AstroSepia\\AstroSepia")
filist = []


for filen in all_files:
    if filen.is_file():
        if filen.name.endswith(".py"):
            file = Path(f"C:\\Users\\Usuario\\Desktop\\Programacion\\AstroSepia\\AstroSepia\\{filen.name}")
            glf = get_file_lines(file)
            filist.append(glf)
        else:
            pass
    elif filen.is_dir:
        scanldir = os.scandir(f"C:\\Users\\Usuario\\Desktop\\Programacion\\AstroSepia\\AstroSepia\\{filen.name}")
        for filen in scanldir:
            if filen.is_file():
                if filen.name.endswith(".py"):
                    file = Path(f"C:\\Users\\Usuario\\Desktop\\Programacion\\AstroSepia\\AstroSepia\\{filen.name}")
                    glf = get_file_lines(file)
                    filist.append(glf)
            elif filen.is_dir:
                scanldir = os.scandir(f"C:\\Users\\Usuario\\Desktop\\Programacion\\AstroSepia\\AstroSepia\\{filen.name}")
                for filen in scanldir:
                    if filen.is_file():
                        if filen.name.endswith(".py"):
                            file = Path(f"C:\\Users\\Usuario\\Desktop\\Programacion\\AstroSepia\\AstroSepia\\{filen.name}")
                            glf = get_file_lines(file)
                            filist.append(glf)
            else:
                pass
for i in filist:
    print(sum(i))



