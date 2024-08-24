
import xlwings as xw
from typing import Union
from pathlib import Path

def return_as_wb(
        wb,
        read_only: Union[str,bool] = False):
    import warnings
    from pathlib import Path
    if isinstance(wb,(str,Path)):
        # This is path
        if read_only in ["auto"]:
            try:
                out_wb = xw.Book(wb, read_only=False)
            except:
                out_wb = xw.Book(wb, read_only=True)
                warnings.warn(f"Read only is set to True. Because there's an error when using interactive mode.")
        elif isinstance(read_only,bool):
            out_wb = xw.Book(wb, read_only=read_only)

    elif isinstance(wb,xw.main.Book):
        out_wb = wb
    else:
        return "Not Valid input"
    return out_wb

del Union
del Path