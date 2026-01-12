if True:
    import tkinter as tk
    import pandas as pd
    import threading
    import requests
    import time
    import re
    from tkinter import ttk, messagebox
    from bs4 import BeautifulSoup as bs
    from urllib.parse import urljoin
    from random import uniform
    HEADERS = {'User-Agent': 'MyMovieBot/1.0 (https://example.com; myemail@example.com)'}

def get_title(infobox) -> str:
    try:
        if not infobox:
            return None
        caption = infobox.find('caption')
        if caption:
            title = caption.get_text(strip=True)
            if title:
                return title

        for row in infobox.find_all('tr'):
            header = row.find('th', {'colspan': '2'})
            if header:
                title = header.get_text(strip=True)
                if title:
                    return title
        return None

    except Exception as e:
        print(f"Error extracting title: {e}")
        return None

def get_lang(infobox) -> str:
    try:
        if not infobox:
            return None
        for row in infobox.find_all('tr'):
            header = row.find('th')
            if header and header.get_text(strip=True) == "Language":
                data = row.find('td')
                if data:
                    language = data.get_text(separator=", ", strip=True)
                    language = ' '.join(language.split())
                    return language
        return None
    except Exception as e:
        return {"error": str(e)}

def get_director(infobox) -> str:
    try:
        if not infobox:
            return None
        for row in infobox.find_all('tr'):
            header = row.find('th')
            if header and header.get_text(strip=True) == "Directed by":
                data = row.find('td')
                if data:
                    director_text = data.get_text(separator=", ", strip=True)
                    director_text = ' '.join(director_text.split())
                    director_text = ' '.join(word for word in director_text.split()
                    if not (word.startswith('[') and word.endswith(']')))
                    directors = [d.strip() for d in director_text.split(",")]
                    if directors:
                        return directors[0]
        return None
    except Exception as e:
        print(f"Error extracting director: {e}")
        return None

def get_runtimeDiff(infobox) -> int:
    try:
        if not infobox:
            return None
        for row in infobox.find_all('tr'):
            header = row.find('th')
            if header and header.get_text(strip=True) in ["Running time", "Length"]:
                data = row.find('td')
                if data:
                    runtime_text = data.get_text(strip=True)
                    numbers = [int(num) for num in re.findall(r'\d+', runtime_text)]
                    if not numbers:
                        return None
                    if 'hr' in runtime_text.lower():
                        hours = 0
                        minutes = 0
                        parts = runtime_text.split()
                        for i, part in enumerate(parts):
                            if part.isdigit():
                                if i+1 < len(parts) and 'hr' in parts[i+1].lower():
                                    hours = int(part)
                                elif i+1 < len(parts) and 'min' in parts[i+1].lower():
                                    minutes = int(part)
                        return hours * 60 + minutes
                    return numbers[0]
        return None
    except Exception as e:
        print(f"Error extracting runtime: {e}")
        return None

def get_cast(infobox) -> list:
    try:
        if not infobox:
            return None
        for row in infobox.find_all('tr'):
            header = row.find('th')
            if header and header.get_text(strip=True) in ["Starring", "Cast"]:
                data = row.find('td')
                if data:
                    cast_links = data.find_all('a')
                    cast_names = []

                    for link in cast_links:
                        if 'href' in link.attrs and '/wiki/' in link['href']:
                            name = link.get_text(strip=True)
                            if name and not name.startswith('['):
                                cast_names.append(name)
                                if len(cast_names) >= 10:
                                    break
                    if not cast_names:
                        cast_text = data.get_text(separator=", ", strip=True)
                        cast_text = ' '.join(cast_text.split())
                        cast_text = ' '.join(word for word in cast_text.split()
                                            if not (word.startswith('[') and word.endswith(']')))
                        cast_names = [name.strip() for name in cast_text.split(",") if name.strip()]
                    if cast_names:
                        return ', '.join(cast_names[:10])
        return None
    except Exception as e:
        print(f"Error extracting cast: {e}")
        return None

def get_attributes(url: str) -> dict:
    try:
        time.sleep(uniform(0.01, 0.02))
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 0.01))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return get_attributes(url)

        response.raise_for_status()
        soup = bs(response.text, 'html.parser')

        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return None

        return {
            "Title": get_title(infobox),
            "Language": get_lang(infobox),
            "Director": get_director(infobox),
            "Runtime": get_runtimeDiff(infobox),
            "Cast": get_cast(infobox),
        }

    except Exception as e:
        print(f"Error getting data from {url}: {e}")
        return None

def get_data(infobox)->dict:
    try:
        if not infobox:
            return None

        return {
            "Title": get_title(infobox),
            "Language": get_lang(infobox),
            "Director": get_director(infobox),
            "Runtime": get_runtimeDiff(infobox),
            "Cast": get_cast(infobox),
        }

    except Exception as e:
        print(f"Error getting data from infobox: {e}")
        return None

