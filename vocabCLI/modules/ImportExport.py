from Database import createConnection
from Exceptions import NoDataFoundException, NoQuotesException, NoRSSFeedsException
import csv
from fpdf import FPDF
from datetime import datetime
from rich import print
from rich.panel import Panel
import os


# TODO @anay : update docstring with new format
def export_to_csv()->None:
    """Export words to csv file."""
    conn= createConnection()
    c=conn.cursor()
    
    # =========================#
    # EXPORT WORDS TO CSV FILE #
    # =========================#
   
    try:
        c.execute("SELECT * FROM words")
        words = c.fetchall()
        if len(words) <= 0:
            raise NoDataFoundException
        
        #check if the directory exists, if not create it
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        with open('exports/WORDS.csv', 'w', newline='', encoding='utf-8', errors='ignore') as file:
            writer = csv.writer(file)
            writer.writerow([ "word", "datetime", "tag", "mastered", "learning", "favorite"])
            writer.writerows(words)
        print(Panel(title="[b reverse green]  Success!  [/b reverse green]", 
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold green]EXPORTED[/bold green] [bold blue]{len(words)}[/bold blue] words to [bold blue]WORDS.csv[/bold blue] file 📁")
        )
    except NoDataFoundException as e:
        print(e)
    
    
    # =========================#
    # EXPORT QUOTES TO CSV FILE#
    # =========================#
    try:
        c.execute("SELECT * FROM quotes")
        quotes = c.fetchall()
        if len(quotes) <= 0:
            raise NoQuotesException
        
        #check if the directory exists, if not create it
        if not os.path.exists('exports'):
            os.makedirs('exports')
         
        with open('exports/QUOTES.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([ "quote", "author", "datetime"])
            writer.writerows(quotes)
        print(Panel(title="[b reverse green]  Success!  [/b reverse green]",
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold green]EXPORTED[/bold green] [bold blue]{len(quotes)}[/bold blue] quotes to [bold blue]QUOTES.csv[/bold blue] file 📁")
        )
    except NoQuotesException as e:
        print("[b red]SKIPPING QUOTES EXPORT[/b red] since no quotes were found in the database. ❌")
    
    # =========================#
    # EXPORT RSS TO CSV FILE   #
    # =========================#
    try:
        c.execute("SELECT * FROM rss")
        rss = c.fetchall()
        if len(rss) <= 0:
            raise NoRSSFoundException
        
        #check if the directory exists, if not create it
        if not os.path.exists('exports'):
            os.makedirs('exports')
         
        with open('exports/RSS.csv', 'w', newline='', encoding='utf-8', errors='ignore') as file:
            writer = csv.writer(file)
            writer.writerow([ "title", "link", "description", "datetime"])
            writer.writerows(rss)
        print(Panel(title="[b reverse green]  Success!  [/b reverse green]",
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold green]EXPORTED[/bold green] [bold blue]{len(rss)}[/bold blue] rss feeds to [bold blue]RSS.csv[/bold blue] file 📁")
        )
    
    
    except NoRSSFoundException as e:
        print(e)
    
    # ==================================#
    # EXPORT QUIZ HISTORY TO CSV FILE   #
    # ==================================#
    try:
        c.execute("SELECT * FROM quiz_history")
        quiz_history = c.fetchall()
        if len(quiz_history) <= 0:
            raise NoDataFoundException
        
        #check if the directory exists, if not create it
        if not os.path.exists('exports'):
            os.makedirs('exports')
         
        with open('exports/QUIZ_HISTORY.csv', 'w', newline='', encoding='utf-8', errors='ignore') as file:
            writer = csv.writer(file)
            writer.writerow([ "type", "datetime", "question_count", "points", "duration"])
            writer.writerows(quiz_history)
        print(Panel(title="[b reverse green]  Success!  [/b reverse green]",
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold green]EXPORTED[/bold green] [bold blue]{len(quiz_history)}[/bold blue] quiz history to [bold blue]QUIZ_HISTORY.csv[/bold blue] file 📁")
        )
    except NoDataFoundException as e:
        print("No quiz history found in the database. ❌")


# TODO @anay : update docstring with new format
def import_from_csv()->None:
    """Import words from csv file."""

    conn= createConnection()
    c=conn.cursor()

    # ==================================#
    # IMPORT WORDS FROM CSV FILE        #
    # ==================================#
    
    # count of words added to database from the csv file
    added_words=0

    # words that already exists in database (counter will be incremented every time SQL throws an error about datetime column UNIQUE constraint violation)
    word_already_exists=0

    try:
        with open ('exports/WORDS.csv', 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.reader(file)
            next(reader) # skip header

            for row in reader:
                try:
                    # if tag is empty, skip the tag column in db
                    if row[2] == "":
                        sql = "INSERT INTO words (word, datetime, mastered, learning, favorite) VALUES (?, ?, ?, ?, ?)"
                        c.execute(sql, (row[0], row[1], row[3], row[4], row[5]))
                    else:
                        # add a checker to see if the word already exists in the database with the same timestamp
                        sql="INSERT INTO words (word, datetime, tag, mastered, learning, favorite) VALUES (?,?,?,?,?,?)"
                        c.execute(sql, row)
                    conn.commit()
                    added_words += c.rowcount
                except Exception as e:
                    word_already_exists+=1
    except FileNotFoundError:
        print(Panel(title="[b reverse red]  Error!  [/b reverse red]", 
                title_align="center",
                padding=(1, 1),
                renderable="[bold red]FILE NOT FOUND[/bold red] ❌. Make sure you have a file named [bold red]WORDS.csv[/bold red] in the same directory as the executable file. 📂")
        )
    finally:
        if word_already_exists>0:
            print(Panel(title="[b reverse yellow]  Warning!  [/b reverse yellow]", 
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold red]SKIPPED[/bold red] [bold blue]{word_already_exists}[/bold blue] DUPLICATE WORD(S) WITH THE SAME TIMESTAMP ⏩")
        )

        if added_words>0:
            print(Panel(title="[b reverse green]  Success!  [/b reverse green]", 
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold green]IMPORTED[/bold green] [bold blue]{added_words}[/bold blue] WORD(S) ✅")
        )

    # ==================================#
    # IMPORT RSS FEEDS FROM CSV FILE    #
    # ==================================#
    
    added_rss=0
    rss_already_exists=0
            
    try:
        with open ('exports/RSS.csv', 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.reader(file)
            next(reader) # skip header
            
            for row in reader:
                try:
                    sql="INSERT INTO rss (title, link, description, datetime) VALUES (?,?,?,?)"
                    c.execute(sql, row)
                    conn.commit()
                    added_rss += c.rowcount
                except Exception as e:
                    rss_already_exists+=1
       
         

    except FileNotFoundError:
        print(Panel(title="[b reverse red]  SKIPPED RSS FEED IMPORT  [/b reverse red]", 
                title_align="center",
                padding=(1, 1),
                renderable="[b blue]SKIPPED RSS FEED IMPORT[/b blue]. Make sure you have a file named [bold red]RSS.csv[/bold red] in the exports if you wish to import your RSS feeds. 📂")
        )
    
    finally:
        if rss_already_exists>0:
            print(Panel(title="[b reverse yellow]  Warning!  [/b reverse yellow]", 
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold red]SKIPPED[/bold red] [bold blue]{rss_already_exists}[/bold blue] DUPLICATE RSS FEED(S) WITH THE SAME TIMESTAMP ⏩")
        )
            
        if added_rss>0:
            print(Panel(title="[b reverse green]  Success!  [/b reverse green]",
                    title_align="center",
                    padding=(1, 1),
                    renderable=f"[bold green]IMPORTED[/bold green] [bold blue]{added_rss}[/bold blue] rss feeds from [bold blue]RSS.csv[/bold blue] file 📁")
            )
        
        

    # ==================================#
    # IMPORT QUOTES FROM CSV FILE       #
    # ==================================#
    
    added_quotes=0
    quote_already_exists=0
     
    try:
        with open ('exports/QUOTES.csv', 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.reader(file)
            next(reader) # skip header
            
            for row in reader:
                try:
                    # add null to optional author column if it is empty
                    if row[1] == "":
                        sql="INSERT INTO quotes (quote, datetime) VALUES (?,?)"
                        c.execute(sql, (row[0], row[2]))
                    else:
                        sql="INSERT INTO quotes (quote, author, datetime) VALUES (?,?,?)"
                        c.execute(sql, row)
                    conn.commit()
                    added_quotes += c.rowcount
                except Exception as e:
                    quote_already_exists+=1
                
    except FileNotFoundError:
        print(Panel(title="[b reverse red]  SKIPPED QUOTE IMPORT  [/b reverse red]", 
                title_align="center",
                padding=(1, 1),
                renderable="[b blue]SKIPPED QUOTE IMPORT[/b blue]. Make sure you have a file named [bold red]QUOTES.csv[/bold red] in the exports if you wish to import your quotes. 📂")
        )
     
    finally:
        if quote_already_exists>0:
            print(Panel(title="[b reverse yellow]  Warning!  [/b reverse yellow]", 
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold red]SKIPPED[/bold red] [bold blue]{quote_already_exists}[/bold blue] DUPLICATE QUOTE(S) WITH THE SAME TIMESTAMP ⏩")
        )
            
        if added_quotes>0:
            print(Panel(title="[b reverse green]  Success!  [/b reverse green]",
                    title_align="center",
                    padding=(1, 1),
                    renderable=f"[bold green]IMPORTED[/bold green] [bold blue]{added_quotes}[/bold blue] quotes from [bold blue]QUOTES.csv[/bold blue] file 📁")
            )
    
    # todo - handle imports from seperate file  quiz_history.csv
    # ==================================#
    # IMPORT QUIZ HISTORY FROM CSV FILE #
    # ==================================#
    
    added_quiz_history=0
    quiz_history_already_exists=0
     
    try:
        with open ('exports/QUIZ_HISTORY.csv', 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.reader(file)
            next(reader) # skip header
            
            for row in reader:
                try:
                    sql="INSERT INTO quiz_history (type, datetime, question_count, points, duration) VALUES (?,?,?,?,?)"
                    c.execute(sql, row)
                    conn.commit()
                    added_quiz_history += c.rowcount
                except Exception as e:
                    quiz_history_already_exists+=1
                
    except FileNotFoundError:
        print(Panel(title="[b reverse red]  SKIPPED QUIZ HISTORY IMPORT  [/b reverse red]", 
                title_align="center",
                padding=(1, 1),
                renderable="[b blue]SKIPPED QUIZ HISTORY IMPORT[/b blue]. Make sure you have a file named [bold red]QUIZ_HISTORY.csv[/bold red] in the exports if you wish to import your quiz history. 📂")
        )
        
    finally:
        if quiz_history_already_exists>0:
            print(Panel(title="[b reverse yellow]  Warning!  [/b reverse yellow]", 
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold red]SKIPPED[/bold red] [bold blue]{quiz_history_already_exists}[/bold blue] DUPLICATE QUIZ HISTORY WITH THE SAME TIMESTAMP ⏩")
        )
            
        if added_quiz_history>0:
            print(Panel(title="[b reverse green]  Success!  [/b reverse green]",
                    title_align="center",
                    padding=(1, 1),
                    renderable=f"[bold green]IMPORTED[/bold green] [bold blue]{added_quiz_history}[/bold blue] quiz history from [bold blue]QUIZ_HISTORY.csv[/bold blue] file 📁")
            )

class PDF(FPDF):
    def header(self):
        #self.image('logo.png', 10, 8, 33)

        self.set_font('helvetica', 'B', 15)

        self.set_title("Vocabulary Builder")
        self.cell(55)
        self.cell(80, 10, 'Vocabulary Builder', border=1, align='C')
        self.ln(20)


    def footer(self):
        """Page footer."""
        self.set_y(-12)
        self.set_font('helvetica', 'I', 10)

        # Page number
        self.cell(0, 10, f'Page {str(self.page_no())}', 0, 0, 'C')


# TODO @anay : update docstring with new format
def export_to_pdf()->None:    # sourcery skip: extract-method
    """Export words to pdf file."""
    try:
        pdf=PDF('P', 'mm', 'A4')
        pdf.set_fill_color(r=152, g=251, b=152)
        pdf.set_auto_page_break(auto=True, margin=5)
        pdf.add_page()
        pdf.set_font("Arial","B", 12)
        conn= createConnection()
        c=conn.cursor()
        c.execute("SELECT DISTINCT (word), tag, mastered, learning, favorite from words")
        rows = c.fetchall()
        if len(rows) <= 0:
            raise NoDataFoundException
        pdf.cell(10,8, txt="#",border=True, align='L', fill=True)
        pdf.cell(40,8, txt="Word",border=True, align='L', fill=True)
        # pdf.cell(40,8, txt="Lookup Date",border=True, align='L', fill=True)
        pdf.cell(40,8, txt="Tag",border=True, align='L', fill=True)
        pdf.cell(30,8, txt="Mastered",border=True, align='L', fill=True)
        pdf.cell(30,8, txt="Learning ",border=True, align='L', fill=True)
        pdf.cell(30,8, txt="Favorite",border=True, align='L', fill=True)
        pdf.ln()

        #reset font
        pdf.set_font("Courier","",10)
        for sr_no, row in enumerate(rows, start=1):

            pdf.cell(10,8, txt=str(sr_no),border=True, align='L') # Sr No.
            pdf.cell(40,8, txt=str(row[0]),border=True, align='L') # Word

            tag = row[2] if row[1] != None else ""
            pdf.cell(40,8, txt=str(tag),border=True, align='L') # Tag

            mastered= "X" if row[2] == 1 else ""
            pdf.cell(30,8, txt=mastered ,border=True, align='C') # Mastered

            learning= "X" if row[3] == 1 else ""
            pdf.cell(30,8, txt=learning,border=True, align='C') # Learning

            favorite= "X" if row[4] == 1 else ""
            pdf.cell(30,8, txt=favorite,border=True, align='C')  # Favorite
            pdf.ln()
            
        #check if the directory exists, if not create it
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        pdf.output(f"exports/VocabularyWords[{datetime.now().strftime('%d_%b_%Y')}].pdf")
        print(Panel(title="[b reverse green]  Success!  [/b reverse green]", 
                title_align="center",
                padding=(1, 1),
                renderable=f"[bold green]EXPORTED[/bold green] [bold blue]{len(rows)}[/bold blue] WORDS TO PDF ✅")
        )

    except NoDataFoundException as e:
        print(e)

    # todo - export quotes to same PDF file (append it)
    # todo - export rss feed to same PDF file (append it)
    # todo - export quiz history to same PDF file (append it)