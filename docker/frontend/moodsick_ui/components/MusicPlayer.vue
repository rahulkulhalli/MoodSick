<template>
  <main class="audioPlayer" id="app">
    <div class="audioPlayerList" :class="{ isActive: isPlaylistActive }">
      <p class="debugToggle" v-on:click="toggleDebug()">debug: {{ debug }}</p>
    </div>
    <div class="audioPlayerUI" :class="{ isDisabled: isPlaylistActive }">
      Listening to #{{ currentSong + 1 }} out of {{ totalSongs }} Snippets
      <div class="albumImage">
        <transition
          name="ballmove"
          enter-active-class="animated zoomIn"
          leave-active-class="animated fadeOutDown"
          mode="out-in"
        >
          <img
            @load="onImageLoaded()"
            :src="getMusicImage"
            :key="currentSong"
            ondragstart="return false;"
            id="playerAlbumArt"
          />
        </transition>
        <div class="loader" :key="currentSong">Loading...</div>
      </div>
      <div class="playerButtons">
        <a class="button play" v-on:click="playAudio()" title="Play/Pause Song">
          <transition name="slide-fade" mode="out-in">
            <i
              class="zmdi"
              :class="[
                currentlyStopped
                  ? 'zmdi-stop'
                  : currentlyPlaying
                  ? 'zmdi-pause-circle'
                  : 'zmdi-play-circle',
              ]"
              :key="1"
            ></i>
          </transition>
        </a>
        <a
          class="button"
          :class="{ isDisabled: currentSong == musicPlaylist.length - 1 }"
          v-on:click="nextSong()"
          title="Next Song"
          ><i class="zmdi zmdi-skip-next"></i
        ></a>

        <star-rating
          :key="randomKey"
          v-model:rating="rating"
          @update:rating="setRating"
          v-bind:increment="1"
          v-bind:max-rating="5"
          inactive-color="#000"
          active-color="#f00"
          v-bind:star-size="30"
          style="justify-content: center"
        ></star-rating>
      </div>
    </div>
  </main>
</template>
  
  <script>
import StarRating from "vue-star-rating";

