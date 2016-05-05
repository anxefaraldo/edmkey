import xlrd
import xlwt


def xls_to_key_annotations(excel_file, sheet_index, export_directory):

    excel_file = xlrd.open_workbook(excel_file)
    spreadsheet = excel_file.sheet_by_index(sheet_index)

    for row in range(spreadsheet.nrows):
        v = spreadsheet.row_values(row)
        txt = open(export_directory + '/' + v[0] + '.key', 'w')
        if len(v[1]) > 3:
            txt.write(v[1] + '\n')
        else:
            txt.write(v[1] + ' major\n')
        txt.close()


def matrix_to_excel(my_matrix,
                    label_rows=('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'),
                    label_cols=('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'),
                    filename='matrix.xls'):

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1')

    start_row = 1
    for label in label_rows:
        ws.write(start_row, 0, label)
        start_row += 1

    start_col = 1
    for label in label_cols:
        ws.write(0, start_col, label)
        start_col += 1

    next_row = 1
    next_col = 1
    for row in my_matrix:
        col = next_col
        for item in row:
            ws.write(next_row, col, item)
            col += 1
        next_row += 1

    wb.save(filename)
