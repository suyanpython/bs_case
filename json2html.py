# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 12:05:34 2024

@author: Suyan
"""
import json, re, os
from collections import defaultdict
import matplotlib.pyplot as plt


# Keywords with categories, including initial count 0 for each keyword
keywords = {
    'Language': [('Python', 0), ('Php', 0), ('Vue', 0), ('React', 0), ('Django', 0), ('Symfony', 0), ('Laravel', 0), ('c#', 0), ('c++', 0),('Java', 0),('Angular', 0)],
    'Database': [ ('Mongo', 0), ('Redis', 0),('ldap', 0),('Postgre', 0)],
    'Others': [ ('Kafka', 0), ('Airflow', 0),('rabbit', 0)],
    'DevOps': [('Linux', 0), ('Kubernetes', 0), ('Docker', 0), ('Aws', 0), ('Azure', 0), ('Ansible', 0), ('Gitlab', 0),('Google Cloud', 0)],
    # 'Location': [('Marseille', 0), ('Aix-en-provence', 0)],
}

flat_keywords = [keyword for category in keywords.values() for keyword, _ in category]
flat_keywords.extend(['ESN', 'DevOps','Full Stack','Fullstack'])

def bold_keywords(text, keywords):
    """Make keywords bold in the given text."""
    for keyword in keywords:
        # Use regex to match the keyword as a whole word
        text = re.sub(rf'\b{re.escape(keyword)}\b', rf'<b>{keyword}</b>', text, flags=re.IGNORECASE)
    return text

def highlight(text):
    # Use regex to match text between "chez" and ", pour"
    def replacer(match):
        # Wrap the matched text in markdown-style for underline and italic
        return f"<u>{match.group(1)}</u>"

    # Apply regex substitution
    text = re.sub(r"chez\s+(.*?)\s*, pour", replacer, text)
    return text


file_path = "scraped_data.json"
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found!")

# Load the JSON data (assuming data.json exists)
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)  # Load JSON properly


# Custom sorting function
def custom_sort(item):
    short_desc = item['short_description'].lower()
    
    # Special sorting rules: prioritize "Marseille" and "Aix-en-Provence"
    if "marseille" in short_desc:
        return (0, short_desc)  # "Marseille" will be sorted first
    elif "aix-en-provence" in short_desc:
        return (1, short_desc)  # "Aix-en-Provence" will be second
    else:
        return (2, short_desc)  # All other cities will come after


# Remove duplicates based on URL
seen_urls = set()
unique_data = []
for item in data:
    if item['url'] not in seen_urls:
        seen_urls.add(item['url'])
        unique_data.append(item)

# Sort the unique data
data = sorted(unique_data, key=custom_sort)





# Start building the HTML table with Bootstrap classes
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Offers</title>
    <!-- Include Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <!-- Include DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
    <style>
        /* Custom styles for the table */
        table {
            background-color: #f9f9f9;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #4CAF50; /* Green background for header */
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2; /* Light grey for even rows */
        }
        tr:hover {
            background-color: #ddd; /* Darker grey on hover */
            cursor: pointer;
        }
        .container {
            margin-top: 30px;
        }
        .content_text {
            max-height: 200px;
            overflow-y: auto;
            display: block;
        }
        .description_text {
            max-height: 200px;
        }
        h2 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        .keyword {
            font-size: 12px; /* Smaller text size */
            margin: 5px 0; /* Space between keyword entries */
    }
    </style>
</head>
<body>


"""





# Function to save pie charts
def save_pie_chart(data, title, filename):
    fig, ax = plt.subplots()
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title)
    plt.savefig(filename)  # Save the chart as an image
    plt.close()
    
    

# Initialize a dictionary to store keyword counts
keyword_counts = defaultdict(int)

if isinstance(data, list):
    countdata = len(data)

# Loop through the JSON data
for item in data:
    # Safely get the values
    title = item.get('title', '')
    content = item.get('content', '')

    # Handle cases where title or content is a list
    if isinstance(title, list):
        title = " ".join(title)

    # Combine title and content into one string
    combined_text = f"{content}".lower()

    for category, category_keywords in keywords.items():
        for i, (keyword, count) in enumerate(category_keywords):
            if re.search(rf'\b{re.escape(keyword.lower())}\b', combined_text):  # Match whole word
                keywords[category][i] = (keyword, count + 1)
            

