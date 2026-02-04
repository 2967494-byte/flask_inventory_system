from nelikvidi_parser import NelikvidiParser
import json
import os
import time

def main():
    parser = NelikvidiParser()
    
    # 1. Load links from all_links.txt (created by running nelikvidi_parser.py)
    links_file = "all_links.txt"
    if not os.path.exists(links_file):
        print("all_links.txt not found. Running link gathering...")
        links = parser.get_all_product_links()
        with open(links_file, "w") as f:
            for l in links:
                f.write(l + "\n")
    else:
        with open(links_file, "r") as f:
            links = [line.strip() for line in f if line.strip()]

    print(f"Total links to process: {len(links)}")
    
    # 2. Setup output folder
    results_folder = "downloads/data"
    images_folder = "downloads/images"
    os.makedirs(results_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)

    # 3. Process items
    # FOR TESTING: Let's process only first 5 items. 
    # Change to len(links) or a larger number for full scraping.
    limit = 10 
    processed_count = 0
    
    for url in links[:limit]:
        product_id = url.split('-')[-1].replace('.html', '')
        output_file = os.path.join(results_folder, f"{product_id}.json")
        
        if os.path.exists(output_file):
            print(f"Skipping {product_id}, already exists.")
            continue
            
        data = parser.scrape_product(url)
        if data:
            # Save JSON
            parser.save_data(data, output_file)
            
            # Download images
            product_img_folder = os.path.join(images_folder, product_id)
            for img_url in data.get('images', []):
                parser.download_image(img_url, product_img_folder)
            
            processed_count += 1
            print(f"[{processed_count}/{limit}] Processed: {data['name']} ({product_id})")
        
        # Be nice to the server
        time.sleep(1)

    print(f"\nBulk processing complete. Processed {processed_count} items.")
    print(f"Data saved to {results_folder}")
    print(f"Images saved to {images_folder}")

if __name__ == "__main__":
    main()
