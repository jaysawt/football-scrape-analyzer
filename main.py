from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv

chrome_driver_path = "C:\Developer\chromedriver.exe"

footmob_urls = ['https://www.fotmob.com/leagues/87/table/laliga',
                'https://www.fotmob.com/leagues/47/table/premier-league',
                'https://www.fotmob.com/leagues/54/overview/bundesliga',
                'https://www.fotmob.com/leagues/55/table/serie',
                'https://www.fotmob.com/leagues/53/table/ligue-1',
                'https://www.fotmob.com/leagues/57/table/eredivisie',
                'https://www.fotmob.com/leagues/61/table/liga-portugal']


offense_defense = [
    'https://1xbet.whoscored.com/Regions/206/Tournaments/4/Seasons/9682/Stages/22176/TeamStatistics/Spain-LaLiga-2023-2024',
    'https://1xbet.whoscored.com/Regions/252/Tournaments/2/Seasons/9618/Stages/22076/TeamStatistics/England-Premier-League-2023-2024',
    'https://1xbet.whoscored.com/Regions/81/Tournaments/3/Seasons/9649/Stages/22128/TeamStatistics/Germany-Bundesliga-2023-2024',
    'https://1xbet.whoscored.com/Regions/108/Tournaments/5/Seasons/9659/Stages/22143/TeamStatistics/Italy-Serie-A-2023-2024',
    'https://1xbet.whoscored.com/Regions/74/Tournaments/22/Seasons/9635/Stages/22105/TeamStatistics/France-Ligue-1-2023-2024',
    'https://1xbet.whoscored.com/Regions/155/Tournaments/13/Seasons/9705/Stages/22225/TeamStatistics/Netherlands-Eredivisie-2023-2024',
    'https://1xbet.whoscored.com/Regions/177/Tournaments/21/Seasons/9730/Stages/22254/TeamStatistics/Portugal-Liga-2023-2024'
]

top20_url = 'https://1xbet.whoscored.com/Statistics'


def create_csv():
    # creating a csv file with  headers
    headers = ['League', 'Team1', 'Team2', 'Team1 Position', 'Team2 Position', 'Team1 Form', 'Team2 Form',
               'Head to Head', 'Team1 Insights', 'Team2 Insights', 'Team1 Home Rank in League(Out of 20)',
               'Team2 Away Rank in League(Out of 20)']
    with open('football statistic.csv', 'w', newline='') as csv_file:
        csv_write = csv.writer(csv_file)
        csv_write.writerow(headers)


def update_csv_from_footmob():
    # Get the Top 6 teams in each league(laliga, pl, seria a, french league, edervise, portugal liga)
    global team1_insight, team2_insight
    for url in footmob_urls:
        driver.get(url)
        time.sleep(2)
        dynamic_content = driver.page_source
        soup = BeautifulSoup(dynamic_content, 'html.parser')
        teams = [team.text for team in soup.findAll(class_='css-ui511c-mftBasicTextStyle')]  # all 20 teams from table
        form = []  # last 3 matches status
        for i in soup.findAll(class_='e2d61un1'):
            for j in i:
                z = [k.text for k in j.findAll('a')]
                form.append(','.join(z))

        for i in soup.select(selector='a.e1cz97n70')[:6]:
            driver.get(f"https://www.fotmob.com{i['href']}")
            time.sleep(0.5)
            page = driver.page_source
            soup2 = BeautifulSoup(page, 'html.parser')

            league = soup2.select_one(selector='div.ehe3dm90 h2').text

            team1 = soup2.select_one(selector='span.css-qjczke-TeamName span.e1rexsj40').text
            team2 = soup2.select_one(selector='span.css-1g9van0-TeamName span.e1rexsj40').text

            team1_position = teams.index(team1) + 1
            team2_position = teams.index(team2) + 1

            team1_stats = form[teams.index(team1)]
            team2_stats = form[teams.index(team2)]

            win_loss = [i.text for i in soup2.select(selector='div.ew2zkhp11 span.ew2zkhp10')]
            head_2_head = f'Win{win_loss[0]} Draw{win_loss[1]} Win{win_loss[2]}'

            insights = [i.text for i in soup2.select(selector='ul.eyeqjsw3 li.eyeqjsw2 p')]
            try:
                team1_insight = f'{insights[0]}\n{insights[1]}\n{insights[2]}'  # change later if doesn't fit on excel sheet
            except IndexError:
                pass
            try:
                team2_insight = f'{insights[3]}\n{insights[4]}\n{insights[5]}'
            except IndexError:
                pass

            with open('football statistic.csv', 'a', newline='') as csv_file:
                csv_write = csv.writer(csv_file)
                csv_write.writerow([league, team1, team2, team1_position, team2_position, team1_stats, team2_stats,
                                    head_2_head, team1_insight, team2_insight])

        with open('football statistic.csv', 'a', newline='') as csv_file:
            csv_write = csv.writer(csv_file)
            csv_write.writerow([])    # space to separate out different league teams


