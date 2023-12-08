<template>
  <div class="container" v-if="spotify_logged_in">
    <LoadSpinner v-if="showHideSpinner" :user_message="custom_user_message" />
    <div class="row">
      <div class="col-sm-12 text-center">How are you feeling today?</div>
    </div>
    <div class="mood-selection text-center">
      <button
        @click="submitMood('Very Happy')"
        class="btn btn-smile Very Happy"
        id="Very Happy"
      >
        😄
      </button>
      <button
        @click="submitMood('Happy')"
        id="Happy"
        class="btn btn-smile Happy"
      >
        😊
      </button>
      <button
        @click="submitMood('Neutral')"
        id="Neutral"
        class="btn btn-smile Neutral"
      >
        😐
      </button>
      <button @click="submitMood('Sad')" id="Sad" class="btn btn-smile Sad">
        🙁
      </button>
      <button
        @click="submitMood('Very Sad')"
        id="Very Sad"
        class="btn btn-smile Very Sad"
      >
        😢
      </button>
    </div>
    <div v-if="show_music_player">
      <ClientOnly>
        <MusicPlayer
          :music-playlist-data="songs_list"
          v-on:set-rating-data="setSongRating"
        ></MusicPlayer>
      </ClientOnly>
    </div>
    <div v-if="show_spotify_player">
      <div class="row">
        <div class="col-sm-6">
          <h5>Popular Tracks</h5>
          <div
            v-for="(_song, index) in model_songs.recommendations.popular_tracks"
            :key="index"
          >
            <iframe
              style="border-radius: 12px"
              :src="`https://open.spotify.com/embed/track/${getFormattedTrack(
                _song
              )}?utm_source=generator`"
              width="100%"
              height="150px"
              frameBorder="0"
              allowfullscreen=""
              allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
              loading="lazy"
            ></iframe>
          </div>
        </div>
        <div class="col-sm-6">
          <h5>Recommended Tracks</h5>
          <div
            v-for="(_song, index) in model_songs.recommendations
              .recommended_songs"
            :key="index"
          >
            <iframe
              style="border-radius: 12px"
              :src="`https://open.spotify.com/embed/track/${getFormattedTrack(
                _song
              )}?utm_source=generator`"
              width="100%"
              height="100%"
              frameBorder="0"
              allowfullscreen=""
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
            ></iframe>
          </div>
        </div>
        <div class="col-sm-6">
          <h5>A Playlist for you</h5>
          <div>
            <iframe
              style="border-radius: 12px"
              :src="`https://open.spotify.com/embed/playlist/${getFormattedTrack(
                model_songs.moodsick_playlist_uri
              )}?utm_source=generator`"
              width="100%"
              height="100%"
              frameBorder="0"
              allowfullscreen=""
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
            ></iframe>
          </div>
        </div>
        <div class="col-sm-6">
          <div v-if="model_songs.data_mined_songs.length > 0">
            <h5>Data Mined Songs</h5>
            <div
              v-for="(_song, index) in model_songs.data_mined_songs"
              :key="index"
            >
              <iframe
                style="border-radius: 12px"
                :src="`https://open.spotify.com/embed/track/${getFormattedTrack(
                  _song
                )}?utm_source=generator`"
                width="100%"
                height="352"
                frameBorder="0"
                allowfullscreen=""
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy"
              ></iframe>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- <div v-show="show_spotify_player"> -->
    <!-- <div id="embed-iframe"></div> -->
    <!-- </div> -->
  </div>
  <div class="container text-center mt-5" v-else>
    <h2>
      We request you to kindly login into Spotify for personalized
      recommendations
    </h2>
    <button class="btn btn-primary" @click="loginToSpotify">
      Login to Spotify
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showHideSpinner: false,
      user_data: null,
      show_music_player: false,
      songs_list: [],
      current_user_rating: [],
      custom_user_message: "",
      mood: null,
      show_spotify_player: false,
      model_songs: [],
      spotify_logged_in: false,
    };
  },
  mounted() {
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"));
    if (Boolean(this.user_data.spotify_logged_in)) {
      this.spotify_logged_in = true;
    }
    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      const element = document.getElementById("embed-iframe");
      const options = {
        uri: "spotify:episode:7makk4oTQel546B0PZlDM5",
      };
      const callback = (EmbedController) => {};
      IFrameAPI.createController(element, options, callback);
    };
  },
  methods: {
    async submitMood(mood) {
      this.mood = mood;
      let list = document.getElementsByClassName("mood-selection")[0].children;
      for (let item of list) {
        if (item.id != mood) {
          item.classList.add("less-op");
        } else {
        }
      }
      let random_songs = [
        "http://10.9.0.6/static/rock.00001.wav",
        "http://10.9.0.6/static/disco.00001.wav",
        "http://10.9.0.6/static/pop.00001.wav",
        "http://10.9.0.6/static/blues.00001.wav",
        "http://10.9.0.6/static/metal.00001.wav",
      ];

      try {
        const response = await fetch("http://10.9.0.6/user/get-songs", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: this.user_data.user_id,
            mood: mood,
          }),
        });
        if (!response.ok) {
          throw new Error("Failed to Login");
        }
        const responseData = await response.json();
        console.log({ responseData });
        if (responseData.length > 0) {
          this.show_music_player = true;
          this.songs_list = responseData;
        } else {
          this.show_music_player = true;
          this.songs_list = random_songs;
        }
      } catch (error) {
        console.log(error);
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
    async setSongRating(data, is_last = false) {
      data.audioFile = data.audioFile
        .substr(data.audioFile.lastIndexOf("/") + 1, data.audioFile.length - 5)
        .replaceAll(".", "");
      data.audioFile = data.audioFile.substr(0, data.audioFile.length - 3);
      this.current_user_rating.push({
        query: data.audioFile,
        rating: data.rating,
      });
      if (is_last) {
        this.show_music_player = false;
        this.custom_user_message =
          "Please wait while we mine data for you and give you songs you would love :)";
        this.showHideSpinner = true;
        try {
          const response = await fetch(
            "http://10.9.0.6/user/get-recommendations-for-user",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                ratings: this.current_user_rating,
                user_id: this.user_data.user_id,
                mood: this.mood,
              }),
            }
          );
          if (!response.ok) {
            throw new Error("Failed to Login");
          }
          const responseData = await response.json();
          this.model_songs = responseData.data;
          this.show_spotify_player = true;
          this.showHideSpinner = false;
          console.log(responseData);
          if (responseData == "Success") {
          } else {
          }
        } catch (error) {
          console.log("error", error);
        }
      }
    },
    getFormattedTrack(_song) {
      return _song.substr(_song.lastIndexOf(":") + 1, _song.length - 1);
    },
    async loginToSpotify() {
      try {
        const response = await fetch("http://10.9.0.6/user/user-auth-url", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: this.user_data.user_id,
          }),
        });
        if (!response.ok) {
          throw new Error("Failed to Login");
        }
        const responseData = await response.json();
        console.log({ responseData });
        window.location.href = responseData.url;
      } catch (error) {
        console.log(error);
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
  },
};
</script>

<style scoped>
.btn-smile {
  font-size: 36px;
  margin: 10px;
  padding: 20px 35px;
  border: none;
  border-radius: 50%;
  background-color: #f0f0f0;
  transition: transform 0.3s ease-in-out;
}

.btn-smile:hover {
  cursor: pointer;
  animation: crazyAnimation 1s infinite;
}

@keyframes crazyAnimation {
  0%,
  100% {
    transform: rotate(0) scale(1);
  }
  25% {
    transform: rotate(20deg) scale(1.2);
  }
  50% {
    transform: rotate(-20deg) scale(0.8);
  }
  75% {
    transform: rotate(10deg) scale(1.1);
  }
}
.less-op {
  opacity: 0.1;
}
</style>

<style>
.TrackWidget_widgetContainer__gADzr {
  height: 136px !important;
}
</style>