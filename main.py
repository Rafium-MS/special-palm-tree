from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
import sys
import schedule
import time
from threading import Thread
from scraping.territorios_scraper import executar_scraper

def main():
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec_())
def agendar_scraping_diario():
    schedule.every().day.at("17:00").do(executar_scraper)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    Thread(target=agendar_scraping_diario, daemon=True).start()
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec_())
