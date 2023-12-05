<template>
    <div class="music-player">
      <audio ref="audioPlayer" :src="currentTrack.url" @ended="onTrackEnd"></audio>
      <div>
        <button @click="playPause">
          {{ isPlaying ? 'Pause' : 'Play' }}
        </button>
        <button @click="nextTrack">Next</button>
      </div>
      <div>Now Playing: {{ currentTrack.name }}</div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        tracks: [
          { name: 'Track 1', url: '/path/to/track1.mp3' },
          { name: 'Track 2', url: '/path/to/track2.mp3' },
          // Add more tracks as needed
        ],
        currentTrackIndex: 0,
        isPlaying: false,
      };
    },
    computed: {
      currentTrack() {
        return this.tracks[this.currentTrackIndex];
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
        this.currentTrackIndex = (this.currentTrackIndex + 1) % this.tracks.length;
        this.play();
      },
      play() {
        this.$refs.audioPlayer.play();
        this.isPlaying = true;
      },
      onTrackEnd() {
        this.nextTrack();
      }
    }
  };
  </script>
  
  <style scoped>
  .music-player {
    /* Add styling here */
  }
  </style>
  