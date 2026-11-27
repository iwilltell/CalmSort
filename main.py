from core.sorter_engine import SorterEngine
from storage.history_manager import HistoryManager
from ui.app_window import AppWindow


def main():
    history_manager = HistoryManager(data_dir="data")
    engine = SorterEngine(history_manager=history_manager)
    app = AppWindow(engine=engine, history_manager=history_manager)
    app.mainloop()


if __name__ == "__main__":
    main()
