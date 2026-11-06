from nba_api.stats.endpoints import leaguegamefinder,playbyplayv3,playercareerstats
from nba_api.stats.static import teams
import pandas as pd,time
from scipy import stats
import matplotlib.pyplot as plt


def find_team_info(abreviation):
    if not isinstance(abreviation,str): 
        raise TypeError("Please enter a string as abbreviation")
    
    nba_teams = teams.get_teams()
    team = [team for team in nba_teams if team["abbreviation"]== abreviation][0]
    if team is None: 
        raise ValueError("No team with that abreviation")
    return team

def find_team_ID(abreviation):
    if not isinstance(abreviation,str): 
        raise TypeError("Please enter a string as abbreviation")
    
    nba_teams = teams.get_teams()
    team = [team for team in nba_teams if team["abbreviation"]== abreviation][0]
    if team is None: 
        raise ValueError("No team with that abreviation")
    team_id = team["id"]
    return team_id

def find_games(abreviation,season= "2026-27",season_types = ("Regular Season"),columns =None):
    team_id = find_team_ID(abreviation)
    frames = []
    for st in season_types:
        finder = leaguegamefinder.LeagueGameFinder(
        team_id_nullable =team_id,
        season_nullable = season,
        season_type_nullable = st,)
        df = finder.get_data_frames()[0]
        df["SEASON_TYPE"] =st; 
        df = df [["SEASON_ID","TEAM_ABBREVIATION","GAME_ID","SEASON_TYPE","PLUS_MINUS","GAME_DATE","PF"]]    
        frames.append(df)
    games = pd.concat(frames,ignore_index=True)
    games["GAME_DATE"] = pd.to_datetime(games["GAME_DATE"])
    if columns is not None:
        games = games[columns]
    return games


def season_foul_comparison(abbreviation,seasons1,seasons2): #season 1 ("2026-27",("Pre Season","Regular Season"))
    cols  = ["GAME_ID", "GAME_DATE", "SEASON_TYPE", "PF"]
    data_season1 = find_games(abbreviation,seasons1[0],seasons1[1],columns = cols)
    data_season2 = find_games(abbreviation,seasons2[0],seasons2[1],columns = cols)
    total_pf_s1 = data_season1["PF"].sum()
    total_pf_s2 = data_season2["PF"].sum()
    average_pf_1 = round(float(data_season1["PF"].mean()),3)
    average_pf_2 = round(float(data_season2["PF"].mean()),3)
    median_pf_1 = round(float(data_season1["PF"].median()),3)
    median_pf_2 = round(float(data_season2["PF"].median()),3)
    sentence = f"{season1[0]} mean PF: {average_pf_1} \n{seasons2[0]} mean PF: {average_pf_2}\n{season1[0]} median PF: {median_pf_1} \n{seasons2[0]} median PF: {median_pf_2}"
    season1_PF = data_season1["PF"]
    season2_PF = data_season2["PF"]
    result = stats.ttest_ind(season1_PF,season2_PF,equal_var=False)
    print(f"t = {result.statistic:.2f}, p = {result.pvalue:.4f}")
    return sentence 


def get_all_games(season): 
    finder = leaguegamefinder.LeagueGameFinder(
        season_nullable= season,
        season_type_nullable= "Regular Season",
        league_id_nullable='00'
    )
    df  = finder.get_data_frames()[0]
    df["SEASON"] = season
    return df[["SEASON", "TEAM_ABBREVIATION", "GAME_ID", "GAME_DATE", "PF"]]

def all_games_pf_avg(season): 
    df = get_all_games(season)
    team_avg = df.groupby("TEAM_ABBREVIATION")["PF"].mean().sort_values(ascending=False)
    team_avg.plot(kind="bar", figsize=(14, 6))
    #plt.tight_layout()
    #plt.show()
    return team_avg

def allgames_PF_comparison(season1,season2,cutoff2=None): # we cannot take all of last season/ Or we rule out the early season explenation 
    games_this = get_all_games(season1)
    games_last = get_all_games(season2)
    games_this ["GAME_DATE"]= pd.to_datetime(games_this["GAME_DATE"]) 
    games_last["GAME_DATE"]= pd.to_datetime(games_last["GAME_DATE"])
    if cutoff2 is not None:
        days_in = (games_this["GAME_DATE"].max() - games_this["GAME_DATE"].min()).days
        cutoff = games_last["GAME_DATE"].min() + pd.Timedelta(days=days_in)
        games_last = games_last[games_last["GAME_DATE"] <= cutoff]
    pf_this = games_this.groupby("GAME_ID")["PF"].sum()
    pf_last = games_last.groupby("GAME_ID")["PF"].sum()
    result = stats.ttest_ind(pf_this, pf_last, equal_var=False)
    print(f"Mean fouls per game: {pf_this.mean():.2f} vs {pf_last.mean():.2f}")
    print(f"t = {result.statistic:.2f}")
    print(f"p = {result.pvalue:.4g}")
    print("Significant" if result.pvalue < 0.05 else "Not significant")
    return 0 
    


print(allgames_PF_comparison('2025-26','2026-27',cutoff2="2025-11-06"))
#season1 = ("2026-27",("Pre Season","Regular Season"))
#season2 = (("2025-26"),("Pre Season","Regular Season"))
#print(season_foul_comparison("NYK",season1,season2))