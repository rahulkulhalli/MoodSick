<template>
  <div class="container">
    <LoadSpinner v-if="showHideSpinner" />
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
        <MusicPlayer :music-playlist-data="songs_list" v-on:set-rating-data="setSongRating"></MusicPlayer>
      </ClientOnly>
    </div>
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
      current_user_rating: []
    };
  },
  mounted() {
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"));
  },
  methods: {
    async submitMood(mood) {
      let list = document.getElementsByClassName("mood-selection")[0].children;
      for (let item of list) {
        console.log(item.id, mood, typeof item.id, mood, item.id == mood);
        if (item.id != mood) {
          item.classList.add("less-op");
        } else {
          console.log("Elsae");
        }
      }
      let random_songs = [
          "rock.00001.wav",
          "disco.00001.wav",
          "pop.00001.wav",
          "blues.00001.wav",
      "metal.00001.wav",
     ]

      this.show_music_player = true;
     this.songs_list = random_songs;
      //   try {
      //     const response = await fetch("http://10.9.0.6/user/get-songs", {
      //       method: "POST",
      //       headers: {
      //         "Content-Type": "application/json",
      //       },
      //       body: JSON.stringify({
      //         email: this.user_data.email,
      //         mood: mood
      //       }),
      //     });

      //     if (!response.ok) {
      //     //   alert("Please try again.");
      //       throw new Error("Failed to Login");
      //     }
      //     const responseData = await response.json();
      //     if (responseData.message == "Success") {

      //     } else {

      //     }
      //   } catch (error) {
      //     // alert("Some Error Occurred! Pleaser Try Again!");
      //   }
    },
    setSongRating(data, is_last=false){
        this.current_user_rating.push({
            query:  data.audioFile.substr(0,data.audioFile.length-5).replace(".",""),
            rating: data.rating
        })
        if(is_last) {
            
        }

        console.log(this.current_user_rating);
    }
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