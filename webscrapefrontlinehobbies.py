import pandas as pd
from selenium import webdriver
import re
import psycopg2
import datetime

# Set up the web driver
#driver = webdriver.Chrome(ChromeDriverManager().install())
chrome_driver_path = 'C:/Users/Admin/Downloads/chromedriver-win64/chromedriver.exe'
driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get("https://www.frontlinehobbies.com.au")
driver.maximize_window()

#Navigate to the kyosho filtered page
rc_button = driver.find_element_by_xpath('//*[@id="n_home"]/div[3]/div[3]/div/div[1]/div/div[2]/div/div[1]/a')
rc_button.click()
rc_car_buttom = driver.find_element_by_xpath('//*[@id="n_home"]/div[2]/div/div[2]/a')
rc_car_buttom.click()
rc_kyosho_filter = driver.find_element_by_xpath('//*[@id="FilterByBrand"]/a[2]')
rc_kyosho_filter.click()

# Get the total number of pages to scrape
pagination = driver.find_element_by_xpath('//ul[contains(@class, "pagination")]')
pages = pagination.find_elements_by_tag_name('li')
last_page = 0
last_page = int(pages[-2].text)
current_page = 1

# Create empty lists to store the scraped data
companyname, date, product_name, product_price, product_rating, availability, product_link, sku, correctsku, product_reviews = [], [], [], [], [], [], [], [], [], []

# Loop through each page and extract the product links
while current_page <= last_page:
    details = driver.find_elements_by_class_name('m_caption')

    for detail in details:
        #Get the link of all products
        product_link.append(detail.find_element_by_css_selector('.m_view').get_attribute("href"))

    try:
        #Click next page button
        new_page = driver.find_element_by_xpath('//a[contains(@aria-label, "Go forward")]')
        new_page.click()
    except:
        break

# Loop through each product link and extract the data
for link in product_link:
    driver.get(link)
    date.append(datetime.date.today().strftime("%Y-%m-%d"))
    companyname.append("frontline hobbies")
    product_name.append(driver.find_element_by_xpath('//h1[@aria-label="Product Name"]').text)
    product_price.append(driver.find_element_by_xpath('//div[@itemprop="price"]').text.replace('$', '').replace(',','').replace('NOW ', ''))
    product_rating.append('0 out of 5 stars')
    availability.append(driver.find_element_by_css_selector('span[itemprop="availability"]').text)
    product_reviews.append('No reviews')
    sku_text = driver.find_element_by_css_selector('span[itemprop="sku"]').text
    sku.append(sku_text)
    correctsku.append(re.sub(r'TRA-?(\d+)-?(\d*[A-Z]*)', r'TRA\1-\2', re.sub('_', '', re.sub(r'T(\d+)([A-Z])?$', r'T\1', sku_text))))
    #re.sub(r'T(\d+)([A-Z])?$', r'T\1', sku_text)

# Quit the web driver after all product links have been scraped
driver.quit()

# Define PostgreSQL database connection parameters
db_params = {
    "dbname": "frontlinehobbies",
    "user": "postgres",
    "password": "password12345",
    "host": "localhost",
    "port": "5432",
}

# Create a DataFrame and drop duplicate rows based on SKU and ProductName
data = {"Date": date, "CompanyName": companyname, "ProductName": product_name, "ScrapedSKU": sku, "Price": product_price, "Rating": product_rating, "InStock": availability, "Reviews": product_reviews}
df = pd.DataFrame(data)
df.insert(4, 'SKU', correctsku)
df.drop_duplicates(subset=['ScrapedSKU', 'ProductName'], keep='first', inplace=True)

# Apply transformations to columns
df['InStock'] = df['InStock'].apply(lambda x: 'Yes' if x in ['In Stock', 'In Stock at Warehouse'] else 'No')
df = df.assign(**{'ProductName': df['ProductName'].str.replace('"|,', '')})
# Convert the datatype of Price column from string to float
df['Price'] = df['Price'].astype(float)

#Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Insert data into the PostgreSQL table
    for row in df.itertuples(index=False):
        cursor.execute(
            """
            INSERT INTO public.scrapeddata (scrape_date, company_name, product_name, scraped_sku, price, fixed_sku, rating, in_stock, review)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (row.Date, row.CompanyName, row.ProductName, row.ScrapedSKU, row.Price, row.SKU, row.Rating, row.InStock, row.Reviews)
        )
    conn.commit()
    cursor.close()
    conn.close()
    print("Data inserted into the database successfully")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)

# Generate a CSV file
df.to_csv("frontlinehobbies-sept142023.csv", index=False)
