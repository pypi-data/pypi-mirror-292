import json

class JsonHandle:
    def __init__(self, playername = ""):
       with open('player_info.json', 'r') as openfile: self.player_info_object = json.load(openfile)
       self.add_player_if_unique(playername)

    def add_player_if_unique(self, playername):
        unique = True
        for i in range(len(self.player_info_object["players"])):
            if self.player_info_object["players"][i]["username"] == playername:
                unique = False
        if unique:
            self.player_info_object["players"].append({"username": playername, "gambling": "False"})
            json_object = json.dumps(self.player_info_object, indent=2) 
            with open("player_info.json", "w") as outfile: outfile.write(json_object)
        pass

    def add_roll(self, playername, die, roll, timestamp):
        index = self.calc_index(playername)
        try:
            self.player_info_object["players"][index]["rolls"].append({
            "die": die, 
            "roll": roll,
            "timestamp": timestamp
            })
        except:
            self.player_info_object["players"][index]["rolls"] = [{
            "die": die, 
            "roll": roll,
            "timestamp": timestamp
            }]
        json_object = json.dumps(self.player_info_object, indent=2) 
        with open("player_info.json", "w") as outfile: outfile.write(json_object)

    def calc_index(self, playername):
        for i in range(len(self.player_info_object["players"])):
            if self.player_info_object["players"][i]["username"] == playername: 
                return i
        else: return None

    def gambling(self, playername):
        index = self.calc_index(playername)
        return self.player_info_object["players"][index]["gambling"] == "True"

    def update_json(self, playername, gambling = None):
        index = self.calc_index(playername)
        if (gambling != None):
            self.player_info_object["players"][index]["gambling"] = str(gambling)
        json_object = json.dumps(self.player_info_object, indent=2)
        with open("player_info.json", "w") as outfile: outfile.write(json_object)

    def get_rolls(self, playername):
        index = self.calc_index(playername)
        return self.player_info_object["players"][index]["rolls"]
    
    def clear_player_data(self):
        if self.message.author.name == 'kaczynskicore':
            self.player_info_object["players"].clear()
            json_object = json.dumps(self.player_info_object, indent=2)
            with open("player_info.json", "w") as outfile: outfile.write(json_object)
