import os
import util_db
from sqlalchemy import Column, Integer, String

basedir = os.path.abspath(os.path.dirname(__file__))


class Player(util_db.DBBase):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    player_name = Column(String(64))

    def __repr__(self):
        return "<Player(player_name='%s')>" % (self.player_name)


class Round(util_db.DBBase):
    __tablename__ = 'rounds'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer)
    round_id = Column(String(16))
    player_num = Column(Integer)
    order = Column(Integer)
    pre_flop = Column(String(8))
    flop = Column(String(8))
    turn = Column(String(8))
    river = Column(String(8))
    chips = Column(Integer)
    pay = Column(Integer)
    win = Column(Integer)
    card_1 = Column(String(8))
    card_2 = Column(String(8))

    def __repr__(self):
        return ("<Player(player_id={player_id}, "
                "round_id={round_id}, "
                "player_num={player_num}, "
                "order={order}, "
                "pre_flop={pre_flop}, "
                "flop={flop}, "
                "turn={turn}, "
                "river={river}, "
                "chips={chips}, "
                "pay={pay}, "
                "win={win}, "
                "card_1={card_1}, "
                "card_2={card_2}, "
                ")>".format(player_id=self.player_id,
                            round_id=self.round_id,
                            player_num=self.player_num,
                            order=self.order,
                            pre_flop=self.pre_flop,
                            flop=self.flop,
                            turn=self.turn,
                            river=self.river,
                            chips=self.chips,
                            pay=self.pay,
                            win=self.win,
                            card_1=self.card_1,
                            card_2=self.card_2))


class Pot(util_db.DBBase):
    __tablename__ = 'pots'
    id = Column(Integer, primary_key=True)
    round_id = Column(String(16))
    tbd = Column(Integer)
    local_id = Column(Integer)
    player_num = Column(Integer)
    tbd1 = Column(String(16))
    tbd2 = Column(String(16))
    tbd3 = Column(String(16))
    tbd4 = Column(String(16))
    card_1 = Column(String(8))
    card_2 = Column(String(8))
    card_3 = Column(String(8))
    card_4 = Column(String(8))
    card_5 = Column(String(8))

    def __repr__(self):
        return ("<Pot(round_id={round_id}, "
                "tbd={tbd}, "
                "local_id={local_id}, "
                "player_num={player_num}, "
                "tbd1={tbd1}, "
                "tbd2={tbd2}, "
                "tbd3={tbd3}, "
                "tbd4={tbd4}, "
                "card_1={card_1}, "
                "card_2={card_2}, "
                "card_3={card_3}, "
                "card_4={card_4}, "
                "card_5={card_5}, "
                ")>".format(round_id=self.round_id,
                            tbd=self.tbd,
                            local_id=self.local_id,
                            player_num=self.player_num,
                            tbd1=self.tbd1,
                            tbd2=self.tbd2,
                            tbd3=self.tbd3,
                            tbd4=self.tbd4,
                            card_1=self.card_1,
                            card_2=self.card_2,
                            card_3=self.card_3,
                            card_4=self.card_4,
                            card_5=self.card_5))


class Roster(util_db.DBBase):
    __tablename__ = 'roster'
    id = Column(Integer, primary_key=True)
    round_id = Column(String(16))
    player_num = Column(Integer)
    player_id = Column(Integer)

    def __repr__(self):
        return ("<Roster(round_id={round_id}, "
                "player_num={player_num}, "
                "player_id={player_id}"
                ")>".format(round_id=self.round_id,
                            player_num=self.player_num,
                            player_id=self.player_id))


class PlayerRanking(util_db.DBBase):
    __tablename__ = 'player_ranking'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer)
    player_name = Column(String(64))
    average_points = Column(Integer)
    total_pay = Column(Integer)
    total_win = Column(Integer)
    round_num = Column(Integer)

    def __repr__(self):
        return ("<PlayerRanking(player_id={player_id}, "
                "player_name={player_name}, "
                "average_points={average_points},"
                "total_pay={total_pay},"
                "total_win={total_win},"
                "round_num={round_num}"
                ")>".format(player_id=self.player_id,
                            player_name=self.player_name,
                            average_points=self.average_points,
                            total_pay=self.total_pay,
                            total_win=self.total_win,
                            round_num=self.round_num,
                            ))


the_db_file_path = '{basedir}/../data/poker_db.sqlite'.format(basedir=basedir)
the_db_url = 'sqlite:///'+the_db_file_path
db_session = util_db.open(the_db_url)
