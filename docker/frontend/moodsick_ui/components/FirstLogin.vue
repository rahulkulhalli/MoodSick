<template>
  <div class="container mt-5">
    <button
      type="button"
      class="btn btn-primary"
      data-bs-toggle="modal"
      data-bs-target="#startFlowModal"
    >
      Start New Flow
    </button>
    <MusicPlayer></MusicPlayer>
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
            <h5 class="modal-title" id="modalLabel">How's Your Mood Today?</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <!-- <p>Select your mood:</p> -->
            <div class="mood-selection text-center">
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
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
  <script>
import * as Bootstrap from "bootstrap";

export default {
  mounted() {
    this.$nextTick(() => {
      const modal = new Bootstrap.Modal(
        document.getElementById("startFlowModal")
      );
      modal.show();
    });
  },
  methods: {
    submitMood(mood) {
      // Implement API call here
      console.log(`Mood selected: ${mood}`);
      // Example: axios.post('/api/mood', { mood });
      // Close the modal after submission
      const modal = new Bootstrap.Modal(
        document.getElementById("startFlowModal")
      );
      modal.hide();
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