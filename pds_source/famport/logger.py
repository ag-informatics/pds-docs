from datetime import datetime

def record(issue):
    f = open("log.txt", "a+")
    errorReport = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  + ">> " + issue + "\n"
    f.write(errorReport)