def pandas_framer(arr: list) -> dict:
    try:
        structured_data = {
            "Title": [],
            "Language": [],
            "Director": [],
            "Runtime": [],
            "Cast": [],
        }

        for movie in arr:
            structured_data["Title"].append(movie.get("Title"))
            structured_data["Language"].append(movie.get("Language"))
            structured_data["Director"].append(movie.get("Director"))
            structured_data["Runtime"].append(movie.get("Runtime"))
            structured_data["Cast"].append(movie.get("Cast"))

        return structured_data

    except Exception as e:
        print(f"Error structuring data: {e}")
        return {}

def is_movie(url:str) -> bool:
    try:
        time.sleep(uniform(0.01, 0.02))
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 0.01))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return is_movie(url)

        response.raise_for_status()
        soup = bs(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            return False

        movie_fields = ["Directed by", "Produced by", "Written by", "Starring", "Release date"]
        for field in movie_fields:
            if infobox.find('th', text=field) and " film " in page_text:
                return get_data(infobox)
        return False

    except Exception as e:
        print(f"Error checking {url}: {e}")
        return False

def get_links(url:str) -> list:
    try:
        time.sleep(uniform(0.01, 0.02))
        site = requests.get(url, headers=HEADERS)

        if site.status_code == 429:
            retry_after = int(site.headers.get('Retry-After', 0.01))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return get_links(url)

        site.raise_for_status()
        soup = bs(site.text, 'html.parser')

        links = []
        exclude = ['/wiki/Special:', '/wiki/Help:', '/wiki/Template:', '/wiki/Talk:', '/wiki/Category:', '/wiki/File:']

        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/wiki/') and not any(href.startswith(prefix) for prefix in exclude):
                full_url = urljoin(url, href)
                links.append(full_url)

        print(f"{len(links)} links scraped from {get_title(soup)}")
        return set(links)

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
class MovieRecommendationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wikipedia Movie Recommender")
        self.root.geometry("1000x800")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Horizontal.TProgressbar', thickness=20)
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input Section
        self.create_input_section()
        
        # Progress Bar Section
        self.create_progress_section()
        
        # Results Section
        self.create_results_section()
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10,0))
        
        # Initialize variables
        self.input_attributes = None
        self.scraping_thread = None
        self.stop_event = threading.Event()
        self.progress_max = 100  # Default maximum value
        self.current_progress = 0   
    def create_progress_section(self):
        """Create the progress bar section"""
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=(0,10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style='Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, expand=True)
        
        # Progress label
        self.progress_label = ttk.Label(
            progress_frame,
            text="0%",
            anchor=tk.CENTER
        )
        self.progress_label.pack()
    def update_progress(self, value=None, max_value=None):
        """Update the progress bar and label"""
        if max_value is not None:
            self.progress_max = max_value
            self.progress_bar.configure(maximum=max_value)
        
        if value is not None:
            self.current_progress = value
        
        # Calculate percentage
        percentage = (self.current_progress / self.progress_max) * 100 if self.progress_max > 0 else 0
        
        # Update widgets
        self.progress_var.set(self.current_progress)
        self.progress_label.config(text=f"{int(percentage)}%")
        self.root.update_idletasks()  
    def increment_progress(self):
        """Increment progress by 1"""
        self.current_progress += 1
        self.update_progress()   
    def reset_progress(self):
        """Reset the progress bar to 0"""
        self.current_progress = 0
        self.progress_max = 100
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.progress_bar.configure(maximum=100)   
    def create_input_section(self):
        """Create the input section of the GUI"""
        input_frame = ttk.LabelFrame(self.main_frame, text="Movie Input", padding="10")
        input_frame.pack(fill=tk.X, pady=(0,10))
        
        # URL Entry
        ttk.Label(input_frame, text="Wikipedia Movie URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(input_frame, width=80)
        self.url_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
        self.url_entry.insert(0, "https://en.wikipedia.org/wiki/Home_Alone")
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10,0))
        
        self.search_btn = ttk.Button(
            button_frame, 
            text="Find Recommendations", 
            command=self.start_scraping_thread
        )
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame, 
            text="Stop", 
            command=self.stop_scraping,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Input Movie Info
        self.input_info_frame = ttk.LabelFrame(input_frame, text="Input Movie Details", padding="10")
        self.input_info_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(10,0))
        
        labels = ["Title:", "Language:", "Director:", "Runtime:", "Cast:"]
        self.input_labels = {}
        
        for i, label in enumerate(labels):
            ttk.Label(self.input_info_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            self.input_labels[label[:-1].lower()] = ttk.Label(self.input_info_frame, text="", wraplength=600)
            self.input_labels[label[:-1].lower()].grid(row=i, column=1, sticky=tk.W)   
    def create_results_section(self):
        """Create the results display section"""
        results_frame = ttk.LabelFrame(self.main_frame, text="Recommended Movies", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for results
        self.tree = ttk.Treeview(results_frame, columns=('title', 'language', 'director', 'runtime', 'cast'), show='headings')
        
        # Configure columns
        self.tree.heading('title', text='Title')
        self.tree.heading('language', text='Language')
        self.tree.heading('director', text='Director')
        self.tree.heading('runtime', text='Runtime (mins)')
        self.tree.heading('cast', text='Cast')
        
        # Set column widths
        self.tree.column('title', width=250, anchor=tk.W)
        self.tree.column('language', width=100, anchor=tk.W)
        self.tree.column('director', width=150, anchor=tk.W)
        self.tree.column('runtime', width=80, anchor=tk.CENTER)
        self.tree.column('cast', width=350, anchor=tk.W)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        y_scroll.grid(row=0, column=1, sticky=tk.NS)
        x_scroll.grid(row=1, column=0, sticky=tk.EW)
        
        # Configure grid weights
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Results info label
        self.results_info = ttk.Label(results_frame, text="", font=('Arial', 10))
        self.results_info.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5,0))   
    def start_scraping_thread(self):
        """Start the scraping process in a separate thread"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a Wikipedia movie URL")
            return
        
        # Clear previous results and reset progress
        self.clear_results()
        self.reset_progress()
        self.update_status("Starting scraping process...")
        
        # Disable search button and enable stop button
        self.search_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start scraping in a separate thread
        self.stop_event.clear()
        self.scraping_thread = threading.Thread(
            target=self.scrape_and_display_results,
            args=(url,),
            daemon=True
        )
        self.scraping_thread.start()     
    def check_thread(self):
        """Check if the scraping thread is still running"""
        if self.scraping_thread.is_alive():
            self.root.after(100, self.check_thread)
        else:
            self.search_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)   
    def stop_scraping(self):
        """Stop the ongoing scraping process"""
        self.stop_event.set()
        self.update_status("Stopping scraping process...")   
    def scrape_and_display_results(self, url):
        """Main scraping function to run in thread"""
        try:
            # Get input movie attributes
            self.root.after(0, lambda: self.update_status("Getting input movie details..."))
            self.input_attributes = get_attributes(url)
            
            if not self.input_attributes:
                self.root.after(0, lambda: self.update_status("Could not get attributes for input movie"))
                return
            
            # Update input movie info in GUI
            self.root.after(0, self.update_input_movie_info)
            
            # Get links from the input movie page
            self.root.after(0, lambda: self.update_status("Finding related movie links..."))
            links = list(get_links(url))
            
            if self.stop_event.is_set():
                self.root.after(0, lambda: self.update_status("Scraping stopped by user"))
                return
            
            # Update progress bar maximum
            self.root.after(0, lambda: self.update_progress(max_value=len(links)))
            
            # Find movies from links
            self.root.after(0, lambda: self.update_status(f"Checking {len(links)} pages for movies..."))
            movies = []
            
            for i, link in enumerate(links):
                if self.stop_event.is_set():
                    break
                
                # Update progress
                self.root.after(0, self.increment_progress)
                self.root.after(0, lambda: self.update_status(f"Processing {i+1}/{len(links)}: {link}"))
                
                movie_data = is_movie(link)
                if movie_data:
                    movies.append(movie_data)
            
            if self.stop_event.is_set():
                self.root.after(0, lambda: self.update_status("Scraping stopped by user"))
                return
            
            self.root.after(0, lambda: self.update_results_info(
                f"{len(movies)} pages are movies out of {len(links)}"
            ))
            
            # Filter movies by language
            filtered_movies = []
            input_language = self.input_attributes.get("Language")
            
            for movie in movies:
                language_match = (movie.get("Language") and input_language and
                                 any(lang.strip().lower() in input_language.lower()
                                     for lang in movie["Language"].split(',')))
                
                if language_match:
                    filtered_movies.append(movie)
                    movie["Language"] = input_language
            
            self.root.after(0, lambda: self.update_results_info(
                f"{len(filtered_movies)} movies match the input movie's language"
            ))
            
            # Convert to DataFrame and display
            movie_dict = pandas_framer(filtered_movies)
            df = pd.DataFrame(movie_dict)
            df = df.dropna()
            df = df.sort_values("Runtime", ignore_index=True)
            df.index += 1
            
            # Update GUI with results
            self.root.after(0, lambda: self.display_results(df))
            self.root.after(0, lambda: self.update_status("Done!"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.search_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
    def update_input_movie_info(self):
        """Update the input movie info display"""
        if self.input_attributes:
            for key, label in self.input_labels.items():
                value = self.input_attributes.get(key.capitalize(), "")
                label.config(text=value[:200] + "..." if len(str(value)) > 200 else value)
    def display_results(self, df):
        """Display the results in the Treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new items
        for _, row in df.iterrows():
            self.tree.insert('', tk.END, values=(
                row.get('Title', ''),
                row.get('Language', ''),
                row.get('Director', ''),
                row.get('Runtime', ''),
                row.get('Cast', '')[:100] + "..." if len(str(row.get('Cast', ''))) > 100 else row.get('Cast', '')
            ))  
    def clear_results(self):
        """Clear all results from the display"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for label in self.input_labels.values():
            label.config(text="")
        
        self.results_info.config(text="")
        self.input_attributes = None  
    def update_status(self, message):
        """Update the status bar"""
        self.root.after(0, lambda: self.status_var.set(message))  
    def update_results_info(self, message):
        """Update the results info label"""
        current_text = self.results_info.cget("text")
        self.results_info.config(text=current_text + "\n" + message if current_text else message)

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieRecommendationApp(root)
    root.mainloop()


