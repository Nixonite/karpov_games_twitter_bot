import tweepy
import boto3
import json
import chess.pgn
import random
import requests

def fetch_twitter_secrets():
  secret_name = 'twitter-secrets'
  region_name = 'us-west-2'

  session = boto3.session.Session()
  client = session.client(
    service_name='secretsmanager',
    region_name=region_name
  )

  secrets_json = json.loads(
    client.get_secret_value(SecretId = secret_name)['SecretString']
    )
  return secrets_json

def get_karpov_games():
  games = []
  with open('AnatolyKarpov.pgn') as pgn:
    while True:
      game = chess.pgn.read_game(pgn)
      if game is None:
        break  
      games.append(game)
  return games

def get_lichess_analysis_board_url(karpov_pgn):
  resp = requests.post("https://lichess.org/import", data={"pgn": karpov_pgn})
  if resp.status_code == 200:
    return resp.url
  else:
    return None

def is_clean_header(g):
  if ('?' not in g.headers['White']) and ('?' not in g.headers['Black']) \
    and ('?' not in g.headers['Date']):
    return True
  else:
    return False

if __name__=="__main__":
  secrets = fetch_twitter_secrets()

  consumer_key = secrets['consumer_key']
  consumer_secret = secrets['consumer_secret']
  access_token = secrets['access_token']
  access_token_secret = secrets['access_token_secret']
  
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  
  api = tweepy.API(auth)
  
  karpov_games = get_karpov_games()
  
  good_games = list(filter(is_clean_header, karpov_games))

  random_game = random.choice(good_games)

  lichess_link = get_lichess_analysis_board_url(random_game)

  if lichess_link is not None:
    white = random_game.headers['White']
    black = random_game.headers['Black']
    game_date = random_game.headers['Date'].replace('.','-')
    api.update_status("{} vs {} ({}) {}".format(
      white,
      black,
      game_date,
      lichess_link
    ))