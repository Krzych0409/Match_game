"""The game requires the 'tk' library to be installed"""
import tkinter as tk
from random import shuffle
import json
import os
from random import randrange


class Game:
    """Whole game run in this class"""
    def __init__(self):
        self.levels = ('3', '6', '10', '15', '28')

    def new_game(self, pairs=3):
        """Creating window of game and selection of images."""
        self.number_of_pairs_str = str(pairs)

        # If exist last game, delete old game
        try: self.game_destroy()
        except: pass

        self.frame = tk.Frame(root)
        self.frame.pack()
        root.title(f'Match - {self.number_of_pairs_str} pairs')

        # Creating a sheet of cards. Rows and columns.
        if self.number_of_pairs_str == '3':
            self.number_of_row = 2
            self.number_of_column = 3
        elif self.number_of_pairs_str == '6':
            self.number_of_row = 3
            self.number_of_column = 4
        elif self.number_of_pairs_str == '10':
            self.number_of_row = 4
            self.number_of_column = 5
        elif self.number_of_pairs_str == '15':
            self.number_of_row = 5
            self.number_of_column = 6
        elif self.number_of_pairs_str == '28':
            self.number_of_row = 7
            self.number_of_column = 8

        self.card_click_history = []
        self.image_list = []
        self.all_images = list(range(1, 31))
        self.number_of_moves = 0

        # Selecting the images.
        for i in range(pairs):
            self.image_list.append(self.all_images.pop(randrange(len(self.all_images))))
        # All cards in list * 2
        self.image_list *= 2

        # Mixed images in list
        shuffle(self.image_list)

        # Making a list with [] * 'self.number_of_row'
        self.fields = [[] for i in range(self.number_of_row)]

        # Making objects class 'Field' and add to the list 'self.fields'
        for row in range(self.number_of_row):
            for column in range(self.number_of_column):
                self.fields[row].append(Field(self.image_list.pop(0), row, column, self))

        # Making menu and add to the 'root'
        self.menu = tk.Menu()
        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label='3 pars', command=lambda: self.new_game(3))
        self.filemenu.add_command(label='6 pars', command=lambda: self.new_game(6))
        self.filemenu.add_command(label='10 pars', command=lambda: self.new_game(10))
        self.filemenu.add_command(label='15 pars', command=lambda: self.new_game(15))
        self.filemenu.add_command(label='28 pars', command=lambda: self.new_game(28))

        self.menu.add_cascade(label='New game', menu=self.filemenu)
        self.menu.add_cascade(label='Ranking', command=self.show_ranking)
        root.config(menu=self.menu)

        self.get_ranking_json()
        # Making bottom frame (display the number of moves and the record)
        self.frame_player = tk.Frame(root)
        self.label_moves = tk.Label(self.frame_player, text=f'Moves: {self.number_of_moves}', font=('calibre', 14, 'normal'))
        self.label_moves.pack(side=tk.TOP)
        try:
            self.label_champion = tk.Label(self.frame_player, text=f'Champion: {self.ranking[self.number_of_pairs_str]["name"][0]} --> {self.ranking[self.number_of_pairs_str]["moves"][0]}',
                                           font=('calibre', 14, 'normal'))
        except IndexError:
            self.label_champion = tk.Label(self.frame_player, text=f'Champion: ---',
                                           font=('calibre', 14, 'normal'))
        self.label_champion.pack(side=tk.BOTTOM)
        self.frame_player.pack()

    def check_pair(self, click_card):
        """Checking for a match. Object of field is argument."""
        # Adding field to the 'self.card_click_history'
        if len(self.card_click_history) == 0:
            self.card_click_history.append(click_card)

        # If the second card is exposed
        elif len(self.card_click_history) == 1:
            self.card_click_history.append(click_card)
            self.number_of_moves += 1
            # Display number of move
            self.label_moves.config(text=f'Moves: {self.number_of_moves}')

            # If the cards match then turn off the activity of the fields.
            if self.card_click_history[0].name == self.card_click_history[1].name:
                self.card_click_history[0].set_disable_field()
                self.card_click_history[1].set_disable_field()
            # If the cards don't match then wait and load the default image.
            elif self.card_click_history[0].name != self.card_click_history[1].name:
                self.frame.after(200, self.card_click_history[0].set_default_image())
                self.frame.after(200, self.card_click_history[1].set_default_image())
            # If player win open the 'win_window'
            if self.end_game() == True:
                self.win_window()

            # Delete filds of moves
            self.card_click_history = []

    def end_game(self):
        """Check that at least one field is active"""
        for row in self.fields:
            for field in row:
                if field.field_activity == True:
                    return False

        return True

    def win_window(self):
        """Creating top window. If the player's score is better than the fifth ranked player then add his score to the ranking."""
        # If the score is worse than the fifth ranking score, do not add the player's score to the ranking.
        try:
            if self.number_of_moves >= self.ranking[self.number_of_pairs_str]['moves'][4]:
                return 0
        except:
            pass

        # Add the player's score to the ranking
        self.window_win = tk.Toplevel(root)
        self.window_win.title('YOU WIN !!!')
        self.label_end_moves = tk.Label(self.window_win, text=f'Moves: {self.number_of_moves}\n\nYour name:', font=('calibre', 14, 'normal'), pady=10)
        self.label_end_moves.pack()
        self.entry_name = tk.Entry(self.window_win, font=('calibre', 14, 'normal'), width=23)
        self.entry_name.pack(fill='x')
        self.entry_name.focus_set()
        self.button_save = tk.Button(self.window_win, text='Save my score', command=self.save_sore, pady=3, padx=10)
        self.button_save.pack()
        self.window_win.bind('<Return>', self.save_sore)

    def get_ranking_json(self):
        """If file: ranking.json does not exist than create a file with an empty ranking. Load ranking.json into the variable 'self.ranking'"""
        if not os.path.isfile('ranking.json'):
            self.ranking = {'3': {'name': [], 'moves': []}, '6': {'name': [], 'moves': []}, '10': {'name': [], 'moves': []},
                            '15': {'name': [], 'moves': []}, '28': {'name': [], 'moves': []}}
            self.file = open('ranking.json', 'w')
            json.dump(self.ranking, self.file)
            self.file.close()
        else:
            self.file = open('ranking.json')
            self.ranking = json.load(self.file)
            self.file.close()

    def save_sore(self, event=0):
        """Adding the player's score to the ranking and sorting the ranking by the number of moves."""
        self.button_save['state'] = tk.DISABLED
        self.name = self.entry_name.get()

        # Add player's sore to the ranking
        self.ranking[self.number_of_pairs_str]['name'].append(self.name)
        self.ranking[self.number_of_pairs_str]['moves'].append(self.number_of_moves)

        for game in self.ranking.values():
            # Sort 2 list, key is 'moves' list.
            game['name'] = [x for _, x in sorted(zip(game['moves'], game['name']), key=lambda pair: pair[0])]
            game['moves'].sort()

        # Save in file the new ranking.
        self.file = open('ranking.json', 'w')
        json.dump(self.ranking, self.file)
        self.file.close()

        # Close top window
        self.window_win.destroy()

    def show_ranking(self):
        """Display ranking in top window"""
        self.window_ranking = tk.Toplevel()
        self.window_ranking.title('Ranking')
        # Each level has its own frame.
        self.ranking_frames = []

        for i, lvl in enumerate(self.levels):
            self.ranking_frames.append(tk.LabelFrame(self.window_ranking, text=f'{lvl} pairs:', font=('calibre', 12)))
            for place in range(5):
                try:
                    if place == 0:
                        self.add_label = tk.Label(self.ranking_frames[i], text=f'{self.ranking[lvl]["moves"][place]} ---> {self.ranking[lvl]["name"][place]}',
                                                  justify=tk.LEFT, anchor='w', font=('calibre', 12), fg='green', pady=10).pack(fill='x')
                    else:
                        self.add_label = tk.Label(self.ranking_frames[i], text=f'{self.ranking[lvl]["moves"][place]} ---> {self.ranking[lvl]["name"][place]}',
                                                  justify=tk.LEFT, anchor='w', font=('calibre', 10)).pack(fill='x')
                except IndexError:
                    # If the ranking place does not exist, add an empty label.
                    self.add_label = tk.Label(self.ranking_frames[i], text=f'').pack(fill='x')
            self.ranking_frames[i].grid(row=0, column=i, padx=25, pady=20)

    def game_destroy(self):
        """Destroy all frames"""
        self.frame.destroy()
        self.frame_player.destroy()


