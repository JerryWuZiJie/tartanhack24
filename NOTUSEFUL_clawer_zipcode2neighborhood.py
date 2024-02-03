import requests
from bs4 import BeautifulSoup

# URL of the page containing the table with zip codes
url = 'https://www.zip-codes.com/city/pa-pittsburgh.asp#zipcodes'

# Send a GET request to the URL
response = requests.get(url)

# If the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with id 'tblZIP'
    table = soup.find('table', id='tblZIP')
    
    # Find all the rows in the table body (ignoring the header row)
    rows = table.tbody.find_all('tr')
    
    with open('output.txt', 'w') as outfile:
        # Iterate over each row and extract the data
        for row in rows:
            # Find all the data cells (td) in the row
            cells = row.find_all('td')
            
            # Extract the text from each cell
            data = [cell.text.strip() for cell in cells]

            outfile.write(str(data))
            outfile.write('\n')

else:
    print('Failed to retrieve the page. Status code:', response.status_code)
