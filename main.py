import spotipy
import spotipy.util as util


username = "alisdairv"
new_dnb_id = '2QvUUgts8I1d1gaMQPDOzI'
#label_file = '/home/alisdairv/Downloads/dnb-labels.txt'
label_file = '/Users/alisdairv/Documents/personal/new_dnb/new_labels.txt'
#label_file = '/home/alisdairv/Documents/personal/new_dnb/imltd.txt'
#year=2018

def get_token(scope):
    client_secret = "9c95b182712d40a5b4ea6619ece9a021"
    client_id = "374f2ecb9c6045dca42f5a12ada529b7"
    redirect_url = "http://localhost"
    token = util.prompt_for_user_token(
                username,
                scope,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_url,
            )
    return token

def all_tracks_from_playlist_resp(sp, resp):
    tracks = []
    tracks_obj = resp['tracks']
    for track in tracks_obj['items']:
        tracks.append(track['track']['id'])
        while tracks_obj['next']:
            try:
                tracks_obj = sp.next(tracks_obj)
            except spotipy.client.SpotifyException:
                sp = spotipy.Spotify(auth=get_token('playlist-modify-private'))
                tracks_obj = sp.next(tracks_obj)
            for track in tracks_obj['items']:
                tracks.append(track['track']['id'])
    return tracks

def get_playlist_track_ids(sp, playlist_id):
    res = sp.user_playlist(username, new_dnb_id)
    playlist_tracks = all_tracks_from_playlist_resp(sp, res)
    return playlist_tracks

def get_labels(labels_file):
    with open(labels_file, 'r') as f:
        labels = f.readlines()
    return labels

def all_tracks_from_search_resp(sp, resp):
    tracks = []
    tracks_obj = resp['tracks']
    for track in tracks_obj['items']:
        tracks.append(track['id'])
        while tracks_obj['next']:
            tracks_obj = sp.next(tracks_obj)['tracks']
            for track in tracks_obj['items']:
                tracks.append(track['id'])
    return tracks

def get_label_track_ids(sp, label_string):
    from datetime import datetime
    now = datetime.now()
    search_str = "year:{} AND label:'{}'".format(now.year, label_string.strip())
    res = sp.search(search_str)
    label_track_ids = all_tracks_from_search_resp(sp, res)
    return label_track_ids

def get_labels_track_ids(sp, label_list):
    labels_tracks = []
    for label in label_list:
        label_tracks = get_label_track_ids(sp, label)
        labels_tracks = labels_tracks + label_tracks
    return labels_tracks

def get_new_track_ids(existing_tracks, input_tracks):
    new_tracks = list(set(input_tracks) - set(playlist_tracks))
    return new_tracks

def get_new_track_ids_new(existing_tracks, input_tracks):
    new_tracks = [id for id in input_tracks if id not in existing_tracks]
    return new_tracks

def add_tracks_to_playlist(sp, playlist_id, track_ids):
    max_per_req = 100
    for i in range(0, len(track_ids), max_per_req):
        end_idx = i + max_per_req if i + max_per_req < len(track_ids) else len(track_ids)
        req_tracks = track_ids[i:end_idx]

        #res = 'adding {} tracks'.format(len(req_tracks))
        try:
            res = sp.user_playlist_add_tracks(username, new_dnb_id, req_tracks)
        except spotipy.client.SpotifyException:
            sp = spotipy.Spotify(auth=get_token('playlist-modify-private'))
            res = sp.user_playlist_add_tracks(username, new_dnb_id, req_tracks)
        print(res)

sp = spotipy.Spotify(auth=get_token('playlist-modify-private'))
# playlist_tracks = get_playlist_track_ids(sp, new_dnb_id)
# print('num playlist tracks: {}'.format(len(playlist_tracks)))
#
tracks_file = '/Users/alisdairv/Documents/personal/new_dnb/tracks.txt'
#
# with open(tracks_file, 'w') as f:
#     for track in playlist_tracks:
#         f.write('{}\n'.format(track))

with open(tracks_file, 'r') as f:
    playlist_tracks = f.readlines()

playlist_tracks = [track.strip() for track in playlist_tracks]
print('num playlist tracks: {}'.format(len(playlist_tracks)))

labels_list = get_labels(label_file)
labels_tracks = get_labels_track_ids(sp, labels_list)
print('num labels tracks: {}'.format(len(labels_tracks)))
new_tracks = get_new_track_ids_new(playlist_tracks, labels_tracks)

print('num new_tracks: {}'.format(len(new_tracks)))
add_tracks_to_playlist(sp, new_dnb_id, new_tracks)

with open(tracks_file, 'a') as f:
    for track in new_tracks:
        f.write('{}\n'.format(track))

