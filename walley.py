import os, requests, json
from PIL import ImageFile

HOME = os.path.expanduser("~")

class Walley:

    def __init__(self, subreddit=None, limit=None, resolution="FHD", directory="~"):
        self.res_collection = {
        'FHD':  (1920, 1080),
        '2K':   (2560, 1440),
        'WQHD': (3440, 1440),
        '4K':   (3440, 2160),
        }
        self.ext = ('.jpg', '.png', 'jepg')
        self.sub = None   #sub as string
        self.dir = os.path.expanduser(directory)
        self.lim = None        #int
        self.res = self.res_collection[f'{resolution}']   #tuple type
        self.url = None
        self.candidates = []    #potential dls
        self.imgout = []        #validatet candidates ready for dl

    def eval_entries(self):
        resp = requests.get(self.url, headers = {'User-agent':'wppGetter'})
        if resp.status_code != 200:
            return False
        elif resp.json()['data']['dist'] == 0:
            return False
        elif self.lim > 200:
            return False    #maybe change the max_limit in the future
        else: 
            self.data = resp.json()
            return True

    def get_candidates(self):
        for entry in self.data['data']['children']:
            self.candidates.append(entry['data']['url'])
        return self.candidates

    def eval_candidate(self, entry):
        data = requests.get(entry, headers = {'User-agent':'wppGetter'}, stream=True).content   #raw data
        parser = ImageFile.Parser()
        parser.feed(data)
        if not entry.lower().endswith(self.ext):    #check file extensions
            return False
        try:
            if entry.lower().startswith('http://i.redd.it/') or entry.lower().startswith('http://i.imgur.com/'):    #filter img sites
                (x, y) = (parser.image.size[0], parser.image.size[1])
                if (x,y) >= self.res:   #check resolution
                    return True
                else:
                    return False
            else:
                return False
        except:
            print("Error while validating resolution for ", entry, "continuing...")
            return False

    def download(self, URL):
        try:
            with open (f"{self.dir}/{os.path.basename(URL)}", "wb") as f:
                f.write(requests.get(URL, headers = {'User-agent':'wppGetter'}, stream=True).content)
            return True
        except:
            return False
            raise Exception("An error while downloading and/or saving the picture ouccurred")

    def redl_protection(self, URL):
        img = os.path.join(self.dir, os.path.basename(URL))
        if os.path.isfile(img):
            return True
        else:
            return False
    def dir_checkup(self):
        if os.path.isdir(f"{self.dir}"):
            return True
        else:
            return False

    def startup_procedure(self):
        #check for config
        if not os.path.exists(f"{HOME}/.config/walley"):
            Logger(f"No config found, creating template config in {HOME}/.config/Walley", 'RED').log()
            os.makedirs(f"{HOME}/.config/walley")
            open(f"{HOME}/.config/walley/config.json", "w").close()
            data = {
                "subreddit":    "wallpapers",
                "limit":        "10",
                "resolution":   "FHD",
                "directory":    "~/Pictures"
            }
            with open(f"{HOME}/.config/walley/config.json", "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        #load config into class vars
        else:
            try:
                with open(f"{HOME}/.config/walley/config.json") as f:
                    data = json.load(f)
                    self.sub = data["subreddit"]
                    self.dir = os.path.expanduser(data["directory"])
                    self.lim = int(data["limit"])
                    self.resolution = data["resolution"]
                    self.url = f"https://www.reddit.com/r/{self.sub}/top/.json?t=all&limit={self.lim}"
                    
                    #Logging
                    Logger("Config found, proceding with following settings:", "GREEN").log()
                    Logger(f"Subreddit: r/{self.sub}\nDirectory: {self.dir}\nResolution: {self.resolution}\nLimit: {self.lim}\n").log()
            except:
                raise Exception("Error while reading config, check entries.")
                return 1

class Logger:

    def __init__(self, message, color='RESET'):
        self.color_collection = {
        'RED':      '\033[1;31m',
        'GREEN':    '\033[1;32m',
        'ORANGE':   '\033[1;33m',
        'RESET':    '\033[0m',
        }
        self.color = self.color_collection[f"{color}"]
        self.message = message
    
    def log(self, line=False):
        if line:
            print("--------------------------------")
            print(self.color + self.message + self.color_collection['RESET'])
        else:
            print(self.color + self.message + self.color_collection['RESET'])



if __name__ == '__main__':
    Wall = Walley()

    Wall.startup_procedure()
    
    Logger("Verifying download directory", "ORANGE").log()
    if not Wall.dir_checkup():
        Logger("Invalid directory specified. Check if directory specified in config exitst", "RED").log(1)
        exit()

    Logger("Checking connection and subreddit", "ORANGE").log()
     
    if Wall.eval_entries():
        Logger("Check successfull", "GREEN").log()

        Logger("Getting images links", "ORANGE").log(1)
    
        candidates = Wall.get_candidates()

        Logger("Evaluating images", "ORANGE").log()

        for candidate in candidates:
            if not Wall.redl_protection(candidate):
                if Wall.eval_candidate(candidate):
                    Logger(f"Downloading Image {candidate}", "GREEN").log()
                    Wall.download(str(candidate))
            
                else:
                    Logger("Image did not match criteria. Skipping...", "ORANGE").log()
            else:
                Logger("Image was already downloaded once before", "ORANGE").log()
            
        Logger("Completed all downloads. Exiting...", "GREEN").log(1)
        exit()
