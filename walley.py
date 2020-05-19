import os, requests, json
from PIL import ImageFile

HOME = os.path.expanduser("~")


class Walley:
    """Walley.
    Main programme class
    """
    def __init__(self,
                 subreddit=None,
                 limit=None,
                 resolution="FHD",
                 directory="~"):
        """__init__.
        Class init.
        Args are overwritten by config. Intended for testing/debugging
        Args:
            subreddit:  str(subreddit)
            limit:      int(max downloads)
            resolution: str("FHD")
            directory:  str("~/Pictures/")
        """
        self.res_collection = {
            'FHD': (1920, 1080),
            '2K': (2560, 1440),
            'WQHD': (3440, 1440),
            '4K': (3440, 2160),
        }
        self.ext = ('.jpg', '.png', 'jepg')
        self.sub = None  #sub as string
        self.dir = os.path.expanduser(directory)
        self.lim = None  #int
        self.res = self.res_collection[f'{resolution}']  #tuple type
        self.url = None
        self.nsfw = False
        self.candidates = []  #potential dls
        self.imgout = []  #validatet candidates ready for dl

    def eval_entries(self):
        """eval_entries.
        Makes main request and retrieves json, checks HTTP code, subreddit validity and max_limit compliance
        """
        resp = requests.get(self.url, headers={'User-agent': 'wppGetter'})
        if resp.status_code != 200:
            return False
        elif resp.json()['data']['dist'] == 0:
            return False
        elif self.lim > 200:
            return False  #maybe change the max_limit in the future
        else:
            self.data = resp.json()
            return True

    def get_candidates(self):
        """get_candidates.
        Appends all potential downloads to self.candidates array. Can filter nsfw contet if set in config
        Must be run after self.eval_entries()!
        """
        for entry in self.data['data']['children']:
            #filter out nsfw if filter is on
            if not self.nsfw:
                if entry['data']['over_18']:
                    continue
            self.candidates.append(entry['data']['url'])
        return self.candidates

    def eval_candidate(self, entry):
        """eval_candidate.
        Main filtering function. Checks sequentially for: 
            -file extension
            -hosting sevice
            -resolution
        Args:
            entry: image URL
        """
        data = requests.get(entry,
                            headers={
                                'User-agent': 'wppGetter'
                            },
                            stream=True).content  #raw data
        parser = ImageFile.Parser()
        parser.feed(data)
        if not entry.lower().endswith(self.ext):  #check file extensions
            return False
        try:
            if entry.lower().startswith('http://i.redd.it/') or entry.lower(
            ).startswith('http://i.imgur.com/') or entry.lower().startswith(
                    'https://i.redd.it/') or entry.lower().startswith(
                        'https://i.imgur.com/'):  #filter img sites
                (x, y) = (parser.image.size[0], parser.image.size[1])
                if (x, y) >= self.res:  #check resolution
                    return True
                else:
                    return False
            else:
                return False
        except:
            print("Error while validating resolution for ", entry,
                  "continuing...")
            return False

    def download(self, URL):
        """download.
        Downloads and saves an image file 
        Args:
            URL: image file URL
        """
        try:
            with open(f"{self.dir}/{os.path.basename(URL)}", "wb") as f:
                f.write(
                    requests.get(URL,
                                 headers={
                                     'User-agent': 'wppGetter'
                                 },
                                 stream=True).content)
            return True
        except:
            return False
            raise Exception(
                "An error while downloading and/or saving the picture ouccurred"
            )

    def redl_protection(self, URL):
        """redl_protection.
        Finds potential duplicate downloads by comparing remote with local files
        Args:
            URL: image URL
        """
        img = os.path.join(self.dir, os.path.basename(URL))
        if os.path.isfile(img):
            return True
        else:
            return False

    def dir_checkup(self):
        """dir_checkup.
        Checks if download directory exitsts
        """
        if os.path.isdir(f"{self.dir}"):
            return True
        else:
            return False

    def startup_procedure(self):
        """startup_procedure.
        checks for user config (and creates it if not present) and loads config into class vars 
        """
        #check for config
        if not os.path.exists(f"{HOME}/.config/walley"):
            Logger(
                f"No config found, creating template config in {HOME}/.config/Walley",
                'RED').log()
            os.makedirs(f"{HOME}/.config/walley")
            open(f"{HOME}/.config/walley/config.json", "w").close()
            data = {
                "subreddit": "wallpapers",
                "limit": "10",
                "resolution": "FHD",
                "directory": "~/Pictures",
                "allow_nsfw": False
            }
            with open(f"{HOME}/.config/walley/config.json", "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        #load config into class vars
        try:
            with open(f"{HOME}/.config/walley/config.json") as f:
                data = json.load(f)
                self.sub = data["subreddit"]
                self.dir = os.path.expanduser(data["directory"])
                self.lim = int(data["limit"])
                self.resolution = data["resolution"]
                self.res = self.res_collection[
                    f'{self.resolution}']  #tuple type
                self.url = f"https://www.reddit.com/r/{self.sub}/top/.json?t=all&limit={self.lim}"
                self.nsfw = data["allow_nsfw"]
                #Logging
                Logger("Config found, proceding with following settings:",
                       "GREEN").log()
                Logger(
                    f"\nSubreddit: r/{self.sub}\nDirectory: {self.dir}\nResolution: {self.resolution}\nLimit: {self.lim}\n"
                ).log()
                if self.nsfw:
                    Logger("NSFW CONTET FILTERING IS OFF", "RED").log()
                else:
                    Logger("Info: NSFW content filtering is on", "GREEN").log()
        except:
            raise Exception("Error while reading config, check entries.")
            return 1


class Logger:
    """Logger.
    Contains logging functions with color highlighting for linux terminals
    """
    def __init__(self, message, color='RESET'):
        """__init__.
        Class init
        Args:
            message: message to print
            color: color of print, defaults to white if unset
        """
        self.color_collection = {
            'RED': '\033[1;31m',
            'GREEN': '\033[1;32m',
            'ORANGE': '\033[1;33m',
            'RESET': '\033[0m',
        }
        self.color = self.color_collection[f"{color}"]
        self.message = message

    def log(self, line=False):
        """log.
        Main logging function
        Args:
            line: prints a separator line if set to True or 1
        """
        if line:
            print("--------------------------------")
            print(self.color + self.message + self.color_collection['RESET'])
        else:
            print(self.color + self.message + self.color_collection['RESET'])


if __name__ == '__main__':

    Wall = Walley()  #make instance

    Wall.startup_procedure()  #load class vars from config

    Logger("Verifying download directory", "ORANGE").log()
    if not Wall.dir_checkup():  #check for download dir
        Logger(
            "Invalid directory specified. Check if directory specified in config exitst",
            "RED").log(1)
        exit()

    Logger("Checking connection and subreddit", "ORANGE").log()

    if Wall.eval_entries():  #get json, check http code and subreddit
        Logger("Check successfull", "GREEN").log()

        Logger("Getting images links", "ORANGE").log(1)

        candidates = Wall.get_candidates()  #make dl array

        Logger("Evaluating images", "ORANGE").log()

        for candidate in candidates:  #filter array
            if not Wall.redl_protection(candidate):
                if Wall.eval_candidate(candidate):
                    Logger(f"Downloading Image {candidate}", "GREEN").log()
                    Wall.download(str(candidate))  #download filtered file

                else:
                    Logger("Image did not match criteria. Skipping...",
                           "ORANGE").log()
            else:
                Logger("Image was already downloaded once before",
                       "ORANGE").log()

        Logger("Completed all downloads. Exiting...", "GREEN").log(1)
        exit()
