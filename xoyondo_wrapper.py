import datetime
import calendar
import io
import matplotlib.pyplot as plt
from operator import add
from urllib.error import HTTPError

import xoyondo as xy

class Xoyondo_Wrapper(xy.Xoyondo):
    def get_week(self, week):
        # Assuming week is a string in the format 'YYYY/WW'
        messages = []
        date_range = ""
        
        if isinstance(week, str) and '/' in week:
            year, week_number = [x.strip() for x in week.split('/')]
            print(year, week_number)
            try:
                year = int(year)
            except ValueError:
                raise ValueError(f'Year {year} is not a valid number.')
            try:
                week_number = int(week_number)
            except ValueError:
                raise ValueError(f'Week number {week_number} is not a valid number.')
            try:
                first_day_of_week = datetime.datetime.strptime(f'{year}-W{week_number} -1', "%Y-W%W -%w")
                last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
                date_range = f"{first_day_of_week.strftime('%Y/%m/%d')}:{last_day_of_week.strftime('%Y/%m/%d')}"
                
                self.log_message(f'{week} corresponds to {date_range}', messages)
                
                return date_range, messages
            except ValueError:
                raise ValueError(f'Invalied input: {week}')
            
        else:
            raise ValueError(f'Invalid input: {week}')
    
        # Kalenderwoche heraussuchen und in Datum umwandeln -> zum Beispiel 2023/09/18:2023/09/24 - als range

    def get_month(self, month):
        # Assuming month is a string in the format 'YYYY/MM'
        messages = []
        date_range = ""
        
        if isinstance(month, str) and '/' in month:
            year, month_number = [x.strip() for x in month.split('/')]
            
            try:
                year = int(year)
            except ValueError:
                raise ValueError(f'Year {year} is not a valid number.')
            
            try:
                month_number = int(month_number)
            except ValueError:
                raise ValueError(f'Month number {month_number} is not a valid number.')   
             
            # Ensure month_number is between 1 and 12
            if 1 <= month_number <= 12:
                # Getting the last day of the month
                last_day = calendar.monthrange(year, month_number)[1]
                first_day_of_month = f'{year}/{month_number}/01'
                last_day_of_month = f'{year}/{month_number}/{last_day}'
                date_range = f"{first_day_of_month}:{last_day_of_month}"
                
                self.log_message(f'{month} corresponds to {date_range}', messages)
                
                return date_range, messages
            else:
                raise ValueError(f'Month {month_number} is not valid. It should be between 1 and 12.')
            
        else:
            raise ValueError(f'Invalid input: {month}')
    
    def reset_poll(self, add_dates):
        
        messages = []
        
        try:
            # Get existing dates
            existing_dates, _messages = self.get_dates()
            messages.extend(_messages)
            
            new_dates = []
            add_dates = str(add_dates)
            
            if "," in add_dates or ":" in add_dates:
                parts = add_dates.split(",")
                for part in parts:
                    if ":" in part:
                        start, end = [x.strip() for x in part.split(":")]
                        dates, _messages = self.get_date_list(start, end)
                        new_dates.extend(dates)
                        messages.extend(_messages)
                    else:
                        new_dates.append(part.strip())
            else:
                new_dates.append(add_dates.strip())

            # Add new dates
            to_add = []
            
            for date in new_dates:
                if date not in existing_dates:
                    to_add.append(date)
            if to_add:
                _messages = self.add_dates(",".join(to_add))
                messages.extend(_messages)

            # Delete all remaining existing dates
            to_delete = []
            for date in existing_dates:
                if date not in new_dates:
                    to_delete.append(date)
            if to_delete:
                _messages = self.delete_dates(",".join(to_delete))
                messages.extend(_messages)
                        
            # Delete existing users
            _messages = self.delete_users()
            messages.extend(_messages)
        except (ValueError, HTTPError) as e:
            messages.append(str(e))

        return messages
    
    def __calculate_combination_of_votes(self, votes_for_specific_date, *args):
        count = 0
        for arg in args:
            count += votes_for_specific_date[arg]
        return count
            
    def create_plot(self, dates=None):
        messages = []
        
        votes, _messages =  self.get_votes_by_date(dates)
        messages.extend(_messages)
        
        if len(votes) > 7:
            self.log_message(f'Only the first 7 dates will be displayed. {len(votes)} dates were found.', messages)
            votes = votes[:7]
        labels = [vote['date'] for vote in votes]
        yes_count = [int(vote['yes_count']) for vote in votes]
        no_count = [int(vote['no_count']) for vote in votes]
        maybe_count = [int(vote['maybe_count']) for vote in votes]
        question_count = [int(vote['question_count']) for vote in votes]
        
        _, ax = plt.subplots(figsize=(10,5))
        
        colors = {'Ja': 'g', 'Vielleicht': 'y', 'Nein': 'r', 'Keine Angabe': 'grey'}
        
        ax.bar(labels, question_count, color=colors['Keine Angabe'], label='Keine Angabe')
        ax.bar(labels, no_count, color=colors['Nein'], bottom=question_count, label='Nein')
        ax.bar(labels, maybe_count, color=colors['Vielleicht'], bottom=list(map(add, question_count, no_count)), label='Vielleicht')
        ax.bar(labels, yes_count, color=colors['Ja'], bottom=list(map(add, question_count, list(map(add, no_count, maybe_count)))), label='Ja')
        
        ax.set_ylabel("Stimmen")
        ax.legend()
        
        # Save the chart as a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        return buf, messages
        