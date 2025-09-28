import urllib.request
import os

# URL for the Iris dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"

# Local file path
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "iris.csv")

# Download the file
print(f"Downloading dataset from {url}...")
urllib.request.urlretrieve(url, file_path)
print(f"Dataset downloaded to {file_path}")

# Also create a header file for clarity
headers = "sepal_length,sepal_width,petal_length,petal_width,species\n"
with open(file_path, 'r') as f:
    content = f.read()
with open(file_path, 'w') as f:
    f.write(headers + content)

print("Added headers to the dataset.")
