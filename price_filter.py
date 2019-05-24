import sqlite3
from bs4 import BeautifulSoup as bs
import requests as req
import xlsxwriter
import pandas as pd

conn = sqlite3.connect('product.db')
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS filter")
c.execute("CREATE TABLE IF NOT EXISTS filter (product 'TEXT' , price 'TEXT', rating 'TEXT', review 'TEXT')")

workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet("Sheet1")

index = 1
query = input('Enter Product: ')
#can also check formax,min, range between them
filter_price = int(input("enter your budget(maximum): "))
for i in range (0,6):
    url="https://www.flipkart.com/search?q="+query+"&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page="+str(i)
#url="https://www.flipkart.com/search?q="+input('Enter Product:')+"&as=on&as-show=on&otracker=AS_Query_TrendingAutoSuggest_1_0&otracker1=AS_Query_TrendingAutoSuggest_1_0&as-pos=1&as-type=TRENDING"
    page=1

    s=bs(req.get(url).text,'html.parser')
    prd=[p.text for p in s.find_all('div',class_="_3wU53n")]
    price=[p.text [1:] for p in s.find_all('div',attrs={'class':'_1vC4OE'})]  #crops symbol
    rating=[p.text for p in s.find_all('span',class_="_38sUEc")]

    if index is 1:
        print("product".ljust(50), '\t', "price".ljust(20), '\t', "rating".ljust(20), '\t', "reviews")
        print('-' * 120)
        index += 1
    for pd,pr,ra in zip(prd,price,rating):

        #convertto int and remove $
        if int(pr.replace(',','')) <= filter_price:
            print(str(pd).ljust(50), '\t','Rs.'+str(pr).ljust(20),str(ra)[0:str(ra).index("Ratings")].ljust(20),'\t',str(ra)[str(ra).index("&")+2:str(ra).index("Reviews")])
            c.execute("INSERT INTO filter(product,price,rating,review) VALUES (?,?,?,?)",(str(pd), str(pr), str(ra)[0:str(ra).index(" Ratings")], str(ra)[str(ra).index("&")+2:str(ra).index(" Reviews")]))  # inserts with id 1
            conn.commit()

print("values stored to db")


## sql to csv file
c.execute('select * from filter')
results = c.fetchall()
#for r in results:
#    print(r)
print(results)

#to highlight cells
bold = workbook.add_format({'bold': True})
worksheet.write('A1', "product", bold)
worksheet.write('B1', "price", bold)
worksheet.write('C1', "rating", bold)
worksheet.write('D1', "review", bold)
# Start from the first cell. Rows and
# columns are zero indexed.
row = 1
col = 0
# Iterate over the data and write it out row by row.
for product, price, rating, review in (results):
    worksheet.write(row, col, product)
    worksheet.write(row, col + 1, price)
    worksheet.write(row, col + 2, rating)
    worksheet.write(row, col + 3, review)
    row += 1


print("finished")
c.close()
conn.close()
workbook.close()

''' #by pandas
f = open('output.csv', 'w')
c.execute('select * from filter')
# Get data in batches
while True:
    # Read the data
    df = pd.DataFrame(c.fetchmany(1000))
    # We are done if there are no data
    if len(df) == 0:
        break
    # Let's write to the file
    else:
        df.to_csv(f, header=False)
#f.close()

df = pd.read_sql(sql, conn)
df.to_csv('output.csv')
'''