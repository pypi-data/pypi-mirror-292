
import xlwings as xw
def returnAsWB(wb):
    if isinstance(wb,str):
        # This is path
        out_wb = xw.Book(wb)

    elif isinstance(wb,xw.main.Book):
        out_wb = wb
    else:
        return "Not Valid input"
    return out_wb