import logging
import datetime

#* ////////////
#*  COLORS
#* ////////////

    #\33[30m	Black
    #\33[31m	Red
    #\33[32m	Green
    #\33[33m	Yellow
    #\33[34m	Blue
    #\33[35m	Purple
    #\33[36m	Cyan
    #\33[37m	White

#? Add \33[1m\33[<ansiref>]{FMT}\33[0m to add bolb messages


FMT = "[{levelname:^4}] [{name}] {asctime}: {message}"
FORMATS = {
    logging.DEBUG: FMT,
    logging.INFO: f"\33[32m{FMT}\33[0m",            #* Green
    logging.WARNING: f"\33[1m\33[95m{FMT}\33[0m",   #* Cyan
    logging.ERROR: f"\33[31m{FMT}\33[0m",           #* Red
    logging.CRITICAL: f"\33[1m\33[31m{FMT}\33[0m",  #* Bold Red
}


class CustomFmt(logging.Formatter):
    def format(self, entry):
        log_fmt = FORMATS[entry.levelno]
        formatter = logging.Formatter(log_fmt, style="{")
        return formatter.format(entry)

handler = logging.StreamHandler()
handler.setFormatter(CustomFmt())
logging.basicConfig(
    level= logging.INFO,
    handlers=[handler],
    datefmt= datetime.datetime.now().astimezone(),
)

def Logger(level, text: str) -> str:
    """Funcion para formatear mensajes de terminal rapidamente.\n
    'i' -> info\n
    'w' -> warn\n
    'c' -> critical\n
    'e' -> error\n
    """
    log = logging.getLogger("STARTUP")

    if level == "i":
        return log.info(text)
    elif level == "w":
        return log.warn(text)
    elif level == "c":
        return log.critical(text)
    elif level == "e":
        return log.error(text)
    else:
        return "Ha ocurrido un error. Establezca ['i', 'w', 'c' o 'e'] como valores para el parametro ['level']"







