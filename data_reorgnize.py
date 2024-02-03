# Open the input file in read mode and the output file in write mode
with open('zipcodeMapping.txt', 'r') as infile, open('output.txt', 'w') as outfile:
    # Read the line from the input file
    line = infile.readline()
    
    # Remove the trailing semicolon if present and split the line into individual items
    items = line.strip(';').split(',')
    
    # Write each item on its own line in the output file
    for item in items:
        outfile.write(item.strip() + '\n')