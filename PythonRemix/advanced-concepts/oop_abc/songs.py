class PlayList():
    def __init__(self, name:str):
        self.name = name
        self.songs = []
        
    def add_song(self, song) ->str:
        self.songs.append(song)
        print(f"Added {song} to playlist")
    
    def remove_song(self, song) -> str:
        self.songs.remove(song)
        
        print(f"{song} removed from playlist")
        
    def show_songs(self) -> list:
        print(f"Playlist {self.name}")
        
        for song in self.songs:
            print(f"- {song}")
            
    
my_playlist = PlayList("Favorites")

my_playlist.add_song("Like You by Tatiana")
my_playlist.add_song("Nights by Avichi")
my_playlist.add_song("It's okay by Night Eagle")
my_playlist.add_song("One by one by unkown")

my_playlist.show_songs()

print(f"You have {len(my_playlist.songs) }songs")

my_playlist.remove_song("One by one by unkown")

print(f"You have {len(my_playlist.songs)} songs")
    
    