export default {
  components: {
    StarRating,
  },
  props: {
    musicPlaylistData: {
      type: Array,
      default: [],
    },
  },
  data() {
    return {
      randomKey: 0,
      rating: 0,
      audio: "",
      imgLoaded: false,
      currentlyPlaying: false,
      currentlyStopped: false,
      currentTime: 0,
      checkingCurrentPositionInTrack: "",
      trackDuration: 0,
      currentProgressBar: 0,
      isPlaylistActive: false,
      currentSong: 0,
      debug: false,
      musicPlaylist: [],
      audioFile: "",
      totalSongs: 0,
      bgImages: [
        "/music_image_1.jpg",
        "/music_image_2.jpg",
        "/music_image_3.jpg"
      ],
    };
  },
  created() {
    this.musicPlaylist = this.musicPlaylistData;
    this.musicPlaylist = this.musicPlaylist.map((item) => {
      return { url: item };
    });
    this.totalSongs = this.musicPlaylist.length;
  },
  computed: {
    currentTrack() {
      return this.tracks[this.currentTrackIndex];
    },
    fancyTimeFormat: function (s) {
      return (s - (s %= 60)) / 60 + (9 < s ? ":" : ":0") + s;
    },
    getMusicImage(){
      return `/${this.getImageFromGenre(this.musicPlaylist[this.currentSong].url)}-logo.png`;
    }
  },
  methods: {
    playPause() {
      const audio = this.$refs.audioPlayer;
      if (this.isPlaying) {
        audio.pause();
      } else {
        audio.play();
      }
      this.isPlaying = !this.isPlaying;
    },
    nextTrack() {
      this.currentTrackIndex =
        (this.currentTrackIndex + 1) % this.tracks.length;
      this.play();
    },
    play() {
      this.$refs.audioPlayer.play();
      this.isPlaying = true;
    },
    onTrackEnd() {
      this.nextTrack();
    },
  },
  mounted: function () {
    this.changeSong();
    this.audio.loop = false;
  },
  methods: {
    togglePlaylist: function () {
      this.isPlaylistActive = !this.isPlaylistActive;
    },
    changeBgImage(){
      // this.getMusicImage = `/${this.getImageFromGenre(this.musicPlaylist[this.currentSong].url)}-logo.png`;
    },
    nextSong: function () {
      this.changeBgImage()
      if (this.rating == 0) {
        alert("Please select a rating!!!");
        return;
      }
      this.rating = 0;
      this.randomKey +=1;
      if (this.currentSong < this.musicPlaylist.length - 1)
        this.changeSong(this.currentSong + 1);
      else
        this.stopAudio()
    },
    prevSong: function () {
      if (this.currentSong > 0) this.changeSong(this.currentSong - 1);
    },
    changeSong: function (index) {
      var wasPlaying = this.currentlyPlaying;
      this.imageLoaded = false;
      if (index !== undefined) {
        this.stopAudio();
        this.currentSong = index;
      }
      this.audioFile = this.musicPlaylist[this.currentSong].url;
      this.audio = new Audio(this.audioFile);
      var localThis = this;
      this.audio.addEventListener("loadedmetadata", function () {
        localThis.trackDuration = Math.round(this.duration);
      });
      this.audio.addEventListener("ended", this.handleEnded);
      if (wasPlaying) {
        this.playAudio();
      }
    },
    isCurrentSong: function (index) {
      if (this.currentSong == index) {
        return true;
      }
      return false;
    },
    getCurrentSong: function (currentSong) {
      return this.musicPlaylist[currentSong].url;
    },
    playAudio: function () {
      if (
        this.currentlyStopped == true &&
        this.currentSong + 1 == this.musicPlaylist.length
      ) {
        this.currentSong = 0;
        this.changeSong();
      }
      if (!this.currentlyPlaying) {
        this.getCurrentTimeEverySecond(true);
        this.currentlyPlaying = true;
        this.audio.play();
      } else {
        this.stopAudio();
      }
      this.currentlyStopped = false;
    },
    stopAudio: function () {
      this.audio.pause();
      this.currentlyPlaying = false;
      this.pausedMusic();
    },
    handleEnded: function () {
      if (this.currentSong + 1 == this.musicPlaylist.length) {
        this.stopAudio();
        this.currentlyPlaying = false;
        this.currentlyStopped = true;
      } else {
        this.currentlyPlaying = false;
        this.currentSong++;
        this.changeSong();
        this.playAudio();
      }
    },
    onImageLoaded: function () {
      this.imgLoaded = true;
    },
    getCurrentTimeEverySecond: function (startStop) {
      var localThis = this;
      this.checkingCurrentPositionInTrack = setTimeout(
        function () {
          localThis.currentTime = localThis.audio.currentTime;
          localThis.currentProgressBar =
            (localThis.audio.currentTime / localThis.trackDuration) * 100;
          localThis.getCurrentTimeEverySecond(true);
        }.bind(this),
        1000
      );
    },
    pausedMusic: function () {
      clearTimeout(this.checkingCurrentPositionInTrack);
    },
    toggleDebug: function () {
      this.debug = !this.debug;
      document.body.classList.toggle("debug");
    },
    setRating(rating) {
      this.$emit("set-rating-data", {
        rating: rating,
        audioFile: this.audioFile,
      }, this.currentSong == this.totalSongs-1);
      this.nextSong();
    },
    getImageFromGenre(x){
      return x.substr(x.lastIndexOf("/")+1, x.length).substr(0, x.substr(x.lastIndexOf("/")+1, x.length).indexOf("."))

    }
  },
  watch: {
    currentTime: function () {
      this.currentTime = Math.round(this.currentTime);
    },
  },
  beforeDestroy: function () {
    this.audio.removeEventListener("ended", this.handleEnded);
    this.audio.removeEventListener("loadedmetadata", this.handleEnded);
    clearTimeout(this.checkingCurrentPositionInTrack);
  },
};
</script>
  
  <style scoped>
@import url("https://cdnjs.cloudflare.com/ajax/libs/material-design-iconic-font/2.2.0/css/material-design-iconic-font.min.css");