html_content += """
<div class="container">
  <!-- Toggle Button -->
  <button class="btn btn-primary" type="button" data-toggle="collapse" data-target="#toggleContent" aria-expanded="false" aria-controls="toggleContent">
    Pie Charts
  </button>

  <!-- Collapsible Content -->
  <div class="collapse mt-3" id="toggleContent">
    <div class="card card-body">
     """

# Loop through categories and display keyword counts inline
for category, category_keywords in keywords.items():
    html_content += f"<div class='category'>"
    counts = {keyword: count for keyword, count in category_keywords}
    filename = f"{category}_pie_chart.png"
    save_pie_chart(counts, f"{category}", filename)
    html_content += f"<img style='width:100%' src='{filename}' alt='{category} Pie Chart'><br>"
    
    category_keywords_sorted = sorted(category_keywords, key=lambda x: x[1], reverse=True)

    # For each keyword in the category, display its count
    for keyword, count in category_keywords_sorted:
        html_content += f"<div class='keyword'><b>{keyword}:</b> {count}</div>"
    
    html_content += "</div>"
html_content += f"""</div>
    </div>
  </div>
</div>
<div>

<div class="container">
    <h2>JSON Data Table -- {countdata} results</h2>
    <table class="table table-bordered" id="jobTable">
        <thead>
            <tr>
                <th>Title</th>
                <th>URL</th>
                <th>Short Description</th>
                <th>Content</th>
            </tr>
        </thead>
        <tbody>
        """

# Filter and process data
filtered_data = []


for item in data:
    # Process title if it's a list of strings
    if isinstance(item.get("title"), list):
        item["title"] = [bold_keywords(title, flat_keywords) for title in item["title"]]
    elif isinstance(item.get("title"), str):  # Handle single string case
        item["title"] = bold_keywords(item["title"], flat_keywords)
    else:
        item["title"] = "No Title Available"

    # Process content if it's a list of strings
    if isinstance(item.get("content"), list):
        item["content"] = [bold_keywords(content, flat_keywords) for content in item["content"]]
    elif isinstance(item.get("content"), str):  # Handle single string case
        item["content"] = bold_keywords(item["content"], flat_keywords)
    else:
        item["content"] = "No Content Available"
        
    if isinstance(item.get("short_description"), list):
        item["short_description"] = [bold_keywords(short_description, keywords) for short_description in item["short_description"]]
    elif isinstance(item.get("short_description"), str):  # Handle single string case
        item["short_description"] = bold_keywords(highlight(item["short_description"]), keywords)
        
    # Check if any of the flat_keywords are in the content
    content_text = " ".join(item["content"]) if isinstance(item["content"], list) else item["content"]
    if any(keyword.lower() in content_text.lower() for keyword in flat_keywords):
        filtered_data.append(item)



    
    html_content += f"""
        <tr>
            <td>{item['title']}</td>
            <td><a href="{item['url']}">{item['url']}</a></td>
            <td class="description_text">{item['short_description']}</td>
            <td class="content_text">{item['content']}</td>
        </tr>
    """

# Close the table and HTML structure
html_content += """
        </tbody>
    </table>
</div>


<!-- Include jQuery (ensure no conflict with Bootstrap) -->
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>

<!-- Include DataTables JavaScript -->
<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>

<script>
    $(document).ready(function() {
        // Initialize DataTable
        $('#jobTable').DataTable({
            "paging": false, // Enable pagination
            "searching": true, // Enable search functionality
            "ordering": true, // Enable sorting
            "info": true, // Show info (number of entries)
            "lengthChange": false, // Disable changing the number of entries per page
        });
    });
</script>

<!-- Include Bootstrap JS and dependencies -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
"""

# Save the generated HTML to a file
with open("table.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML table has been generated and saved as 'table.html'.")


# Replace original data with filtered data
data = filtered_data
# Save the updated data back to the JSON file
output_file = "scraped_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