class Field:
    """The class create a buttons of field and set button activity"""
    def __init__(self, name, row, column, game):
        self.frame = game.frame
        self.name = name
        self.image = tk.PhotoImage(file=rf'images\{self.name}.png')
        self.default_image = tk.PhotoImage(file=r'images\0.png')
        self.row = row
        self.column = column
        self.field_activity = True
        self.field_button = tk.Button(self.frame, image=self.default_image, command=self.click).grid(row=self.row, column=self.column)

    def set_disable_field(self):
        # Set activity on False and set own image.
        self.field_button = tk.Button(self.frame, image=self.image, state=tk.DISABLED).grid(row=self.row, column=self.column)
        self.field_activity = False

    def set_default_image(self):
        # Set activity on True and set default image.
        self.field_button = tk.Button(self.frame, image=self.default_image, command=self.click).grid(row=self.row, column=self.column)
        self.field_activity = True

    def click(self):
        # If field is activ, change activity to False and display image. Calls the 'check_pair' method.
        if self.field_activity == True:
            self.field_button = tk.Button(self.frame, image=self.image).grid(row=self.row, column=self.column)
            self.field_activity = False
            self.frame.update()
            game.check_pair(self)


root = tk.Tk()
# Blocking the resizing of window
root.resizable(False, False)

game = Game()
game.new_game()

root.mainloop()