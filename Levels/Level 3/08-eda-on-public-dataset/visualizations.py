import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load cleaned data
data_path = os.path.join('data', 'iris_cleaned.csv')
df = pd.read_csv(data_path)

# Set style
sns.set_style("whitegrid")

# 1. Histogram of sepal length
plt.figure(figsize=(8,6))
sns.histplot(df['sepal_length'], kde=True, color='skyblue')
plt.title('Distribution of Sepal Length')
plt.xlabel('Sepal Length (cm)')
plt.ylabel('Frequency')
plt.savefig(os.path.join('plots', 'sepal_length_histogram.png'))
plt.close()

# 2. Scatter plot of sepal length vs petal length
plt.figure(figsize=(8,6))
sns.scatterplot(data=df, x='sepal_length', y='petal_length', hue='species', palette='viridis')
plt.title('Sepal Length vs Petal Length by Species')
plt.xlabel('Sepal Length (cm)')
plt.ylabel('Petal Length (cm)')
plt.legend(title='Species')
plt.savefig(os.path.join('plots', 'sepal_vs_petal_scatter.png'))
plt.close()

# 3. Box plot of features by species
plt.figure(figsize=(10,6))
df_melted = df.melt(id_vars='species', value_vars=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
sns.boxplot(data=df_melted, x='variable', y='value', hue='species', palette='Set2')
plt.title('Box Plot of Features by Species')
plt.xlabel('Feature')
plt.ylabel('Value (cm)')
plt.xticks(rotation=45)
plt.legend(title='Species')
plt.savefig(os.path.join('plots', 'features_boxplot.png'))
plt.close()

# 4. Pairplot for all features
g = sns.pairplot(df, hue='species', palette='husl')
g.fig.suptitle('Pairplot of Iris Features by Species', y=1.02)
plt.savefig(os.path.join('plots', 'pairplot.png'))
plt.close()

print("Visualizations saved to plots/ directory.")
