import tabula

# Read pdf into DataFrame
# df = tabula.read_pdf("/home/manan/Desktop/tabula.pdf", pages='all')
tabula.convert_into("/home/manan/Desktop/tabula.pdf", "output.csv", output_format="csv")

# print(df)