############################################################################################
# finding defensive and offensive home and away rank
def defense_offense(where):
    driver.find_element(By.CSS_SELECTOR, f'#stage-team-stats-summary #field dd a[data-value={where}]').click()
    time.sleep(3)
    soup3 = BeautifulSoup(driver.page_source, 'html.parser')
    home_away = soup3.select(
        selector=f'#statistics-team-table-summary div.semi-attached-table #top-team-stats-summary-grid #top-team-stats-summary-content tr td.overflow-text a')
    game = [i.text.split('. ')[1] for i in home_away]
    return game


# Correcting the mismatching data
def correct_teams(data):
    if 'Athletic Bilbao' in data:
        data[data.index('Athletic Bilbao')] = 'Athletic Club'
    if 'AC Milan' in data:
        data[data.index('AC Milan')] = 'Milan'
    if 'Verona' in data:
        data[data.index('Verona')] = 'Hellas Verona'
    for tup in [('West Ham', 'West Ham United'), ('Tottenham', 'Tottenham Hotspur'),
                ('Brighton', 'Brighton & Hove Albion'), ('Newcastle', 'Newcastle United'), ('Wolves', 'Wolverhampton Wanderers'),
                ('Bournemouth', 'AFC Bournemouth'), ('Luton', 'Luton Town')]:
        if tup[0] in data:
            data[data.index(tup[0])] = tup[1]
    for tup1 in [('Bayern Munich', 'Bayern München'), ('Hoffenheim', 'TSG Hoffenheim'),
                ('Freiburg', 'SC Freiburg'), (' Augsburg', 'FC Augsburg'), ('Bochum', 'VfL Bochum'),
                ('FC Koln', '1. FC Köln'), ('Borussia M.Gladbach', "Borussia M'Gladbach"),
                ('SV Darmstadt', 'Darmstadt')]:
        if tup1[0] in data:
            data[data.index(tup1[0])] = tup1[1]
    return data


# defensive offensive
def defensive_offensive_stats():
    for url in offense_defense:
        driver.get(url)
        time.sleep(3)
        try:
            driver.find_element(By.CLASS_NAME, 'webpush-swal2-close').click()
            time.sleep(1)
        except:
            pass

        home_rank = defense_offense("Home")
        home_rank_corrected = correct_teams(home_rank)   # This is to manually correct mismatching data between 2 sites
        away_rank = defense_offense("Away")
        away_rank_corrected = correct_teams(away_rank)

        with open('football statistic.csv', 'r', newline='') as csv_file:
            data = list(csv.reader(csv_file))
            for dat in data[1:]:   # 1:len(list(data))-1
                team1_home_rank, team2_away_rank = '', ''  # This is done to fill cells when data is not available
                for home in home_rank_corrected:      # this had to be done because of data mismatch between 2 sites
                    try:    # Done to encounter empty rows in Excel sheets
                        if home in dat[1]:
                            team1_home_rank = home_rank.index(home) + 1
                            dat.append(team1_home_rank)
                    except IndexError:
                        pass
                for away in away_rank_corrected:      # this had to be done because of data mismatch between footmob and whoscored
                    try:
                        if away in dat[2]:
                            team2_away_rank = away_rank.index(away) + 1
                            dat.append(team2_away_rank)
                    except IndexError:
                        pass
        with open('football statistic.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(data)


def top_20_teams():
    driver.get(top20_url)
    soup4 = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup4.select(selector='#top-team-stats-summary-content tr td.overflow-text a')
    with open('football statistic.csv', 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([])
        csv_writer.writerow(['Top 20 Teams in Europe (overall statistics)'])
        for i in table:
            csv_writer.writerow([i.text])


if __name__ == '__main__':
    # initialize the driver
    option = webdriver.ChromeOptions()
    option.add_experimental_option('detach', True)
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=option)
    create_csv()
    update_csv_from_footmob()
    defensive_offensive_stats()
    top_20_teams()
    driver.quit()


#4.11.2