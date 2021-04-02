import dbussy as dbus
from dbussy import DBUS
import ravel
import asyncio

class MPRISController:
    mpris_base = 'org.mpris.MediaPlayer2'
    player_interface = mpris_base + '.Player'
    tracklist_interface = mpris_base + '.TrackList'
    playlists_interface = mpris_base = '.Playlists'
    properties_interface = 'org.freedesktop.DBus.Properties'


    async def connect(self):
        """ Connects the MPRISController object to dbus.
        """
        self.conn = await ravel.session_bus_async(asyncio.get_running_loop())
        self.dbus_daemon = ravel.def_proxy_interface(ravel.INTERFACE.CLIENT,
                                            name="DbusDaemon",
                                            introspected = dbus.standard_interfaces[DBUS.INTERFACE_DBUS],
                                            is_async=True )(connection = self.conn, dest = DBUS.SERVICE_DBUS)["/"]
    
    async def get_services(self):
        """ Return a list of all of the MPRIS-based services that are registered on the system.
            Not actually part of the MPRIS Spec, but useful.
        """
        reply = await self.dbus_daemon.ListNames()
        names = reply[0]
        return [name for name in names if name.startswith(self.mpris_base)]


    # Base
    def listen_propchanged(self, func):
        """ Create an event listener for the PropertiesChanged event.

        """
        self.conn.listen_signal(path = "/org/mpris/MediaPlayer2",
                                fallback = False,
                                interface = "org.freedesktop.DBus.Properties",
                                name = "PropertiesChanged",
                                func = func)
    

    async def send_raise(self, name):
        """ Bring media player with this name to the foreground, if possible. 
            If it can't (e.g. the media player doesn't support this), nothing happens.

        """
        return await self.send_simple_command(name, 'Raise', self.mpris_base)


    async def send_quit(self, name):
        """ Cause the media player to quit.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        return await self.send_simple_command(name, 'Quit', self.mpris_base)


    def listen_seeked(self, f):
        """ Create an event listener for the Seeked event.

        """
        self.conn.listen_signal(path = "/org/mpris/MediaPlayer2",
                                fallback = False,
                                interface = "org.mpris.MediaPlayer2.Player",
                                name = "Seeked",
                                func = f)


    async def send_simple_command(self, name, method, interface):
        """ Hit <method> in <interface> of <name>, 
        """
        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = interface,
                                                method = method)
        return await self.conn.connection.send_await_reply(request)


    async def send_play(self, name):
        """ Cause the media player to start playing.
            If it can't (e.g. the media player doesn't support this), nothing happens.
        """
        return await self.send_simple_command(name, 'Play', self.player_interface)


    async def send_pause (self, name):
        """ Cause the media player to pause.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        return await self.send_simple_command(name, 'Pause', self.player_interface)


    async def send_next (self, name):
        """ Cause the media player to go to the next track.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        return await self.send_simple_command(name, 'Next', self.player_interface)


    async def send_playpause (self, name):
        """ Cause the media player to toggle the play/pause state.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        return await self.send_simple_command(name, 'PlayPause', self.player_interface)


    async def open_uri(self, name, uri):
        """ Cause the media player to open the uri.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = 'org.mpris.MediaPlayer2.Player',
                                                method = "OpenUri")
        request.append_objects("s", uri)
        reply = await self.conn.connection.send_await_reply(request)
        return reply


    def listen_playlist_changed(self, f):
        """ Create an event listener for the PlaylistChanged event.

        """
        self.conn.listen_signal(path = "/org/mpris/MediaPlayer2",
                                fallback = False,
                                interface = "org.mpris.MediaPlayer2.Playlists",
                                name = "PlaylistChanged",
                                func = f)


    async def send_activate_playlist(self, name, playlist_id):
        """ Cause the media player to activate a specific playlist.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = 'org.mpris.MediaPlayer2.Playlists',
                                                method = "ActivatePlaylist")
        request.append_objects("o", playlist_id)
        reply = await self.conn.connection.send_await_reply(request)
        return reply


    async def send_get_playlists(self, name, index: int, max_count: int, order: str, reverse_order: bool):
        """ Get the object urls for the playlists.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = 'org.mpris.MediaPlayer2.Playlists',
                                                method = "GetPlaylists")
        request.append_objects("uusb", index, max_count, order, reverse_order)
        reply = await self.conn.connection.send_await_reply(request)
        reply = next(reply.objects)
        for x in reply:
            x[0] = str(x[0])
        return reply



    # TrackList
    async def get_tracks_metadata(self, name, track_ids):
        """ Get the metadata for the given track ids, given as a list of strings.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            Note: the track ids here are object path
        """

        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = 'org.mpris.MediaPlayer2.TrackList',
                                                method = "GetTracksMetadata")
        request.append_objects("ao", track_ids)
        reply = await self.conn.connection.send_await_reply(request)
        reply = next(reply.objects)
        reply = [{k:v[1] for k,v in r.items()} for r in reply]
        return reply

    async def add_track(self, name, uri, after_track, set_as_current ):
        """ Add a track given the file uri, give it a position, and potentially set it as current playing.
            If it can't (e.g. the media player doesn't support this), nothing happens.
            note: after_track is an object path
        """
        

        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = 'org.mpris.MediaPlayer2.TrackList',
                                                method = "AddTrack")
        request.append_objects("sob", uri, after_track, set_as_current)
        await self.conn.connection.send_await_reply(request)


    async def remove_track(self, name, track_id):
        """ Remove track <track_id> where track_id is the object path of the track
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = 'org.mpris.MediaPlayer2.TrackList',
                                                method = "RemoveTrack")
        request.append_objects("o", track_id)
        await self.conn.connection.send_await_reply(request)


    async def go_to(self, name, track_id):
        """ Start playing a specific track
            If it can't (e.g. the media player doesn't support this), nothing happens.
            
        """
        request = dbus.Message.new_method_call(destination = dbus.valid_bus_name("org.mpris.MediaPlayer2." + name),
                                                path = "/org/mpris/MediaPlayer2",
                                                iface = 'org.mpris.MediaPlayer2.TrackList',
                                                method = "GoTo")
        request.append_objects("o", track_id)
        await self.conn.connection.send_await_reply(request)

    def listen_track_list_replaced(self, fun):
        """ Create an event listener for the TrackListReplaced event.

        """
        self.conn.listen_signal(path = "/org/mpris/MediaPlayer2",
                                fallback = False,
                                interface = "org.mpris.MediaPlayer2.TrackList",
                                name = "TrackListReplaced",
                                func = fun)

    def listen_track_added(self, fun):
        """ Create an event listener for the TrackAdded event.

        """
        self.conn.listen_signal(path = "/org/mpris/MediaPlayer2",
                                fallback = False,
                                interface = "org.mpris.MediaPlayer2.TrackList",
                                name = "TrackAdded",
                                func = fun)


    def listen_track_removed(self, fun):
        """ Create an event listener for the TrackRemoved event.

        """
        self.conn.listen_signal(path = "/org/mpris/MediaPlayer2",
                                fallback = False,
                                interface = "org.mpris.MediaPlayer2.TrackList",
                                name = "TrackRemoved",
                                func = fun)


    def listen_track_metadata_changed(self, fun):
        """ Create an event listener for the TrackMetadataChanged event.

        """
        self.conn.listen_signal(path = "/org/mpris/MediaPlayer2",
                                fallback = False,
                                interface = "org.mpris.MediaPlayer2.TrackList",
                                name = "TrackMetadataChanged",
                                func = fun)

