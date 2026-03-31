import rispy
import pandas as pd
import os
folders = ["pubmed_txt"] #altered
total_dict = []
for folder in folders:
    for file in os.listdir(folder):
        if file.endswith(".ris"): #altered 
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                references = rispy.load(f)
                total_dict.extend(references)
ris_filename = 'all_references_with_duplicates.ris'
with open(ris_filename, 'w', encoding='utf-8') as ris_file:
    rispy.dump(total_dict, ris_file)

print(total_dict[0].keys())

filtered_df = [[item.get("title"), item.get("authors"), item.get("year"), item.get('abstract'), item.get('doi')] for item in total_dict if item.get("title") is not None and item.get("authors") is not None and item.get("year") is not None and item.get('abstract') is not None and item.get('doi') is not None]
filtered_df = pd.DataFrame(filtered_df, columns=['title', 'authors', 'year', 'abstract', 'doi'])
filtered_df = filtered_df.drop_duplicates(subset=['doi', 'title'])
filtered_df.to_csv('all_references_without_duplicates.csv', index=False)
print(len(filtered_df))
