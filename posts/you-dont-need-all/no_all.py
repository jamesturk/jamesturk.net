class NoImportStar(Exception):
    def __init__(self):
        super().__init__(f"from {__name__} import * is not allowed!")

    def __getitem__(self, i):
        raise NoImportStar()

__all__ = NoImportStar()
