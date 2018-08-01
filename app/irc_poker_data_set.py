import os
import json
import re
import tarfile
import urllib
import util_file
from irc_poker_db import db_session, Player, Pot, Roster, Round

basedir = os.path.abspath(os.path.dirname(__file__))

class IrcPokerData():
    db_session = db_session
    Player = Player
    Pot = Pot
    Roster = Roster
    Round = Round
    player_name_id_map = {}
    poker_cards = [
        'As', 'Ah', 'Ad', 'Ac',
        'Ks', 'Kh', 'Kd', 'Kc',
        'Qs', 'Qh', 'Qd', 'Qc',
        'Js', 'Jh', 'Jd', 'Jc',
        'Ts', 'Th', 'Td', 'Tc',
        '9s', '9h', '9d', '9c',
        '8s', '8h', '8d', '8c',
        '7s', '7h', '7d', '7c',
        '6s', '6h', '6d', '6c',
        '5s', '5h', '5d', '5c',
        '4s', '4h', '4d', '4c',
        '3s', '3h', '3d', '3c',
        '2s', '2h', '2d', '2c']

    def __init__(self):
        pass

    def open(self):
        download_extract_errors = []
        cprg_irc_poker_db_url = 'http://poker.cs.ualberta.ca/IRC/IRCdata.tgz'
        print('CPRG IRC Poker Database URL {url}'.format(url=cprg_irc_poker_db_url))
        local_file_name = cprg_irc_poker_db_url.split('/')[-1]
        print('Local db file name {file}'.format(file=local_file_name))
        dest_tarfile_path = '{basedir}/../data/{file}'.format(basedir=basedir, file=local_file_name)

        if not os.path.exists(dest_tarfile_path):
            print('Downloading the file to {file}...'.format(file=dest_tarfile_path))
            cprg_irc_poker_db_opener = urllib.URLopener()
            cprg_irc_poker_db_opener.retrieve(cprg_irc_poker_db_url, dest_tarfile_path)

        db_folder, local_file_extension = os.path.splitext(local_file_name)
        if not os.path.isdir(db_folder):
            print('Extracting folder {folder}...'.format(folder=db_folder))
            tar = tarfile.open(dest_tarfile_path)
            tar.extractall()
            tar.close()

            files = util_file.get_name_list_of_files(db_folder)
            for file in files:
                file_name, ext = os.path.splitext(file)
                if ext == '.tgz' or ext == '.gz':
                    game_file = '{folder}/{file}'.format(folder=db_folder, file=file)
                    print('Extracting file {file}...'.format(file=game_file))
                    game_folder = '{folder}/{file}'.format(folder=db_folder, file=file_name)
                    # if not os.path.isdir(game_folder):
                    try:
                        tar = tarfile.open(game_file)
                        tar.extractall()
                    except:
                        download_extract_errors.append('{file} untar failed'.format(file=game_file))
                    else:
                        pass
                    finally:
                        tar.close()
        
        if len(download_extract_errors) > 0:
            print('Downloading and extracting errors: {error_counts}'.format(error_counts=len(download_extract_errors)))
            for error_msg in download_extract_errors:
                print('!!!EXCEPT {msg}'.format(msg=error_msg))


        player_num = db_session.query(Player).count()
        if player_num <= 0:
            self.traverse_records(self.parse_players)
            player_num = db_session.query(Player).count()
            print('Total players {player_num}'.format(player_num=str(player_num)))
            round_num = db_session.query(Round).count()
            print('Total rounds {round_num}'.format(round_num=str(round_num)))
            self.round_data_clean()

        pot_num = db_session.query(Pot).count()
        if pot_num <= 0:
            self.traverse_records(self.parse_pot)
            pot_num = db_session.query(Pot).count()
            print('Total rounds {pot_num}'.format(pot_num=str(pot_num)))
            self.pot_data_clean()

        roster_num = db_session.query(Roster).count()
        if roster_num <= 0:
            self.traverse_records(self.parse_roster)
            roster_num = db_session.query(Roster).count()
            print('Total rounds {roster_num}'.format(roster_num=str(roster_num)))
            self.roster_data_clean()


    def traverse_records(self, parser):
        holdems = [ 
            '/../data/holdem/', 
            '/../data/holdem1/', 
            '/../data/holdem2/', 
            '/../data/holdem3/', 
            '/../data/holdemii/', 
            '/../data/holdempot/' 
        ]
        error_records = []
        for h in holdems:
            holdem = '{basedir}{h}'.format(basedir=basedir,h=h)
            print('Opening {holdem}...'.format(holdem=holdem))
            monthly_records = util_file.get_sub_folder_list(holdem)
            for month_data in monthly_records:
                month_data_root = holdem + month_data
                print('Parsing {month_data_root}...').format(month_data_root=month_data_root)
                parser(month_data_root, error_records)
            db_session.commit()
        print('Traverse record errors: {error_counts}'.format(error_counts=len(error_records)))
        for error_msg in error_records:
            print('!!!EXCEPT {msg}'.format(msg=error_msg))


    def parse_players(self, month_data_root, player_records_errors):
        pdb_path = month_data_root + '/pdb/'
        if not os.path.isdir(pdb_path):
            return
        player_records = util_file.get_name_list_of_files(pdb_path)
        for player in player_records:
            print('Parsing {month_data_root}-{player}...'.format(month_data_root=month_data_root, player=player))
            filename = pdb_path+player
            player_catch = set()
            with open(filename) as data_file:
                for line in data_file:
                    try:
                        round_raw = line.split()
                        the_round = {}
                        player_name = re.sub('[[\]]', '', round_raw[0])
                        the_round['player_name'] = player_name
                        the_round['round_id'] = round_raw[1]
                        the_round['player_num'] = int(round_raw[2])
                        the_round['order'] = int(round_raw[3])
                        the_round['pre_flop'] = round_raw[4]
                        the_round['flop'] = round_raw[5]
                        the_round['turn'] = round_raw[6]
                        the_round['river'] = round_raw[7]
                        the_round['chips'] = int(round_raw[8])
                        the_round['pay'] = int(round_raw[9])
                        the_round['win'] = int(round_raw[10])
                        if len(round_raw)>11:
                            the_round['card_1'] = round_raw[11]
                        if len(round_raw)>12:
                            the_round['card_2'] = round_raw[12]
                    except:
                        player_records_errors.append('{filename}-{player_name} except'.format(filename=filename, player_name=player_name))
                    else:
                        if player_name not in player_catch:
                            player_catch.add(player_name)
                            player = db_session.query(Player).filter_by(player_name=player_name).first()
                            if player is None:
                                player = Player(player_name=player_name)
                                db_session.add(player)
                                db_session.flush()
                        # round_data = db_session.query(Round).filter(Round.player_id==player.id).filter(Round.round_id==the_round['round_id']).first()
                        round_data = None
                        if round_data is None:
                            round_data = Round(player_id=player.id,
                                              round_id=the_round['round_id'],
                                              player_num=the_round['player_num'],
                                              order=the_round['order'],
                                              pre_flop=the_round['pre_flop'],
                                              flop=the_round['flop'],
                                              turn=the_round['turn'],
                                              river=the_round['river'],
                                              chips=the_round['chips'],
                                              pay=the_round['pay'],
                                              win=the_round['win'])
                            if 'card_1' in the_round:
                                round_data.card_1 = the_round['card_1']
                            if 'card_2' in the_round:
                                round_data.card_2 = the_round['card_2']
                            db_session.add(round_data)


    def parse_pot(self, month_data_root, pot_records_errors):
        filename = month_data_root + '/hdb'
        if not os.path.exists(filename):
            return
        with open(filename) as data_file:
            for line in data_file:
                try:
                    pot_raw = line.split()
                    the_round = {}
                    the_round['round_id'] = pot_raw[0]
                    the_round['tbd'] = pot_raw[1]
                    the_round['local_id'] = int(pot_raw[2])
                    the_round['player_num'] = int(pot_raw[3])
                    if len(pot_raw)>4:
                        the_round['tbd1'] = pot_raw[4]
                    if len(pot_raw)>5:
                        the_round['tbd2'] = pot_raw[5]
                    if len(pot_raw)>6:
                        the_round['tbd3'] = pot_raw[6]
                    if len(pot_raw)>7:
                        the_round['tbd4'] = pot_raw[7]
                    if len(pot_raw)>8:
                        the_round['card_1'] = pot_raw[8]
                    if len(pot_raw)>9:
                        the_round['card_2'] = pot_raw[9]
                    if len(pot_raw)>10:
                        the_round['card_3'] = pot_raw[10]
                    if len(pot_raw)>11:
                        the_round['card_4'] = pot_raw[11]
                    if len(pot_raw)>12:
                        the_round['card_5'] = pot_raw[12]
                except:
                    pot_records_errors.append('{filename} except'.format(filename=filename))
                else:
                    # print(the_round)
                    # pot_data = db_session.query(Pot).filter(Pot.round_id==the_round['round_id']).first()
                    pot_data = None
                    if pot_data is None:
                        pot_data = Pot(round_id=the_round['round_id'],
                                          tbd=the_round['tbd'],
                                          local_id=the_round['local_id'],
                                          player_num=the_round['player_num'])
                        if 'tbd1' in the_round:
                            pot_data.tbd1 = the_round['tbd1']
                        if 'tbd2' in the_round:
                            pot_data.tbd2 = the_round['tbd2']
                        if 'tbd3' in the_round:
                            pot_data.tbd3 = the_round['tbd3']
                        if 'tbd4' in the_round:
                            pot_data.tbd4 = the_round['tbd4']
                        if 'card_1' in the_round:
                            pot_data.card_1 = the_round['card_1']
                        if 'card_2' in the_round:
                            pot_data.card_2 = the_round['card_2']
                        if 'card_3' in the_round:
                            pot_data.card_3 = the_round['card_3']
                        if 'card_4' in the_round:
                            pot_data.card_4 = the_round['card_4']
                        if 'card_5' in the_round:
                            pot_data.card_5 = the_round['card_5']
                        db_session.add(pot_data)


    def parse_roster(self, month_data_root, roster_records_errors):
        filename = month_data_root + '/hroster'
        if not os.path.exists(filename):
            return
        flush_count = 0
        with open(filename) as data_file:
            # load self.player_name_id_map in memory
            if len(self.player_name_id_map) == 0:
                player_records = db_session.query(Player).all()
                for player_rec in player_records:
                    self.player_name_id_map[player_rec.player_name] = player_rec.id
                    # print('{name}-{id}'.format(name=player_rec.player_name, id=str(player_rec.id)))
                print('Make player name-id mapping... {counts} items'.format(counts=len(self.player_name_id_map)))

            for line in data_file:
                try:
                    roster_raw = line.split()
                    the_round = {}
                    the_round['round_id'] = roster_raw[0]
                    the_round['player_num'] = int(roster_raw[1])
                    the_round['players'] = []
                    for i in range(2, len(roster_raw)):
                        the_round['players'].append(roster_raw[i])
                except:
                    roster_records_errors.append('{filename} except'.format(filename=filename))
                else:
                    # print(the_round)
                    for player_name in the_round['players']:
                        # roster_data = db_session.query(Roster).filter(Roster.round_id==the_round['round_id']).filter(Roster.player_id==self.player_name_id_map[player_name]).first()
                        roster_data = None
                        if roster_data is None and player_name in self.player_name_id_map:
                            print('Adding {filename}-{round_id}-{player_name}...'.format(filename=filename, round_id=the_round['round_id'], player_name=player_name))
                            roster_data = Roster(round_id=the_round['round_id'],
                                              player_num=the_round['player_num'],
                                              player_id=self.player_name_id_map[player_name])
                            db_session.add(roster_data)
                            flush_count += 1
                            if flush_count%1000 == 0:
                                db_session.commit()
                        else:
                            roster_records_errors.append('{filename} except'.format(filename=filename))


    def round_data_clean(self):
        db_session.query(Round).filter(Round.player_num > 12).delete()
        db_session.query(Round).filter(Round.player_num < 2).delete()
        db_session.query(Round).filter(~Round.card_1.in_(self.poker_cards)).delete(synchronize_session=False)
        db_session.query(Round).filter(~Round.card_2.in_(self.poker_cards)).delete(synchronize_session=False)
        db_session.commit()
    

    def pot_data_clean(self):
        db_session.query(Pot).filter(Pot.player_num > 12).delete()
        db_session.query(Pot).filter(Pot.player_num < 2).delete()
        db_session.query(Pot).filter(~Pot.card_1.in_(self.poker_cards)).delete(synchronize_session=False)
        db_session.query(Pot).filter(~Pot.card_2.in_(self.poker_cards)).delete(synchronize_session=False)
        db_session.query(Pot).filter(~Pot.card_3.in_(self.poker_cards)).delete(synchronize_session=False)
        db_session.query(Pot).filter(~Pot.card_4.in_(self.poker_cards)).delete(synchronize_session=False)
        db_session.query(Pot).filter(~Pot.card_5.in_(self.poker_cards)).delete(synchronize_session=False)
        db_session.commit()


    def roster_data_clean(self):
        db_session.query(Roster).filter(Roster.player_num > 12).delete()
        db_session.query(Roster).filter(Roster.player_num < 2).delete()
        db_session.commit()

