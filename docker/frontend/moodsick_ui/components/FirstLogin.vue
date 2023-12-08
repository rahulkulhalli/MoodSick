<template>
  <div class="container mt-5">
    <!-- <button
      type="button"
      class="btn btn-primary"
      data-bs-toggle="modal"
      data-bs-target="#startFlowModal"
    >
      Start New Flow
    </button>
    <MusicPlayer></MusicPlayer> -->
    <div
      class="modal fade"
      id="startFlowModal"
      tabindex="-1"
      aria-labelledby="modalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title" id="modalLabel">Welcome to Moodsick!</h3>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <h5>Answer some questions to help us understand to better</h5>

            <div v-for="(mood, index) in moods" :key="index">
              <span
                >{{ index + 1 }}) When you are feeling {{ mood }}, what kind of
                music do you feel listening to?</span
              >
              <div v-for="(genre, genre_index) in genres" :key="genre_index">
                <input
                  type="checkbox"
                  :id="genre"
                  @change="update_setting(mood, genre)"
                />
                <label :for="genre">{{ genre }}</label>
              </div>
            </div>
            <div>
              <button class="btn btn-primary" @click="save_preferences">
                Save Preferences
              </button>
            </div>

            <!-- <p>Select your mood:</p> -->

            <!-- <div class="mood-selection text-center">
              <button @click="submitMood('very happy')" class="btn btn-smile">
                😄
              </button>
              <button @click="submitMood('happy')" class="btn btn-smile">
                😊
              </button>
              <button @click="submitMood('neutral')" class="btn btn-smile">
                😐
              </button>
              <button @click="submitMood('sad')" class="btn btn-smile">
                🙁
              </button>
              <button @click="submitMood('very sad')" class="btn btn-smile">
                😢
              </button>
            </div> -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
  <script>
import * as Bootstrap from "bootstrap";

export default {
  data() {
    return {
      genres: [],
      moods: [],
      user_responses: {},
      user_data: null,
    };
  },
  created() {
    this.getGenres();
  },
  mounted() {
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"));
    this.$nextTick(() => {
      const modal = new Bootstrap.Modal(
        document.getElementById("startFlowModal")
      );
      modal.show();
    });
  },
  methods: {
    submitMood(mood) {
      const modal = new Bootstrap.Modal(
        document.getElementById("startFlowModal")
      );
      modal.hide();
    },
    update_setting(mood, genre) {
      if (genre in this.user_responses[mood]) {
        this.user_responses[mood].filter((e) => e !== mood);
      } else {
        this.user_responses[mood].push(genre);
      }
    },
    async getGenres() {
      try {
        const response = await fetch("http://10.9.0.6/admin/genres-moods", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        if (!response.ok) {
          alert("Please try again.");
          throw new Error("Failed to Login");
        }
        const responseData = await response.json();
        this.genres = responseData.genres;
        this.moods = responseData.moods;
        this.moods.forEach((element) => {
          this.user_responses[element] = [];
        });
      } catch (error) {
        console.log(error);
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
    async save_preferences() {
      console.log(this.user_data);
      try {
        const response = await fetch(
          "http://10.9.0.6/user/save-user-mood-genres",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: this.user_data.email,
              mapping: this.user_responses,
            }),
          }
        );
        if (!response.ok) {
          alert("Please try again.");
          throw new Error("Failed to Login");
        }
        const responseData = await response.json();

        if (responseData.Status == true) {
          let user_data = JSON.parse(sessionStorage.getItem("user_data"));
          user_data["login_history"] = [true];
          sessionStorage.setItem("user_data", JSON.stringify(user_data));
          await this.$router.go()
        }
        console.log(responseData);
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
</style>