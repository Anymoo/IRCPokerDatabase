import os
from irc_poker_data_set import IrcPokerData as ipd

basedir = os.path.abspath(os.path.dirname(__file__))

irc_poker_data = ipd()
irc_poker_data.open()



from irc_poker_db import db_session, PlayerRanking

def player_ranking():
    if db_session.query(PlayerRanking).count() >= db_session.query(ipd.Player).count():
        return
    ### travers all players
    i = 0
    players = ipd.db_session.query(ipd.Player).all()
    for player in players:
        i += 1
        if i%100 == 0:
            db_session.commit()
        p = db_session.query(PlayerRanking).filter(PlayerRanking.player_id==player.id).first()
        if p:
            print(p.__repr__())
            continue
        total_pay = 0
        total_win = 0
        round_num = 0
        rounds = ipd.db_session.query(ipd.Round).filter(ipd.Round.player_id==player.id).all()
        for round in rounds:
            total_pay += round.pay
            total_win += round.win
            round_num += 1
        average_points = (total_win-total_pay)/round_num
        player_ranking = PlayerRanking(player_id=player.id, 
                                        player_name=player.player_name, 
                                        average_points=average_points,
                                        total_pay=total_pay,
                                        total_win=total_win,
                                        round_num=round_num)
        print(player_ranking.__repr__())
        db_session.add(player_ranking)
    db_session.commit()


player_ranking()
