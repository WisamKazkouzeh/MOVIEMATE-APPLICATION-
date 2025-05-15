import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import json
import datetime
import bcrypt
from PIL import Image, ImageTk
from collections import defaultdict

# Constants
USERS_FILE = "users.json"
RATINGS_FILE = "ratings.json"
MOVIES_FILE = "movies.json"
FRIENDS_FILE = "friends.json"
POSTER_DIR = "posters"

# Color Theme - Yellow and Black
THEME = {
    "bg": "#000000",
    "fg": "#FFFF00",
    "btn_bg": "#333300",
    "btn_fg": "#FFFF00",
    "highlight": "#FFCC00",
    "card_bg": "#1A1A00",
    "card_fg": "#FFFF00",
    "entry_bg": "#333300",
    "entry_fg": "#FFFF00",
    "admin_btn": "#990000"
}

class MovieMateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MovieMate 🎬")
        self.root.geometry("1200x800")
        self.root.configure(bg=THEME["bg"])

        self.users = self.load_data(USERS_FILE, {})
        self.ratings = self.load_data(RATINGS_FILE, {})
        self.movie_db = self.load_data(MOVIES_FILE, None)
        self.friends = self.load_data(FRIENDS_FILE, {})
        self.poster_map = {}

        os.makedirs(POSTER_DIR, exist_ok=True)

        self.create_default_admin()
        if not self.movie_db:
            self.create_mini_database()
        self.load_poster_map()

        self.current_user = None
        self.is_admin = False
        self.setup_ui()

    def load_data(self, filename, default):
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return default
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Failed to load {filename}: {str(e)}")
            return default

    def save_data(self, data, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except (TypeError, IOError) as e:
            messagebox.showerror("Error", f"Failed to save {filename}: {str(e)}")
            return False

    def create_default_admin(self):
        if "admin" not in self.users:
            self.users["admin"] = {
                "password": self.hash_password("admin123"),
                "joined": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_data(self.users, USERS_FILE)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password, hashed):
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except ValueError:
            return False

    def create_mini_database(self):
        self.movie_db = {
            "Action": [
                {"title": "The Dark Knight", "year": "2008", "description": "Batman faces the Joker in Gotham.", "poster": "dark_knight.jpg", "id": 1},
                {"title": "Inception", "year": "2010", "description": "A thief enters dreams to steal secrets.", "poster": "inception.jpg", "id": 2},
                {"title": "Mad Max: Fury Road", "year": "2015", "description": "A post-apocalyptic chase in the wasteland.", "poster": "mad_max.jpg", "id": 3},
                {"title": "Gladiator", "year": "2000", "description": "A Roman general seeks vengeance.", "poster": "gladiator.jpg", "id": 4},
                {"title": "Die Hard", "year": "1988", "description": "A cop battles terrorists in a skyscraper.", "poster": "die_hard.jpg", "id": 5},
                {"title": "John Wick", "year": "2014", "description": "An ex-hitman seeks revenge after his dog is killed.", "poster": "john_wick.jpg", "id": 6},
                {"title": "The Bourne Identity", "year": "2002", "description": "A man with amnesia uncovers his past as a spy.", "poster": "bourne_identity.jpg", "id": 7},
                {"title": "Mission: Impossible - Fallout", "year": "2018", "description": "Ethan Hunt races to stop a global catastrophe.", "poster": "mission_impossible_fallout.jpg", "id": 8},
                {"title": "Skyfall", "year": "2012", "description": "James Bond's loyalty to M is tested.", "poster": "skyfall.jpg", "id": 9},
                {"title": "The Expendables", "year": "2010", "description": "A group of mercenaries takes on a dangerous mission.", "poster": "expendables.jpg", "id": 10},
                {"title": "Black Panther", "year": "2018", "description": "T'Challa becomes king of Wakanda and faces challenges.", "poster": "black_panther.jpg", "id": 11},
                {"title": "Avengers: Endgame", "year": "2019", "description": "The Avengers assemble to undo Thanos' actions.", "poster": "avengers_endgame.jpg", "id": 12},
                {"title": "Casino Royale", "year": "2006", "description": "James Bond takes on a terrorist financier in a high-stakes poker game.", "poster": "casino_royale.jpg", "id": 71},
                {"title": "Speed", "year": "1994", "description": "A cop must prevent a bomb on a bus from exploding.", "poster": "speed.jpg", "id": 72},
                {"title": "The Equalizer", "year": "2014", "description": "A retired operative takes on a Russian mafia.", "poster": "equalizer.jpg", "id": 73}
            ],
            "Comedy": [
                {"title": "Superbad", "year": "2007", "description": "High schoolers throw a wild party.", "poster": "superbad.jpg", "id": 13},
                {"title": "The Hangover", "year": "2009", "description": "A bachelor party goes wrong in Vegas.", "poster": "hangover.jpg", "id": 14},
                {"title": "Deadpool", "year": "2016", "description": "A mercenary with a sense of humor.", "poster": "deadpool.jpg", "id": 15},
                {"title": "Zombieland", "year": "2009", "description": "Survivors in a zombie apocalypse.", "poster": "zombieland.jpg", "id": 16},
                {"title": "Pitch Perfect", "year": "2012", "description": "A college a cappella group competes.", "poster": "pitch_perfect.jpg", "id": 17},
                {"title": "Anchorman", "year": "2004", "description": "A 1970s news anchor faces challenges.", "poster": "anchorman.jpg", "id": 18},
                {"title": "Step Brothers", "year": "2008", "description": "Two grown men become stepbrothers and cause chaos.", "poster": "step_brothers.jpg", "id": 19},
                {"title": "Mean Girls", "year": "2004", "description": "A teen navigates high school social hierarchies.", "poster": "mean_girls.jpg", "id": 20},
                {"title": "The Nice Guys", "year": "2016", "description": "A private eye and a hired enforcer team up in 1970s LA.", "poster": "nice_guys.jpg", "id": 21},
                {"title": "21 Jump Street", "year": "2012", "description": "Two cops go undercover at a high school.", "poster": "21_jump_street.jpg", "id": 22},
                {"title": "Knives Out", "year": "2019", "description": "A detective investigates a dysfunctional family's patriarch's death.", "poster": "knives_out.jpg", "id": 23},
                {"title": "Game Night", "year": "2018", "description": "A game night turns into a real mystery.", "poster": "game_night.jpg", "id": 24},
                {"title": "Crazy Rich Asians", "year": "2018", "description": "A woman discovers her boyfriend's wealthy family in Singapore.", "poster": "crazy_rich_asians.jpg", "id": 74},
                {"title": "The Grand Budapest Hotel", "year": "2014", "description": "A concierge and his lobby boy get embroiled in a caper.", "poster": "grand_budapest_hotel.jpg", "id": 75},
                {"title": "Jojo Rabbit", "year": "2019", "description": "A boy has an imaginary friend who is Adolf Hitler.", "poster": "jojo_rabbit.jpg", "id": 76}
            ],
            "Drama": [
                {"title": "The Shawshank Redemption", "year": "1994", "description": "Two prisoners find hope.", "poster": "shawshank.jpg", "id": 25},
                {"title": "Forrest Gump", "year": "1994", "description": "A man witnesses history.", "poster": "forrest_gump.jpg", "id": 26},
                {"title": "Fight Club", "year": "1999", "description": "An underground fight club spirals out of control.", "poster": "fight_club.jpg", "id": 27},
                {"title": "The Godfather", "year": "1972", "description": "A mafia family saga.", "poster": "godfather.jpg", "id": 28},
                {"title": "Schindler's List", "year": "1993", "description": "A businessman saves Jews during the Holocaust.", "poster": "schindlers_list.jpg", "id": 29},
                {"title": "The Green Mile", "year": "1999", "description": "A death row guard encounters a unique prisoner.", "poster": "green_mile.jpg", "id": 30},
                {"title": "12 Years a Slave", "year": "2013", "description": "A free man is kidnapped and sold into slavery.", "poster": "12_years_a_slave.jpg", "id": 31},
                {"title": "The Pursuit of Happyness", "year": "2006", "description": "A struggling salesman fights for a better life.", "poster": "pursuit_of_happyness.jpg", "id": 32},
                {"title": "A Beautiful Mind", "year": "2001", "description": "A mathematician struggles with schizophrenia.", "poster": "beautiful_mind.jpg", "id": 33},
                {"title": "The Wolf of Wall Street", "year": "2013", "description": "A stockbroker's rise and fall in corruption.", "poster": "wolf_of_wall_street.jpg", "id": 34},
                {"title": "Moonlight", "year": "2016", "description": "A young man grows up in a tough Miami neighborhood.", "poster": "moonlight.jpg", "id": 77},
                {"title": "Manchester by the Sea", "year": "2016", "description": "A man returns to his hometown after his brother's death.", "poster": "manchester_by_the_sea.jpg", "id": 78},
                {"title": "The Departed", "year": "2006", "description": "An undercover cop and a mole infiltrate each other's worlds.", "poster": "departed.jpg", "id": 79}
            ],
            "Science Fiction": [
                {"title": "Interstellar", "year": "2014", "description": "Explorers travel through a wormhole.", "poster": "interstellar.jpg", "id": 35},
                {"title": "The Matrix", "year": "1999", "description": "A hacker discovers reality's truth.", "poster": "matrix.jpg", "id": 36},
                {"title": "Blade Runner 2049", "year": "2017", "description": "A replicant hunter uncovers a secret.", "poster": "blade_runner_2049.jpg", "id": 37},
                {"title": "Dune", "year": "2021", "description": "A noble family controls a desert planet.", "poster": "dune.jpg", "id": 38},
                {"title": "Star Wars: The Empire Strikes Back", "year": "1980", "description": "The Rebels face the Empire's wrath.", "poster": "empire_strikes_back.jpg", "id": 39},
                {"title": "Arrival", "year": "2016", "description": "A linguist communicates with alien visitors.", "poster": "arrival.jpg", "id": 40},
                {"title": "Ex Machina", "year": "2014", "description": "A programmer tests an AI's capabilities.", "poster": "ex_machina.jpg", "id": 41},
                {"title": "2001: A Space Odyssey", "year": "1968", "description": "A journey to Jupiter with a mysterious monolith.", "poster": "2001_space_odyssey.jpg", "id": 42},
                {"title": "Annihilation", "year": "2018", "description": "A team explores a mysterious zone called The Shimmer.", "poster": "annihilation.jpg", "id": 43},
                {"title": "Her", "year": "2013", "description": "A man falls in love with an AI operating system.", "poster": "her.jpg", "id": 80},
                {"title": "Edge of Tomorrow", "year": "2014", "description": "A soldier relives the same day to fight aliens.", "poster": "edge_of_tomorrow.jpg", "id": 81},
                {"title": "The Martian", "year": "2015", "description": "An astronaut is stranded on Mars and must survive.", "poster": "martian.jpg", "id": 82}
            ],
            "Horror": [
                {"title": "The Shining", "year": "1980", "description": "A family is haunted in an isolated hotel.", "poster": "shining.jpg", "id": 44},
                {"title": "Get Out", "year": "2017", "description": "A man uncovers a dark secret at his girlfriend's family estate.", "poster": "get_out.jpg", "id": 45},
                {"title": "Hereditary", "year": "2018", "description": "A family is haunted by sinister forces after a death.", "poster": "hereditary.jpg", "id": 46},
                {"title": "It", "year": "2017", "description": "Kids face a shape-shifting entity in Derry.", "poster": "it.jpg", "id": 47},
                {"title": "The Conjuring", "year": "2013", "description": "Paranormal investigators help a family in a haunted house.", "poster": "conjuring.jpg", "id": 48},
                {"title": "A Quiet Place", "year": "2018", "description": "A family must live in silence to avoid creatures that hunt by sound.", "poster": "quiet_place.jpg", "id": 83},
                {"title": "The Witch", "year": "2015", "description": "A Puritan family encounters evil in 17th-century New England.", "poster": "witch.jpg", "id": 84},
                {"title": "Midsommar", "year": "2019", "description": "A couple visits a Swedish festival that turns sinister.", "poster": "midsommar.jpg", "id": 85}
            ],
            "Romance": [
                {"title": "The Notebook", "year": "2004", "description": "A couple's love story unfolds through a notebook.", "poster": "notebook.jpg", "id": 49},
                {"title": "La La Land", "year": "2016", "description": "A musician and an actress fall in love in LA.", "poster": "la_la_land.jpg", "id": 50},
                {"title": "Pride & Prejudice", "year": "2005", "description": "Elizabeth Bennet navigates love and societal expectations.", "poster": "pride_prejudice.jpg", "id": 51},
                {"title": "Before Sunrise", "year": "1995", "description": "Two strangers meet and connect in Vienna.", "poster": "before_sunrise.jpg", "id": 52},
                {"title": "Amélie", "year": "2001", "description": "A shy waitress changes lives in Paris with small acts of kindness.", "poster": "amelie.jpg", "id": 86},
                {"title": "Call Me by Your Name", "year": "2017", "description": "A teen experiences a summer romance in 1980s Italy.", "poster": "call_me_by_your_name.jpg", "id": 87},
                {"title": "A Star Is Born", "year": "2018", "description": "A musician helps a young singer find fame as he struggles.", "poster": "star_is_born.jpg", "id": 88}
            ],
            "Thriller": [
                {"title": "Se7en", "year": "1995", "description": "Two detectives hunt a serial killer with a twisted motive.", "poster": "se7en.jpg", "id": 53},
                {"title": "Gone Girl", "year": "2014", "description": "A man becomes a suspect in his wife's disappearance.", "poster": "gone_girl.jpg", "id": 54},
                {"title": "Shutter Island", "year": "2010", "description": "A marshal investigates a patient's disappearance on an island.", "poster": "shutter_island.jpg", "id": 55},
                {"title": "The Silence of the Lambs", "year": "1991", "description": "An FBI agent seeks help from a cannibalistic killer.", "poster": "silence_of_the_lambs.jpg", "id": 56},
                {"title": "Parasite", "year": "2019", "description": "A poor family infiltrates a wealthy household.", "poster": "parasite.jpg", "id": 57},
                {"title": "Prisoners", "year": "2013", "description": "A father takes desperate measures when his daughter goes missing.", "poster": "prisoners.jpg", "id": 89},
                {"title": "Nightcrawler", "year": "2014", "description": "A driven man becomes a crime journalist in LA.", "poster": "nightcrawler.jpg", "id": 90},
                {"title": "Zodiac", "year": "2007", "description": "Investigators hunt the Zodiac Killer in San Francisco.", "poster": "zodiac.jpg", "id": 91}
            ],
            "Adventure": [
                {"title": "Jurassic Park", "year": "1993", "description": "A theme park with cloned dinosaurs goes wrong.", "poster": "jurassic_park.jpg", "id": 58},
                {"title": "Indiana Jones: Raiders of the Lost Ark", "year": "1981", "description": "An archaeologist races to find the Ark of the Covenant.", "poster": "raiders_lost_ark.jpg", "id": 59},
                {"title": "The Lord of the Rings: The Fellowship of the Ring", "year": "2001", "description": "A hobbit embarks on a quest to destroy a powerful ring.", "poster": "lotr_fellowship.jpg", "id": 60},
                {"title": "Pirates of the Caribbean: The Curse of the Black Pearl", "year": "2003", "description": "A pirate and a blacksmith rescue a kidnapped maiden.", "poster": "pirates_caribbean.jpg", "id": 61},
                {"title": "The Revenant", "year": "2015", "description": "A frontiersman seeks survival and revenge in the wilderness.", "poster": "revenant.jpg", "id": 92},
                {"title": "Life of Pi", "year": "2012", "description": "A young man survives a shipwreck with a Bengal tiger.", "poster": "life_of_pi.jpg", "id": 93},
                {"title": "Into the Wild", "year": "2007", "description": "A young man abandons society to live in the Alaskan wilderness.", "poster": "into_the_wild.jpg", "id": 94}
            ],
            "Animation": [
                {"title": "Toy Story", "year": "1995", "description": "Toys come to life when humans aren't looking.", "poster": "toy_story.jpg", "id": 62},
                {"title": "Spirited Away", "year": "2001", "description": "A girl navigates a magical world to save her parents.", "poster": "spirited_away.jpg", "id": 63},
                {"title": "The Incredibles", "year": "2004", "description": "A family of superheroes saves the world.", "poster": "incredibles.jpg", "id": 64},
                {"title": "Coco", "year": "2017", "description": "A boy journeys to the Land of the Dead to uncover his family history.", "poster": "coco.jpg", "id": 65},
                {"title": "Inside Out", "year": "2015", "description": "Emotions guide a young girl through a life change.", "poster": "inside_out.jpg", "id": 66},
                {"title": "Finding Nemo", "year": "2003", "description": "A clownfish searches for his lost son in the ocean.", "poster": "finding_nemo.jpg", "id": 95},
                {"title": "Up", "year": "2009", "description": "An elderly man embarks on an adventure with a floating house.", "poster": "up.jpg", "id": 96},
                {"title": "WALL-E", "year": "2008", "description": "A small waste-collecting robot finds love and saves Earth.", "poster": "wall_e.jpg", "id": 97}
            ],
            "Mystery": [
                {"title": "The Sixth Sense", "year": "1999", "description": "A boy who sees dead people seeks help from a psychologist.", "poster": "sixth_sense.jpg", "id": 67},
                {"title": "Memento", "year": "2000", "description": "A man with short-term memory loss hunts his wife's killer.", "poster": "memento.jpg", "id": 68},
                {"title": "The Others", "year": "2001", "description": "A woman suspects her house is haunted.", "poster": "others.jpg", "id": 69},
                {"title": "Oldboy", "year": "2003", "description": "A man seeks answers after being imprisoned for 15 years.", "poster": "oldboy.jpg", "id": 70},
                {"title": "The Girl with the Dragon Tattoo", "year": "2011", "description": "A journalist and hacker investigate a decades-old disappearance.", "poster": "girl_with_dragon_tattoo.jpg", "id": 98},
                {"title": "Donnie Darko", "year": "2001", "description": "A troubled teen has visions of a man in a rabbit suit.", "poster": "donnie_darko.jpg", "id": 99},
                {"title": "L.A. Confidential", "year": "1997", "description": "Cops uncover corruption in 1950s Los Angeles.", "poster": "la_confidential.jpg", "id": 100}
            ]
        }
        self.save_data(self.movie_db, MOVIES_FILE)
        self.load_poster_map()

    def load_poster_map(self):
        self.poster_map = {}
        for genre, movies in self.movie_db.items():
            for movie in movies:
                poster_name = movie.get('poster', '')
                if poster_name:
                    poster_path = os.path.join(POSTER_DIR, poster_name)
                    self.poster_map[movie['title']] = poster_path if os.path.exists(poster_path) else None

    def setup_ui(self):
        self.frames = {
            "login": LoginFrame(self),
            "movies": MovieBrowserFrame(self),
            "profile": ProfileFrame(self),
            "account": AccountFrame(self),
            "movie_detail": MovieDetailFrame(self),

            "recommendations": RecommendationsFrame(self),
            "friends": FriendsFrame(self)
        }

        self.theme_btn = tk.Button(self.root, text="🌓 Toggle Theme",
                                   command=self.toggle_theme,
                                   bg=THEME["btn_bg"], fg=THEME["btn_fg"],
                                   font=("Helvetica", 14))
        self.admin_btn = tk.Button(self.root, text="🛡️ Admin",
                                   command=lambda: self.show_frame("admin"),
                                   bg=THEME["admin_btn"], fg="white",
                                   font=("Helvetica", 14))

        self.show_frame("login")

    def show_frame(self, frame_name):
        for name, frame in self.frames.items():
            if name == frame_name:
                frame.tkraise()
                frame.place(relwidth=1, relheight=1)
                if hasattr(frame, 'on_show'):
                    frame.on_show()
            else:
                frame.place_forget()
        self.update_control_buttons()

    def update_control_buttons(self):
        if self.is_admin:
            self.admin_btn.place(x=10, y=10)
            self.theme_btn.place_forget()
        elif self.current_user:
            self.theme_btn.place(x=10, y=10)
            self.admin_btn.place_forget()
        else:
            self.theme_btn.place_forget()
            self.admin_btn.place_forget()

    def toggle_theme(self):
        messagebox.showinfo("Theme", "Theme toggling will be implemented in a future version")

    def login_user(self, username, password):
        if username in self.users and self.verify_password(password, self.users[username]["password"]):
            self.current_user = username
            self.is_admin = (username == "admin")
            self.ratings.setdefault(username, {})
            self.friends.setdefault(username, {"friends": [], "requests_sent": [], "requests_received": []})
            self.show_frame("movies")
            return True
        return False

    def logout_user(self):
        self.current_user = None
        self.is_admin = False
        self.show_frame("login")

    def export_ratings(self, username):
        data = self.ratings.get(username, {})
        if not data:
            messagebox.showinfo("No Data", "No ratings to export.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if path:
            try:
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Exported", f"Ratings saved to {path}")
            except IOError as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def send_friend_request(self, from_user, to_user):
        if from_user == to_user:
            return False, "Cannot send friend request to yourself"
        if to_user not in self.users:
            return False, "User does not exist"
        if to_user in self.friends[from_user]["friends"]:
            return False, "You are already friends"
        if to_user in self.friends[from_user]["requests_sent"]:
            return False, "Friend request already sent"

        self.friends[from_user]["requests_sent"].append(to_user)
        self.friends[to_user]["requests_received"].append(from_user)
        self.save_data(self.friends, FRIENDS_FILE)
        return True, "Friend request sent successfully"

    def accept_friend_request(self, from_user, to_user):
        if from_user not in self.friends[to_user]["requests_received"]:
            return False, "No friend request from this user"

        self.friends[to_user]["requests_received"].remove(from_user)
        self.friends[from_user]["requests_sent"].remove(to_user)
        self.friends[to_user]["friends"].append(from_user)
        self.friends[from_user]["friends"].append(to_user)
        self.save_data(self.friends, FRIENDS_FILE)
        return True, "Friend request accepted"

    def reject_friend_request(self, from_user, to_user):
        if from_user not in self.friends[to_user]["requests_received"]:
            return False, "No friend request from this user"

        self.friends[to_user]["requests_received"].remove(from_user)
        self.friends[from_user]["requests_sent"].remove(to_user)
        self.save_data(self.friends, FRIENDS_FILE)
        return True, "Friend request rejected"

    def get_movie_genre(self, title):
        for genre, movies in self.movie_db.items():
            for movie in movies:
                if movie["title"] == title:
                    return genre
        return None

class LoginFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=THEME["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        center_frame = tk.Frame(self, bg=THEME["bg"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center_frame, text="🎬 MovieMate", font=("Helvetica", 28, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=30)

        form_frame = tk.Frame(center_frame, bg=THEME["bg"])
        form_frame.pack()

        tk.Label(form_frame, text="Username:", font=("Helvetica", 16),
                 bg=THEME["bg"], fg=THEME["fg"]).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = tk.Entry(form_frame, font=("Helvetica", 16),
                                       bg=THEME["entry_bg"], fg=THEME["entry_fg"], width=20)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="Password:", font=("Helvetica", 16),
                 bg=THEME["bg"], fg=THEME["fg"]).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = tk.Entry(form_frame, show="*", font=("Helvetica", 16),
                                       bg=THEME["entry_bg"], fg=THEME["entry_fg"], width=20)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        btn_frame = tk.Frame(center_frame, bg=THEME["bg"])
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Login", font=("Helvetica", 16), width=15, height=1,
                  command=self.login, bg=THEME["btn_bg"], fg=THEME["btn_fg"]).pack(side="left", padx=10, pady=10)
        tk.Button(btn_frame, text="Sign Up", font=("Helvetica", 16), width=15, height=1,
                  command=self.signup, bg=THEME["btn_bg"], fg=THEME["btn_fg"]).pack(side="left", padx=10, pady=10)

        self.place(relwidth=1, relheight=1)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return

        if self.app.login_user(username, password):
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return

        if username.lower() == "admin":
            messagebox.showerror("Error", "Cannot create admin account")
        elif username in self.app.users:
            messagebox.showerror("Error", "Username already exists")
        elif len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
        else:
            self.app.users[username] = {
                "password": self.app.hash_password(password),
                "joined": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.app.ratings[username] = {}
            self.app.friends[username] = {"friends": [], "requests_sent": [], "requests_received": []}
            if self.app.save_data(self.app.users, USERS_FILE) and self.app.save_data(self.app.ratings, RATINGS_FILE) and self.app.save_data(self.app.friends, FRIENDS_FILE):
                messagebox.showinfo("Success", "Account created successfully!")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)

class MovieBrowserFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=THEME["bg"])
        self.app = app
        self.filtered_movies = []
        self.setup_ui()

    def setup_ui(self):
        nav_frame = tk.Frame(self, bg=THEME["bg"])
        nav_frame.pack(fill="x", pady=5)

        tk.Button(nav_frame, text="❤️ Profile", command=lambda: self.app.show_frame("profile"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(side="left", padx=10)
        tk.Button(nav_frame, text="📽️ Recommendations", command=lambda: self.app.show_frame("recommendations"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(side="left", padx=10)
        tk.Button(nav_frame, text="👥 Friends", command=lambda: self.app.show_frame("friends"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(side="left", padx=10)
        tk.Button(nav_frame, text="⚙️ Account", command=lambda: self.app.show_frame("account"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(side="left")

        self.genre_var = tk.StringVar(value="All")
        self.filter_frame = tk.Frame(self, bg=THEME["bg"])
        self.filter_frame.pack(fill="x", pady=5)

        tk.Label(self.filter_frame, text="Filter by Genre:", bg=THEME["bg"], fg=THEME["fg"],
                 font=("Helvetica", 14)).pack(side="left", padx=5)

        self.genre_buttons = []
        self.update_genre_filters()

        self.canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grid_frame = tk.Frame(self.canvas, bg=THEME["bg"])
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.place(relwidth=1, relheight=1)
        self.apply_filter()

    def update_genre_filters(self):
        for btn in self.genre_buttons:
            btn.destroy()
        self.genre_buttons = []

        genres = ["All"] + sorted(self.app.movie_db.keys())
        current_genre = self.genre_var.get()
        if current_genre not in genres:
            self.genre_var.set("All")

        for genre in genres:
            btn = tk.Radiobutton(self.filter_frame, text=genre, variable=self.genre_var,
                                 value=genre, command=self.apply_filter,
                                 bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 12))
            btn.pack(side="left", padx=5)
            self.genre_buttons.append(btn)

    def apply_filter(self):
        genre = self.genre_var.get()
        if genre == "All":
            self.filtered_movies = [m for genre_movies in self.app.movie_db.values() for m in genre_movies]
        else:
            self.filtered_movies = self.app.movie_db.get(genre, [])

        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.display_movies()

    def display_movies(self):
        if not self.filtered_movies:
            tk.Label(self.grid_frame, text=f"No movies found in {self.genre_var.get() if self.genre_var.get() != 'All' else 'database'}",
                     bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14)).pack(pady=50)
            return

        columns = 5
        for i, movie in enumerate(self.filtered_movies):
            row = i // columns
            col = i % columns
            card = self.create_movie_card(movie)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.grid_frame.grid_columnconfigure(col, weight=1)

    def create_movie_card(self, movie):
        card = tk.Frame(self.grid_frame, width=200, height=280, bg=THEME["card_bg"], bd=2, relief="groove")
        card.grid_propagate(False)

        card.bind("<Button-1>", lambda e: self.show_movie_detail(movie["title"]))

        poster_path = self.app.poster_map.get(movie["title"])
        poster_label = tk.Label(card, bg=THEME["card_bg"])
        if poster_path and os.path.exists(poster_path):
            try:
                img = Image.open(poster_path)
                img = img.resize((120, 160), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                poster_label.config(image=img)
                poster_label.image = img
            except Exception as e:
                print(f"Error loading poster: {e}")
                poster_label.config(text="No Image", height=8, bg=THEME["card_bg"], fg=THEME["card_fg"], font=("Helvetica", 10))
        else:
            poster_label.config(text="Poster not available", height=8, bg=THEME["card_bg"], fg=THEME["card_fg"], font=("Helvetica", 10))
        poster_label.pack()

        tk.Label(card, text=movie["title"], wraplength=160, font=("Helvetica", 11, "bold"),
                 bg=THEME["card_bg"], fg=THEME["card_fg"]).pack(pady=(5, 0))
        tk.Label(card, text=f"({movie.get('year', 'N/A')})", font=("Helvetica", 9),
                 bg=THEME["card_bg"], fg=THEME["card_fg"]).pack()

        self.add_rating_controls(card, movie["title"])
        return card

    def add_rating_controls(self, card, title):
        btn_frame = tk.Frame(card, bg=THEME["card_bg"])
        btn_frame.pack(pady=5)

        user_rating = self.app.ratings.get(self.app.current_user, {}).get(title)
        if user_rating is not None:
            rating_text = "👍" if user_rating == 1 else "👎"
            tk.Label(btn_frame, text=rating_text, font=("Helvetica", 12),
                     bg=THEME["card_bg"], fg=THEME["card_fg"]).pack()
        else:
            tk.Button(btn_frame, text="👍", width=3, command=lambda: self.rate_movie(title, 1),
                      bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 10)).pack(side="left", padx=2)
            tk.Button(btn_frame, text="👎", width=3, command=lambda: self.rate_movie(title, 0),
                      bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 10)).pack(side="left", padx=2)

    def show_movie_detail(self, movie_title):
        self.app.frames["movie_detail"].load_movie(movie_title)
        self.app.show_frame("movie_detail")

    def rate_movie(self, title, rating):
        self.app.ratings[self.app.current_user][title] = rating
        if self.app.save_data(self.app.ratings, RATINGS_FILE):
            for widget in self.grid_frame.winfo_children():
                widget.destroy()
            self.display_movies()

    def on_show(self):
        self.update_genre_filters()
        self.apply_filter()

class ProfileFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=THEME["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="❤️ Your Ratings", font=("Helvetica", 18, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
        tk.Button(self, text="🔙 Back", command=lambda: self.app.show_frame("movies"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(anchor="nw", padx=10, pady=10)

        self.canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.ratings_frame = tk.Frame(self.canvas, bg=THEME["bg"])
        self.canvas.create_window((0, 0), window=self.ratings_frame, anchor="nw")

        self.ratings_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.place(relwidth=1, relheight=1)

    def load_ratings(self):
        for widget in self.ratings_frame.winfo_children():
            widget.destroy()

        user_ratings = self.app.ratings.get(self.app.current_user, {})
        if not user_ratings:
            tk.Label(self.ratings_frame, text="You haven't rated any movies yet.",
                     bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14)).pack(pady=20)
            return

        sorted_ratings = sorted(user_ratings.items(), key=lambda x: (-x[1], x[0]))
        for movie, rating in sorted_ratings:
            rating_frame = tk.Frame(self.ratings_frame, bg=THEME["card_bg"], bd=1, relief="groove")
            rating_frame.pack(fill="x", pady=2, padx=10)

            rating_icon = "👍" if rating == 1 else "👎"
            tk.Label(rating_frame, text=rating_icon, font=("Helvetica", 14),
                     bg=THEME["card_bg"], fg=THEME["card_fg"]).pack(side="left", padx=5)

            movie_label = tk.Label(rating_frame, text=movie, font=("Helvetica", 14),
                                   bg=THEME["card_bg"], fg=THEME["highlight"], cursor="hand2")
            movie_label.pack(side="left", padx=5)
            movie_label.bind("<Button-1>", lambda e, m=movie: self.show_movie_detail(m))

            movie_year = self.get_movie_year(movie)
            if movie_year:
                tk.Label(rating_frame, text=f"({movie_year})", bg=THEME["card_bg"], fg=THEME["card_fg"],
                         font=("Helvetica", 14)).pack(side="left", padx=5)

    def get_movie_year(self, title):
        for genre in self.app.movie_db.values():
            for movie in genre:
                if movie["title"] == title:
                    return movie.get("year", "")
        return ""

    def show_movie_detail(self, movie_title):
        self.app.frames["movie_detail"].load_movie(movie_title)
        self.app.show_frame("movie_detail")

    def on_show(self):
        self.load_ratings()

class RecommendationsFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=THEME["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="📽️ Recommended Movies", font=("Helvetica", 18, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
        tk.Button(self, text="🔙 Back", command=lambda: self.app.show_frame("movies"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(anchor="nw", padx=10, pady=10)

        self.canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grid_frame = tk.Frame(self.canvas, bg=THEME["bg"])
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.place(relwidth=1, relheight=1)

    def get_recommendations(self):
        user_ratings = self.app.ratings.get(self.app.current_user, {})
        if not user_ratings:
            return []

        liked_genres = defaultdict(int)
        for movie_title, rating in user_ratings.items():
            if rating == 1:  # Liked
                genre = self.app.get_movie_genre(movie_title)
                if genre:
                    liked_genres[genre] += 1

        if not liked_genres:
            return []

        sorted_genres = sorted(liked_genres.items(), key=lambda x: x[1], reverse=True)

        recommended_movies = []
        for genre, _ in sorted_genres:
            for movie in self.app.movie_db.get(genre, []):
                if movie["title"] not in user_ratings:
                    recommended_movies.append(movie)
                if len(recommended_movies) >= 10:
                    break
            if len(recommended_movies) >= 10:
                break

        return recommended_movies

    def display_recommendations(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        recommended_movies = self.get_recommendations()
        if not recommended_movies:
            tk.Label(self.grid_frame, text="No recommendations available. Rate some movies to get started!",
                     bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14)).pack(pady=50)
            return

        columns = 5
        for i, movie in enumerate(recommended_movies):
            row = i // columns
            col = i % columns
            card = self.create_movie_card(movie)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.grid_frame.grid_columnconfigure(col, weight=1)

    def create_movie_card(self, movie):
        card = tk.Frame(self.grid_frame, width=200, height=280, bg=THEME["card_bg"], bd=2, relief="groove")
        card.grid_propagate(False)

        card.bind("<Button-1>", lambda e: self.show_movie_detail(movie["title"]))

        poster_path = self.app.poster_map.get(movie["title"])
        poster_label = tk.Label(card, bg=THEME["card_bg"])
        if poster_path and os.path.exists(poster_path):
            try:
                img = Image.open(poster_path)
                img = img.resize((120, 160), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                poster_label.config(image=img)
                poster_label.image = img
            except Exception as e:
                print(f"Error loading poster: {e}")
                poster_label.config(text="No Image", height=8, bg=THEME["card_bg"], fg=THEME["card_fg"], font=("Helvetica", 10))
        else:
            poster_label.config(text="Poster not available", height=8, bg=THEME["card_bg"], fg=THEME["card_fg"], font=("Helvetica", 10))
        poster_label.pack()

        tk.Label(card, text=movie["title"], wraplength=160, font=("Helvetica", 11, "bold"),
                 bg=THEME["card_bg"], fg=THEME["card_fg"]).pack(pady=(5, 0))
        tk.Label(card, text=f"({movie.get('year', 'N/A')})", font=("Helvetica", 9),
                 bg=THEME["card_bg"], fg=THEME["card_fg"]).pack()

        self.add_rating_controls(card, movie["title"])
        return card

    def add_rating_controls(self, card, title):
        btn_frame = tk.Frame(card, bg=THEME["card_bg"])
        btn_frame.pack(pady=5)

        user_rating = self.app.ratings.get(self.app.current_user, {}).get(title)
        if user_rating is not None:
            rating_text = "👍" if user_rating == 1 else "👎"
            tk.Label(btn_frame, text=rating_text, font=("Helvetica", 12),
                     bg=THEME["card_bg"], fg=THEME["card_fg"]).pack()
        else:
            tk.Button(btn_frame, text="👍", width=3, command=lambda: self.rate_movie(title, 1),
                      bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 10)).pack(side="left", padx=2)
            tk.Button(btn_frame, text="👎", width=3, command=lambda: self.rate_movie(title, 0),
                      bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 10)).pack(side="left", padx=2)

    def show_movie_detail(self, movie_title):
        self.app.frames["movie_detail"].load_movie(movie_title)
        self.app.show_frame("movie_detail")

    def rate_movie(self, title, rating):
        self.app.ratings[self.app.current_user][title] = rating
        if self.app.save_data(self.app.ratings, RATINGS_FILE):
            self.display_recommendations()

    def on_show(self):
        self.display_recommendations()

class FriendsFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=THEME["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="👥 Friends", font=("Helvetica", 18, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
        tk.Button(self, text="🔙 Back", command=lambda: self.app.show_frame("movies"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(anchor="nw", padx=10, pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.friends_tab = tk.Frame(self.notebook, bg=THEME["bg"])
        self.requests_tab = tk.Frame(self.notebook, bg=THEME["bg"])
        self.suggestions_tab = tk.Frame(self.notebook, bg=THEME["bg"])

        self.notebook.add(self.friends_tab, text="My Friends")
        self.notebook.add(self.requests_tab, text="Requests")
        self.notebook.add(self.suggestions_tab, text="Suggestions")

        self.setup_friends_tab()
        self.setup_requests_tab()
        self.setup_suggestions_tab()

        style = ttk.Style()
        style.configure("TNotebook", background=THEME["bg"])
        style.configure("TNotebook.Tab", background=THEME["btn_bg"], foreground=THEME["btn_fg"],
                        padding=[10, 5], font=("Helvetica", 14))
        style.map("TNotebook.Tab", background=[("selected", THEME["highlight"])],
                  foreground=[("selected", "black")])

        self.place(relwidth=1, relheight=1)

    def setup_friends_tab(self):
        self.friends_canvas = tk.Canvas(self.friends_tab, bg=THEME["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.friends_tab, orient="vertical", command=self.friends_canvas.yview)
        self.friends_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.friends_canvas.pack(side="left", fill="both", expand=True)

        self.friends_frame = tk.Frame(self.friends_canvas, bg=THEME["bg"])
        self.friends_canvas.create_window((0, 0), window=self.friends_frame, anchor="nw")

        self.friends_frame.bind("<Configure>", lambda e: self.friends_canvas.configure(scrollregion=self.friends_canvas.bbox("all")))

    def setup_requests_tab(self):
        tk.Label(self.requests_tab, text="Incoming Requests", font=("Helvetica", 16, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=5)

        self.incoming_frame = tk.Frame(self.requests_tab, bg=THEME["bg"])
        self.incoming_frame.pack(fill="x", padx=10)

        tk.Label(self.requests_tab, text="Sent Requests", font=("Helvetica", 16, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=5)

        self.sent_frame = tk.Frame(self.requests_tab, bg=THEME["bg"])
        self.sent_frame.pack(fill="x", padx=10)

    def setup_suggestions_tab(self):
        tk.Label(self.suggestions_tab, text="Users with Similar Interests", font=("Helvetica", 16, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=5)

        self.suggestions_frame = tk.Frame(self.suggestions_tab, bg=THEME["bg"])
        self.suggestions_frame.pack(fill="x", padx=10)

    def load_friends(self):
        for widget in self.friends_frame.winfo_children():
            widget.destroy()

        friends = self.app.friends.get(self.app.current_user, {}).get("friends", [])
        if not friends:
            tk.Label(self.friends_frame, text="No friends yet.", bg=THEME["bg"], fg=THEME["fg"],
                     font=("Helvetica", 14)).pack(pady=20)
        else:
            for friend in sorted(friends):
                friend_frame = tk.Frame(self.friends_frame, bg=THEME["card_bg"], bd=1, relief="groove")
                friend_frame.pack(fill="x", pady=2, padx=10)

                friend_label = tk.Label(friend_frame, text=friend, font=("Helvetica", 14),
                                        bg=THEME["card_bg"], fg=THEME["highlight"], cursor="hand2")
                friend_label.pack(side="left", padx=10, pady=5)
                friend_label.bind("<Button-1>", lambda e, f=friend: self.show_friend_profile(f))

                tk.Button(friend_frame, text="Remove", command=lambda f=friend: self.remove_friend(f),
                          bg="#FF0000", fg="white", font=("Helvetica", 12)).pack(side="right", padx=10)

    def show_friend_profile(self, friend):
        dialog = tk.Toplevel(self)
        dialog.title(f"{friend}'s Profile")
        dialog.geometry("600x400")
        dialog.configure(bg=THEME["bg"])
        dialog.resizable(False, False)

        tk.Label(dialog, text=f"👤 {friend}", font=("Helvetica", 18, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)

        user_data = self.app.users.get(friend, {})
        friends = self.app.friends.get(friend, {}).get("friends", [])
        tk.Label(dialog, text=f"Joined: {user_data.get('joined', 'N/A')}", font=("Helvetica", 14),
                 bg=THEME["bg"], fg=THEME["fg"]).pack()
        tk.Label(dialog, text=f"Friends: {len(friends)}", font=("Helvetica", 14),
                 bg=THEME["bg"], fg=THEME["fg"]).pack()

        tk.Label(dialog, text="Liked Movies:", font=("Helvetica", 16, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)

        canvas = tk.Canvas(dialog, bg=THEME["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=10)

        ratings_frame = tk.Frame(canvas, bg=THEME["bg"])
        canvas.create_window((0, 0), window=ratings_frame, anchor="nw")
        ratings_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        user_ratings = self.app.ratings.get(friend, {})
        liked_movies = [(movie, year) for movie, rating in user_ratings.items() if rating == 1
                        for genre in self.app.movie_db.values() for m in genre if m["title"] == movie and (year := m.get("year", ""))]
        if not liked_movies:
            tk.Label(ratings_frame, text="No liked movies yet.", bg=THEME["bg"], fg=THEME["fg"],
                     font=("Helvetica", 14)).pack(pady=20)
        else:
            for movie, year in sorted(liked_movies):
                movie_frame = tk.Frame(ratings_frame, bg=THEME["card_bg"], bd=1, relief="groove")
                movie_frame.pack(fill="x", pady=2, padx=10)

                movie_label = tk.Label(movie_frame, text=movie, font=("Helvetica", 14),
                                       bg=THEME["card_bg"], fg=THEME["highlight"], cursor="hand2")
                movie_label.pack(side="left", padx=5)
                movie_label.bind("<Button-1>", lambda e, m=movie: self.show_movie_detail(m))

                tk.Label(movie_frame, text=f"({year})", font=("Helvetica", 14),
                         bg=THEME["card_bg"], fg=THEME["card_fg"]).pack(side="left", padx=5)

        tk.Button(dialog, text="Close", command=dialog.destroy,
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(pady=10)

    def remove_friend(self, friend):
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove {friend} as a friend?"):
            self.app.friends[self.app.current_user]["friends"].remove(friend)
            self.app.friends[friend]["friends"].remove(self.app.current_user)
            self.app.save_data(self.app.friends, FRIENDS_FILE)
            self.load_friends()
            self.load_suggestions()

    def show_movie_detail(self, movie_title):
        self.app.frames["movie_detail"].load_movie(movie_title)
        self.app.show_frame("movie_detail")

    def load_requests(self):
        for widget in self.incoming_frame.winfo_children():
            widget.destroy()
        for widget in self.sent_frame.winfo_children():
            widget.destroy()

        incoming = self.app.friends.get(self.app.current_user, {}).get("requests_received", [])
        if not incoming:
            tk.Label(self.incoming_frame, text="No incoming requests.", bg=THEME["bg"], fg=THEME["fg"],
                     font=("Helvetica", 14)).pack(pady=5)
        else:
            for user in incoming:
                frame = tk.Frame(self.incoming_frame, bg=THEME["bg"])
                frame.pack(fill="x", pady=2)
                tk.Label(frame, text=user, bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14)).pack(side="left", padx=5)
                tk.Button(frame, text="Accept", command=lambda u=user: self.accept_request(u),
                          bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(side="left", padx=5)
                tk.Button(frame, text="Reject", command=lambda u=user: self.reject_request(u),
                          bg="#FF0000", fg="white", font=("Helvetica", 12)).pack(side="left", padx=5)

        sent = self.app.friends.get(self.app.current_user, {}).get("requests_sent", [])
        if not sent:
            tk.Label(self.sent_frame, text="No sent requests.", bg=THEME["bg"], fg=THEME["fg"],
                     font=("Helvetica", 14)).pack(pady=5)
        else:
            for user in sent:
                tk.Label(self.sent_frame, text=f"Pending: {user}", bg=THEME["bg"], fg=THEME["fg"],
                         font=("Helvetica", 14)).pack(anchor="w", padx=5, pady=2)

    def load_suggestions(self):
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()

        user_ratings = self.app.ratings.get(self.app.current_user, {})
        if not user_ratings:
            tk.Label(self.suggestions_frame, text="Rate some movies to get friend suggestions!",
                     bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14)).pack(pady=5)
            return

        liked_movies = set(movie for movie, rating in user_ratings.items() if rating == 1)
        if not liked_movies:
            tk.Label(self.suggestions_frame, text="Like some movies to get friend suggestions!",
                     bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14)).pack(pady=5)
            return

        similar_users = []
        for other_user in self.app.users.keys():
            if other_user == self.app.current_user or other_user == "admin":
                continue
            if other_user in self.app.friends[self.app.current_user]["friends"]:
                continue
            if other_user in self.app.friends[self.app.current_user]["requests_sent"]:
                continue

            other_ratings = self.app.ratings.get(other_user, {})
            other_liked = set(movie for movie, rating in other_ratings.items() if rating == 1)
            common_likes = liked_movies & other_liked
            if common_likes:
                similarity = len(common_likes)
                similar_users.append((other_user, similarity, common_likes))

        similar_users.sort(key=lambda x: x[1], reverse=True)
        if not similar_users:
            tk.Label(self.suggestions_frame, text="No users with similar interests found.",
                     bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14)).pack(pady=5)
            return

        for user, similarity, common in similar_users[:5]:
            frame = tk.Frame(self.suggestions_frame, bg=THEME["bg"])
            frame.pack(fill="x", pady=2)
            tk.Label(frame, text=f"{user} (Common Likes: {similarity})", bg=THEME["bg"], fg=THEME["fg"],
                     font=("Helvetica", 14)).pack(side="left", padx=5)
            tk.Button(frame, text="Add Friend", command=lambda u=user: self.send_request(u),
                      bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(side="left", padx=5)

    def send_request(self, to_user):
        success, message = self.app.send_friend_request(self.app.current_user, to_user)
        messagebox.showinfo("Result", message)
        if success:
            self.load_requests()
            self.load_suggestions()

    def accept_request(self, from_user):
        success, message = self.app.accept_friend_request(from_user, self.app.current_user)
        messagebox.showinfo("Result", message)
        if success:
            self.load_friends()
            self.load_requests()
            self.load_suggestions()

    def reject_request(self, from_user):
        success, message = self.app.reject_friend_request(from_user, self.app.current_user)
        messagebox.showinfo("Result", message)
        if success:
            self.load_requests()
            self.load_suggestions()

    def on_show(self):
        self.load_friends()
        self.load_requests()
        self.load_suggestions()

class AccountFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=THEME["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="⚙️ Account Settings", font=("Helvetica", 18, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
        tk.Button(self, text="🔙 Back", command=lambda: self.app.show_frame("movies"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(anchor="nw", padx=10, pady=10)

        self.info_label = tk.Label(self, font=("Helvetica", 14), bg=THEME["bg"], fg=THEME["fg"])
        self.info_label.pack(pady=10)

        self.stats_label = tk.Label(self, font=("Helvetica", 14), bg=THEME["bg"], fg=THEME["fg"])
        self.stats_label.pack(pady=5)

        btn_frame = tk.Frame(self, bg=THEME["bg"])
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="🔑 Change Password", command=self.change_password,
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(pady=5)
        tk.Button(btn_frame, text="📤 Export Ratings", command=self.export_ratings,
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(pady=5)
        tk.Button(btn_frame, text="🚪 Logout", command=self.app.logout_user,
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(pady=5)

        self.place(relwidth=1, relheight=1)

    def update_info(self):
        if not self.app.current_user:
            return

        user_data = self.app.users[self.app.current_user]
        ratings = self.app.ratings.get(self.app.current_user, {})
        friends = self.app.friends.get(self.app.current_user, {}).get("friends", [])
        self.info_label.config(text=f"👤 {self.app.current_user}\nJoined: {user_data['joined']}\nFriends: {len(friends)}")

        liked = sum(1 for r in ratings.values() if r == 1)
        disliked = sum(1 for r in ratings.values() if r == 0)
        self.stats_label.config(text=f"🎞️ Rated: {len(ratings)}\n👍 Liked: {liked}\n👎 Disliked: {disliked}")

    def change_password(self):
        dialog = tk.Toplevel(self)
        dialog.title("Change Password")
        dialog.resizable(False, False)
        dialog.configure(bg=THEME["bg"])

        tk.Label(dialog, text="Current Password:", bg=THEME["bg"], fg=THEME["fg"],
                 font=("Helvetica", 14)).pack(pady=5)
        current_pw = tk.Entry(dialog, show="*", bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                              font=("Helvetica", 14))
        current_pw.pack(pady=5)

        tk.Label(dialog, text="New Password:", bg=THEME["bg"], fg=THEME["fg"],
                 font=("Helvetica", 14)).pack(pady=5)
        new_pw = tk.Entry(dialog, show="*", bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                          font=("Helvetica", 14))
        new_pw.pack(pady=5)

        def submit():
            current = current_pw.get()
            new = new_pw.get()

            if not self.app.verify_password(current, self.app.users[self.app.current_user]["password"]):
                messagebox.showerror("Error", "Incorrect current password")
            elif not new:
                messagebox.showerror("Error", "New password cannot be empty")
            elif len(new) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters")
            else:
                self.app.users[self.app.current_user]["password"] = self.app.hash_password(new)
                if self.app.save_data(self.app.users, USERS_FILE):
                    dialog.destroy()
                    messagebox.showinfo("Success", "Password changed successfully")

        tk.Button(dialog, text="Submit", command=submit,
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(pady=10)

    def export_ratings(self):
        self.app.export_ratings(self.app.current_user)

    def on_show(self):
        self.update_info()

class MovieDetailFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg=THEME["bg"])
        self.app = app
        self.current_movie = None
        self.current_genre = None
        self.setup_ui()

    def setup_ui(self):
        tk.Button(self, text="🔙 Back to Movies", command=lambda: self.app.show_frame("movies"),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 14)).pack(anchor="nw", padx=10, pady=10)

        content_frame = tk.Frame(self, bg=THEME["bg"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        poster_frame = tk.Frame(content_frame, bg=THEME["bg"])
        poster_frame.pack(side="left", padx=20)

        self.poster_label = tk.Label(poster_frame, bg=THEME["bg"])
        self.poster_label.pack()

        details_frame = tk.Frame(content_frame, bg=THEME["bg"])
        details_frame.pack(side="left", fill="both", expand=True)

        self.title_label = tk.Label(details_frame, font=("Helvetica", 22, "bold"),
                                    bg=THEME["bg"], fg=THEME["fg"])
        self.title_label.pack(anchor="w", pady=(0, 10))

        self.year_label = tk.Label(details_frame, font=("Helvetica", 14),
                                   bg=THEME["bg"], fg=THEME["fg"])
        self.year_label.pack(anchor="w", pady=(0, 10))

        self.genre_label = tk.Label(details_frame, font=("Helvetica", 14),
                                    bg=THEME["bg"], fg=THEME["fg"])
        self.genre_label.pack(anchor="w", pady=(0, 20))

        tk.Label(details_frame, text="Description:", font=("Helvetica", 14, "bold"),
                 bg=THEME["bg"], fg=THEME["fg"]).pack(anchor="w")

        self.desc_label = tk.Label(details_frame, wraplength=500, justify="left",
                                   bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14))
        self.desc_label.pack(anchor="w", pady=(0, 20))

        rating_frame = tk.Frame(details_frame, bg=THEME["bg"])
        rating_frame.pack(anchor="w", pady=20)

        tk.Label(rating_frame, text="Your Rating:", bg=THEME["bg"], fg=THEME["fg"],
                 font=("Helvetica", 14)).grid(row=0, column=0, sticky="w")

        self.rating_status = tk.Label(rating_frame, bg=THEME["bg"], fg=THEME["fg"],
                                      font=("Helvetica", 14))
        self.rating_status.grid(row=0, column=1, padx=10)

        btn_frame = tk.Frame(rating_frame, bg=THEME["bg"])
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Button(btn_frame, text="👍 Like", width=8, command=lambda: self.rate_movie(1),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="👎 Dislike", width=8, command=lambda: self.rate_movie(0),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ Remove", width=8, command=lambda: self.rate_movie(None),
                  bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(side="left", padx=5)

        self.place(relwidth=1, relheight=1)

    def load_movie(self, title):
        self.current_movie = None
        self.current_genre = None

        for genre, movies in self.app.movie_db.items():
            for movie in movies:
                if movie["title"] == title:
                    self.current_movie = movie
                    self.current_genre = genre
                    break
            if self.current_movie:
                break

        if not self.current_movie:
            messagebox.showerror("Error", "Movie not found")
            self.app.show_frame("movies")
            return

        self.title_label.config(text=self.current_movie["title"])
        self.year_label.config(text=f"Year: {self.current_movie.get('year', 'N/A')}")
        self.genre_label.config(text=f"Genre: {self.current_genre}")
        self.desc_label.config(text=self.current_movie.get("description", "No description available"))

        poster_path = self.app.poster_map.get(title)
        if poster_path and os.path.exists(poster_path):
            try:
                img = Image.open(poster_path).resize((250, 375), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                self.poster_label.config(image=img)
                self.poster_label.image = img
            except Exception as e:
                print(f"Error loading poster: {e}")
                self.poster_label.config(text="Poster not available", height=15, width=25,
                                         bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14))
        else:
            self.poster_label.config(text="Poster not available", height=15, width=25,
                                     bg=THEME["bg"], fg=THEME["fg"], font=("Helvetica", 14))

        self.update_rating_display()

    def update_rating_display(self):
        if not self.current_movie or not self.app.current_user:
            return

        rating = self.app.ratings.get(self.app.current_user, {}).get(self.current_movie["title"])
        if rating is not None:
            status = "👍 Liked" if rating == 1 else "👎 Disliked"
            self.rating_status.config(text=status)
        else:
            self.rating_status.config(text="Not rated yet")

    def rate_movie(self, rating):
        if not self.current_movie or not self.app.current_user:
            return

        title = self.current_movie["title"]
        if rating is None:
            if title in self.app.ratings[self.app.current_user]:
                del self.app.ratings[self.app.current_user][title]
        else:
            self.app.ratings[self.app.current_user][title] = rating

        if self.app.save_data(self.app.ratings, RATINGS_FILE):
            self.update_rating_display()
def setup_movies_tab(self):
    list_frame = tk.Frame(self.movies_tab, bg=THEME["bg"])
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    self.movie_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                 bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                                 selectbackground=THEME["highlight"], font=("Helvetica", 14))
    self.movie_list.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=self.movie_list.yview)

    controls_frame = tk.Frame(self.movies_tab, bg=THEME["bg"])
    controls_frame.pack(fill="x", padx=10, pady=5)

    add_frame = tk.Frame(controls_frame, bg=THEME["bg"])
    add_frame.pack(side="left", padx=10)

    tk.Label(add_frame, text="Add New Movie:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 14)).pack(anchor="w")

    form_frame = tk.Frame(add_frame, bg=THEME["bg"])
    form_frame.pack(fill="x", pady=5)

    tk.Label(form_frame, text="Title:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    self.title_entry = tk.Entry(form_frame, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                                font=("Helvetica", 12))
    self.title_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Year:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    self.year_entry = tk.Entry(form_frame, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                               font=("Helvetica", 12))
    self.year_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Genre:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    self.genre_combobox = ttk.Combobox(form_frame, values=sorted(self.app.movie_db.keys()),
                                       font=("Helvetica", 12), state="readonly")
    self.genre_combobox.grid(row=2, column=1, padx=5, pady=5)
    self.genre_combobox.set("Action")  # Default genre

    tk.Label(form_frame, text="Description:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    self.desc_entry = tk.Entry(form_frame, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                               font=("Helvetica", 12))
    self.desc_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Poster:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).grid(row=4, column=0, sticky="e", padx=5, pady=5)
    self.poster_button = tk.Button(form_frame, text="Choose File", command=self.choose_poster,
                                   bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12))
    self.poster_button.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    tk.Button(add_frame, text="Add Movie", command=self.add_movie,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(pady=10)

    action_frame = tk.Frame(controls_frame, bg=THEME["bg"])
    action_frame.pack(side="left", padx=10)

    tk.Label(action_frame, text="Manage Selected Movie:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 14)).pack(anchor="w")
    tk.Button(action_frame, text="Edit", command=self.edit_movie,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(pady=5)
    tk.Button(action_frame, text="Delete", command=self.delete_movie,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(pady=5)

    self.movie_list.bind("<<ListboxSelect>>", self.on_movie_select)
    self.selected_movie = None
    self.poster_path = None

def setup_users_tab(self):
    list_frame = tk.Frame(self.users_tab, bg=THEME["bg"])
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    self.user_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                                selectbackground=THEME["highlight"], font=("Helvetica", 14))
    self.user_list.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=self.user_list.yview)

    controls_frame = tk.Frame(self.users_tab, bg=THEME["bg"])
    controls_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(controls_frame, text="Manage Users:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 14)).pack(anchor="w")
    tk.Button(controls_frame, text="View Details", command=self.view_user_details,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(anchor="w", pady=5)
    tk.Button(controls_frame, text="Delete User", command=self.delete_user,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(anchor="w", pady=5)

    self.user_list.bind("<<ListboxSelect>>", self.on_user_select)
    self.selected_user = None

def on_show(self):
    if not self.app.is_admin:
        messagebox.showerror("Access Denied", "Only admin can access this page")
        self.app.show_frame("movies")
        return
    self.load_movies()
    self.load_users()

def load_movies(self):
    self.movie_list.delete(0, tk.END)
    for genre, movies in sorted(self.app.movie_db.items()):
        for movie in sorted(movies, key=lambda x: x["title"]):
            self.movie_list.insert(tk.END, f"{movie['title']} ({movie['year']}) - {genre}")

def load_users(self):
    self.user_list.delete(0, tk.END)
    for user in sorted(self.app.users.keys()):
        if user != "admin":  # Exclude admin from list
            self.user_list.insert(tk.END, user)

def on_movie_select(self, event):
    selection = self.movie_list.curselection()
    if selection:
        index = selection[0]
        movie_str = self.movie_list.get(index)
        # Extract title from string like "Title (Year) - Genre"
        title = movie_str.split(" (")[0]
        self.selected_movie = None
        for genre, movies in self.app.movie_db.items():
            for movie in movies:
                if movie["title"] == title:
                    self.selected_movie = (movie, genre)
                    break
            if self.selected_movie:
                break
    else:
        self.selected_movie = None

def on_user_select(self, event):
    selection = self.user_list.curselection()
    if selection:
        self.selected_user = self.user_list.get(selection[0])
    else:
        self.selected_user = None

def choose_poster(self):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg"), ("All files", "*.*")])
    if file_path:
        self.poster_path = file_path
        self.poster_button.config(text="File Selected")

def add_movie(self):
    title = self.title_entry.get().strip()
    year = self.year_entry.get().strip()
    genre = self.genre_combobox.get()
    description = self.desc_entry.get().strip()
    poster = self.poster_path

    if not title or not year or not genre or not description:
        messagebox.showerror("Error", "All fields except poster are required")
        return

    if not year.isdigit() or len(year) != 4:
        messagebox.showerror("Error", "Year must be a 4-digit number")
        return

    # Check if movie already exists
    for g, movies in self.app.movie_db.items():
        for m in movies:
            if m["title"].lower() == title.lower():
                messagebox.showerror("Error", "Movie already exists")
                return

    # Generate unique movie ID
    max_id = 0
    for movies in self.app.movie_db.values():
        for m in movies:
            max_id = max(max_id, m["id"])
    new_id = max_id + 1

    # Handle poster
    poster_name = ""
    if poster:
        import shutil
        poster_name = f"{title.replace(' ', '_').lower()}_{new_id}.jpg"
        poster_dest = os.path.join(POSTER_DIR, poster_name)
        try:
            shutil.copy(poster, poster_dest)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save poster: {str(e)}")
            return

    # Add movie to database
    new_movie = {
        "title": title,
        "year": year,
        "description": description,
        "poster": poster_name,
        "id": new_id
    }
    self.app.movie_db[genre].append(new_movie)
    self.app.poster_map[title] = os.path.join(POSTER_DIR, poster_name) if poster_name else None

    if self.app.save_data(self.app.movie_db, MOVIES_FILE):
        messagebox.showinfo("Success", "Movie added successfully")
        self.title_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.poster_button.config(text="Choose File")
        self.poster_path = None
        self.load_movies()

def edit_movie(self):
    if not self.selected_movie:
        messagebox.showerror("Error", "Please select a movie to edit")
        return

    movie, genre = self.selected_movie

    dialog = tk.Toplevel(self)
    dialog.title("Edit Movie")
    dialog.resizable(False, False)
    dialog.configure(bg=THEME["bg"])

    tk.Label(dialog, text="Title:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).pack(pady=5)
    title_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                           font=("Helvetica", 12))
    title_entry.pack(pady=5)
    title_entry.insert(0, movie["title"])

    tk.Label(dialog, text="Year:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).pack(pady=5)
    year_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                          font=("Helvetica", 12))
    year_entry.pack(pady=5)
    year_entry.insert(0, movie["year"])

    tk.Label(dialog, text="Genre:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).pack(pady=5)
    genre_combobox = ttk.Combobox(dialog, values=sorted(self.app.movie_db.keys()),
                                  font=("Helvetica", 12), state="readonly")
    genre_combobox.pack(pady=5)
    genre_combobox.set(genre)

    tk.Label(dialog, text="Description:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).pack(pady=5)
    desc_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["entry_fg"],
                          font=("Helvetica", 12))
    desc_entry.pack(pady=5)
    desc_entry.insert(0, movie["description"])

    tk.Label(dialog, text="Poster:", bg=THEME["bg"], fg=THEME["fg"],
             font=("Helvetica", 12)).pack(pady=5)
    poster_button = tk.Button(dialog, text="Choose File" if not movie["poster"] else "Replace File",
                             command=lambda: self.choose_poster_edit(poster_button),
                             bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12))
    poster_button.pack(pady=5)

    def submit():
        new_title = title_entry.get().strip()
        new_year = year_entry.get().strip()
        new_genre = genre_combobox.get()
        new_desc = desc_entry.get().strip()
        new_poster = self.poster_path

        if not new_title or not new_year or not new_genre or not new_desc:
            messagebox.showerror("Error", "All fields except poster are required")
            return

        if not new_year.isdigit() or len(new_year) != 4:
            messagebox.showerror("Error", "Year must be a 4-digit number")
            return

        # Check if new title conflicts (excluding current movie)
        for g, movies in self.app.movie_db.items():
            for m in movies:
                if m["title"].lower() == new_title.lower() and m["id"] != movie["id"]:
                    messagebox.showerror("Error", "Movie title already exists")
                    return

        # Handle poster
        new_poster_name = movie["poster"]
        if new_poster:
            import shutil
            new_poster_name = f"{new_title.replace(' ', '_').lower()}_{movie['id']}.jpg"
            poster_dest = os.path.join(POSTER_DIR, new_poster_name)
            try:
                if movie["poster"] and os.path.exists(os.path.join(POSTER_DIR, movie["poster"])):
                    os.remove(os.path.join(POSTER_DIR, movie["poster"]))
                shutil.copy(new_poster, poster_dest)
            except IOError as e:
                messagebox.showerror("Error", f"Failed to save poster: {str(e)}")
                return

        # Update movie
        old_title = movie["title"]
        self.app.movie_db[genre].remove(movie)
        updated_movie = {
            "title": new_title,
            "year": new_year,
            "description": new_desc,
            "poster": new_poster_name,
            "id": movie["id"]
        }
        self.app.movie_db[new_genre].append(updated_movie)
        self.app.poster_map.pop(old_title, None)
        self.app.poster_map[new_title] = os.path.join(POSTER_DIR, new_poster_name) if new_poster_name else None

        if self.app.save_data(self.app.movie_db, MOVIES_FILE):
            dialog.destroy()
            messagebox.showinfo("Success", "Movie updated successfully")
            self.load_movies()
            self.selected_movie = None
            self.poster_path = None

    tk.Button(dialog, text="Submit", command=submit,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=("Helvetica", 12)).pack(pady=10)

def choose_poster_edit(self, button):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg"), ("All files", "*.*")])
    if file_path:
        self.poster_path = file_path
        button.config(text="File Selected")

def delete_movie(self):
    if not self.selected_movie:
        messagebox.showerror("Error", "Please select a movie to delete")
        return

    movie, genre = self.selected_movie
    if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{movie['title']}'?"):
        # Remove movie from database
        self.app.movie_db[genre].remove(movie)
        # Remove poster file
        if movie["poster"] and os.path.exists(os.path.join(POSTER_DIR, movie["poster"])):
            try:
                os.remove(os.path.join(POSTER_DIR, movie["poster"]))
            except OSError:
                pass
        # Remove from poster map
        self.app.poster_map.pop(movie["title"], None)
        # Remove from all users' ratings
        for user_ratings in self.app.ratings.values():
            user_ratings.pop(movie["title"], None)

        if self.app.save_data(self.app.movie_db, MOVIES_FILE) and self.app.save_data(self.app.ratings, RATINGS_FILE):
            messagebox.showinfo("Success", "Movie deleted successfully")
            self.load_movies()
            self.selected_movie = None

def view_user_details(self):
    if not self.selected_user:
        messagebox.showerror("Error", "Please select a user to view details")
        return

    user = self.selected_user
    user_data = self.app.users.get(user, {})
    ratings = self.app.ratings.get(user, {})
    friends = self.app.friends.get(user, {}).get("friends", [])

    details = f"Username: {user}\n"
    details += f"Joined: {user_data.get('joined', 'N/A')}\n"
    details += f"Total Ratings: {len(ratings)}\n"
    details += f"Total Friends: {len(friends)}\n"
    details += "\nLiked Movies:\n"
    liked = [m for m, r in ratings.items() if r == 1]
    details += "\n".join(liked) if liked else "None"

    messagebox.showinfo("User Details", details)

def delete_user(self):
    if not self.selected_user:
        messagebox.showerror("Error", "Please select a user to delete")
        return

    if self.selected_user == "admin":
        messagebox.showerror("Error", "Cannot delete admin account")
        return

    if messagebox.askyesno("Confirm", f"Are you sure you want to delete user '{self.selected_user}'?"):
        user = self.selected_user
        # Remove user from users
        self.app.users.pop(user, None)
        # Remove user ratings
        self.app.ratings.pop(user, None)
        # Remove user from friends lists
        self.app.friends.pop(user, None)
        for other_user in self.app.friends:
            self.app.friends[other_user]["friends"] = [f for f in self.app.friends[other_user]["friends"] if f != user]
            self.app.friends[other_user]["requests_sent"] = [r for r in self.app.friends[other_user]["requests_sent"] if r != user]
            self.app.friends[other_user]["requests_received"] = [r for r in self.app.friends[other_user]["requests_received"] if r != user]

        if (self.app.save_data(self.app.users, USERS_FILE) and
            self.app.save_data(self.app.ratings, RATINGS_FILE) and
            self.app.save_data(self.app.friends, FRIENDS_FILE)):
            messagebox.showinfo("Success", "User deleted successfully")
            self.load_users()
            self.selected_user = None
# Main execution block to run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieMateApp(root)
    root.mainloop()