.animated {
  animation-duration: 0.5s;
}
.audioPlayer {
  position: relative;
  background-color: #eceff1;
  min-height: 25rem;
  width: 20rem;
  overflow: hidden;
  padding: 1.5rem;
  margin: 0 auto;
  border-radius: 0.5rem;
  box-shadow: 0 19px 38px rgba(0, 0, 0, 0.3), 0 15px 12px rgba(0, 0, 0, 0.22);
  user-select: none;
}
.audioPlayer .nav-icon {
  width: 15px;
  height: 12px;
  position: absolute;
  top: 1.125rem;
  left: 1.5rem;
  transform: rotate(0deg);
  transition: 0.25s ease-in-out;
  cursor: pointer;
}
.audioPlayer .nav-icon span {
  display: block;
  position: absolute;
  height: 2px;
  width: 100%;
  background: rgba(0, 0, 0, 0.75);
  border-radius: 6px;
  opacity: 1;
  left: 0;
  transform: rotate(0deg);
  transition: 0.5s ease-in-out;
}
.audioPlayer .nav-icon span:nth-child(1) {
  top: 0px;
}
.audioPlayer .nav-icon span:nth-child(2) {
  top: 5px;
}
.audioPlayer .nav-icon span:nth-child(3) {
  top: 10px;
}
.audioPlayer .nav-icon.isActive span:nth-child(1) {
  top: 5px;
  transform: rotate(135deg);
}
.audioPlayer .nav-icon.isActive span:nth-child(2) {
  opacity: 0;
  left: -60px;
}
.audioPlayer .nav-icon.isActive span:nth-child(3) {
  top: 5px;
  transform: rotate(-135deg);
}
.audioPlayer .audioPlayerList {
  color: rgba(0, 0, 0, 0.75);
  width: 17rem;
  transition: 0.5s;
  transform: translateX(-200%);
  position: absolute;
  margin-top: 1.5rem;
  overflow: auto;
  z-index: 10;
  will-change: transform;
}
.audioPlayer .audioPlayerList.isActive {
  transform: translateX(0);
}
.audioPlayer .audioPlayerList .item {
  margin-bottom: 1.5rem;
  border-left: 0.1rem solid transparent;
  transition: 0.2s;
}
.audioPlayer .audioPlayerList .item:hover {
  padding-left: 0.5rem;
  cursor: pointer;
}
.audioPlayer .audioPlayerList .item .title {
  color: rgba(0, 0, 0, 1);
  font-size: 1rem;
  margin-bottom: 0.75rem;
}
.audioPlayer .audioPlayerList .item .artist {
  color: rgba(0, 0, 0, 0.5);
  font-size: 0.8rem;
}
.audioPlayer .audioPlayerList .item.isActive {
  border-left-color: black;
  padding-left: 1rem;
}
.audioPlayer .audioPlayerList .debugToggle {
  cursor: pointer;
  color: red;
}
.audioPlayer .audioPlayerUI {
  margin-top: 1.5rem;
  will-change: transform, filter;
  transition: 0.5s;
}
.audioPlayer .audioPlayerUI.isDisabled {
  transform: scale(0.75) translateX(100%);
  filter: blur(5px) grayscale(100%);
}
.audioPlayer .audioPlayerUI .albumDetails {
  text-align: center;
  margin: 2rem 0;
}
.audioPlayer .audioPlayerUI .albumDetails p {
  margin: 0px;
}
.audioPlayer .audioPlayerUI .albumDetails p.title {
  font-size: 1rem;
  color: rgba(0, 0, 0, 1);
}
.audioPlayer .audioPlayerUI .albumDetails p.artist {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  font-weight: none;
  color: rgba(0, 0, 0, 0.75);
  transition-delay: 100ms;
}
.audioPlayer .audioPlayerUI .albumImage {
  width: 17rem;
  height: 17rem;
  overflow: hidden;
  margin: 0 auto;
}
.audioPlayer .audioPlayerUI .albumImage img {
  width: 100%;
  height: 100%;
  z-index: 10;
  object-fit: cover;
  object-position: 50% 50%;
  border-radius: 0.5rem;
}
.audioPlayer .audioPlayerUI .playerButtons {
  position: relative;
  margin: 0 auto;
  text-align: center;
}
.audioPlayer .audioPlayerUI .playerButtons .button {
  font-size: 2rem;
  display: inline-block;
  vertical-align: middle;
  padding: 0.5rem;
  margin: 0 0.25rem;
  color: rgba(0, 0, 0, 0.75);
  border-radius: 50%;
  outline: 0;
  text-decoration: none;
  cursor: pointer;
  transition: 0.5s;
}
.audioPlayer .audioPlayerUI .playerButtons .button.play {
  font-size: 4rem;
  margin: 0 1.5rem;
}
.audioPlayer .audioPlayerUI .playerButtons .button:active {
  opacity: 0.75;
  transform: scale(0.75);
}
.audioPlayer .audioPlayerUI .playerButtons .button.isDisabled {
  color: rgba(0, 0, 0, 0.2);
  cursor: initial;
}
.audioPlayer .audioPlayerUI .playerButtons .button.isDisabled:active {
  transform: none;
}
.audioPlayer .audioPlayerUI .currentTimeContainer {
  width: 100%;
  height: 1rem;
  display: flex;
  justify-content: space-between;
}
.audioPlayer .audioPlayerUI .currentTimeContainer .currentTime,
.audioPlayer .audioPlayerUI .currentTimeContainer .totalTime {
  font-size: 0.5rem;
  font-family: monospace;
  color: rgba(0, 0, 0, 0.75);
}
.audioPlayer .audioPlayerUI .currentProgressBar {
  width: 100%;
  background-color: rgba(0, 0, 0, 0.1);
  margin: 0.75rem 0;
}
.audioPlayer .audioPlayerUI .currentProgressBar .currentProgress {
  background-color: rgba(0, 0, 0, 0.75);
  width: 0px;
  height: 1px;
  transition: 100ms;
}
.loader {
  margin: 60px auto;
  font-size: 10px;
  position: relative;
  text-indent: -9999em;
}
/* data change transitions */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter,
.slide-fade-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
/* pen specific formatting */
body {
  background: #29b6f6;
  color: rgba(255, 255, 255, 0.7);
  font-family: Raleway, sans-serif;
  padding: 3rem;
}
.heading {
  text-align: center;
  margin: 0;
  margin: 2rem 0;
  font-family: Inconsolata, monospace;
}
.heading h1 {
  color: #eceff1;
  margin: 0;
  margin-bottom: 1rem;
  font-size: 1.75rem;
}
.heading p {
  margin: 0;
  font-size: 0.85rem;
}
.heading a {
  color: rgba(255, 255, 255, 0.8);
  transition: 0.3s;
  text-decoration-style: dotted;
}
.heading a:hover {
  color: rgba(255, 255, 255, 1) !important;
}
.heading a:visited {
  color: rgba(255, 255, 255, 0.5);
}
</style>
  