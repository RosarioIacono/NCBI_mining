"""
A script to mine a taxonomy from NCBI given a list of species in the format genus_species
"""
import pandas as pd
from Bio import Entrez
import time

# Function to fetch taxonomy information using NCBI Entrez
def fetch_taxonomy(genus, species):
    try:
        Entrez.email = "my.email@address.com"  # Replace with your email
        search_term = f"{genus} {species}"
        print(f"Searching for: {search_term}")
        handle = Entrez.esearch(db="taxonomy", term=search_term, retmode="xml")
        record = Entrez.read(handle)
        handle.close()
        
        if record['IdList']:
            taxon_id = record['IdList'][0]
            handle = Entrez.efetch(db="taxonomy", id=taxon_id, retmode="xml")
            taxon_record = Entrez.read(handle)
            handle.close()
            lineage = taxon_record[0].get('LineageEx', [])
            taxonomy = { 'phylum': None, 'class': None, 'order': None, 'family': None }
            for taxon in lineage:
                rank = taxon.get('Rank')
                scientific_name = taxon.get('ScientificName')
                if rank in taxonomy:
                    taxonomy[rank] = taxon['ScientificName']
                    print(f"Found {rank}: {taxon.get('ScientificName')}")
                    
            return taxonomy
        else:
            return { 'phylum': None, 'class': None, 'order': None, 'family': None }
    except Exception as e:
        print(f"Error fetching taxonomy for {genus} {species}: {e}")
        return { 'phylum': None, 'class': None, 'order': None, 'family': None }

# Load the CSV file
file_path = 'path_to_my_file.csv'  # Replace with your file path
species_df = pd.read_csv(file_path, header=None, names=['Species'])

# Split the species column into Genus and Species
# Split the species column into Genus and Species
species_df[['Genus', 'Species']] = species_df['Species'].str.split('_', n=1, expand=True)


# Fetch taxonomy for each species
taxonomy_info = []

for index, row in species_df.iterrows():
    genus = row['Genus']
    species = row['Species']
    tax_info = fetch_taxonomy(genus, species)
    print(tax_info)
    taxonomy_info.append({
        'Genus': genus,
        'Species': species,
        'Phylum': tax_info['phylum'],
        'Class': tax_info['class'],
        'Order': tax_info['order'],
        'Family': tax_info['family']
    })
    time.sleep(1)  # To avoid hitting the NCBI rate limit

# Convert the fetched data into a DataFrame
taxonomy_df = pd.DataFrame(taxonomy_info)

# Save the taxonomy table to a new CSV file
taxonomy_df.to_csv('path_to_my_file.csv', index=False)

